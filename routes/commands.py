from aiohttp.web import RouteTableDef, Request, json_response
from datetime import datetime as dt, timedelta as delta
from sqlalchemy.ext.asyncio import AsyncSession
from api.models.commands import Method
from api.models import Command


commands = RouteTableDef()


@commands.post('/api/commands')
async def add_command(req: Request, session: AsyncSession):
  data = (await req.json()).get('data', {})
  try:
    cuid = await Command.create_uid(session)
    command = Command(cuid, **data)
    await command.save(session)
    return json_response(dict(status='success', message='Command successfully created!'))
  except Exception as e:
    print(e)
    return json_response(dict(status='error', message=str(e)), status=400)


@commands.get('/api/commands')
async def get_commands(req: Request, session: AsyncSession):
  try:
    commands = await Command.get_json(session)
    return json_response(dict(status='success', body=commands))
  except Exception as e:
    print(e)
    return json_response(dict(status='error', message=str(e)), status=400)


@commands.options('/api/commands')
async def get_models(req: Request, session: AsyncSession):
  methods = [item.value for item in Method]
  return json_response(dict(status='success', body=dict(methods=methods)))


@commands.post('/api/commands/{uid}')
@commands.delete('/api/commands/{uid}')
async def manage_command(req: Request, session: AsyncSession):
  action = 'deleted!'
  uid = req.match_info.get('uid')
  try:
    command = await Command.first(session, uid=uid)
    if not command:
      return json_response(dict(status='error', message='Command not found!'), status=404)
    if req.method == 'POST':
      action = 'edited!'
      data = (await req.json()).get('data', {})
      await command.edit(session, **data)
    elif req.method == 'DELETE':
      await command.delete(session)
    return json_response(dict(status='success', message=f'Command successfully {action}'))
  except Exception as e:
    print(e)
    return json_response(dict(status='error', message=str(e)), status=400)

