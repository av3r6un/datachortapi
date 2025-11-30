from aiohttp.web import RouteTableDef, Request, json_response
from datetime import datetime as dt, timedelta as delta
from sqlalchemy.ext.asyncio import AsyncSession
from api.functions import SlotMachine
from api.models import Slot, Symbol


slots = RouteTableDef()
slot_machine = SlotMachine()


@slots.post('/api/slots')
async def add_slot(req: Request, session: AsyncSession):
  data = (await req.json()).get('data', {})
  try:
    symbols = await Symbol.get_multi(session, 'id', data.pop('symbols'))
    suid = await Slot.create_uid(session)
    slot = Slot(suid, **data)
    slot.symbols = symbols
    await session.commit()
    return json_response(dict(status='success', message='Slot successfully created!'))
  except Exception as e:
    return json_response(dict(status='error', message=str(e)), status=400)


@slots.get('/api/slots')
async def get_slots(req: Request, session: AsyncSession):
  try:
    slots = await Slot.get_json(session)
    return json_response(dict(status='success', body=slots))
  except Exception as e:
    print(e)
    return json_response(dict(status='error', message=str(e)), status=400)


@slots.get('/api/slots/{uid}')
async def slot_info(req: Request, session: AsyncSession):
  try:
    uid = req.match_info.get('uid')
    slot = await Slot.first(session, uid=uid)
    if not slot:
      return json_response(dict(status='error', message='Slot not wound!'), status=400)
    return json_response(dict(status='success', body=slot.json))
  except Exception as e:
    print(e)
    return json_response(dict(status='error', message=str(e)))


@slots.post('/api/slots/{uid}')
@slots.delete('/api/slots/{uid}')
async def manage_slot(req: Request, session: AsyncSession):
  action = 'deleted!'
  try:
    uid = req.match_info.get('uid')
    slot = await Slot.first(session, uid=uid)
    if not slot:
      return json_response(dict(status='error', message='Slot not wound!'), status=400)
    if req.method == 'POST':
      data = (await req.json()).get('data', {})
      await slot.edit(session, data)
      action = 'edited!'
    elif req.method == 'DELETE':
      await slot.delete(session)
    else:
      return json_response(dict(status='success', body=slot.json))
    return json_response(dict(status='success', message=f'Slot successfully {action}'))
  except Exception as e:
    return json_response(dict(status='success', message=f'Slot succesfully {action}'))


@slots.get('/api/slots/{name}')
@slots.get('/api/slots/')
async def get_slots(req: Request, session: AsyncSession):
  try:
    if not slot_machine:
      return json_response(dict(status='error', message='Slots Machine is not initialized!'))
    name = req.match_info.get('name', 'default').replace('_', ' ').capitalize()
    result = await slot_machine.spin_slot(session, name)
    print(result)
    return json_response(dict(status='success', body=True))  
  except Exception as e:
    return json_response(dict(status='error', message=str(e)), status=400)
