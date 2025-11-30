from aiohttp.web import RouteTableDef, Request, json_response
from sqlalchemy.ext.asyncio import AsyncSession
from api.functions import SlotMachine, Responder
from api.models import GuildUser, XPHistory
from functools import reduce
from operator import mul


main = RouteTableDef()
resp = Responder()


@main.get('/spin')
@resp
async def spin_slots(req: Request, session: AsyncSession, **kwargs):
  from api import settings
  try:
    sm = SlotMachine()
    spin_result, jackpots = await sm.spin_slot(session, name=kwargs.get('args'))
    message = ''
    for s in spin_result:
      message += f"{chr(int(s.emoji.replace('U+', ''), 16))} "
    total_multiplier = reduce(mul, (j.reward_multiplier for j in jackpots), 1)
    
    user = await GuildUser.first(session, id=kwargs.get('author'))
    if not user:
      return json_response(dict(status='error', message='Author is not found! Maybe he has not been registered!'))
    
    history = XPHistory(user.uid, 'spin', settings.XP_BIAS * total_multiplier, ','.join(j.name for j in jackpots))
    await history.save(session)
    
    await user.buff(session, settings.XP_BIAS*total_multiplier)
    return json_response(resp.response(reply=message.strip()))
  except Exception as e:
    print(e)
    return json_response(dict(status='error', message=str(e)), status=400)


@main.get('/experience')
@resp
async def discover_xp(req: Request, session: AsyncSession, **kwargs):
  from api import settings
  try:
    user = await GuildUser.first(session, id=kwargs.get('author'))
    if not user:
      return json_response(dict(status='error', message='Author is not found! Maybe he has not been registered!'))
    message = f':glowing_star: {user.xp_total} pts\n:medal:{max(int((user.xp_total / 100) ** settings.LEVEL_BIAS), 1)} level'
    return json_response(resp.response(reply=message.strip()))
  except Exception as e:
    print(e)
    return json_response(dict(status='error', message=str(e)), status=400)
  
