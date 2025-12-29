from aiohttp.web import RouteTableDef, Request, json_response
from sqlalchemy.ext.asyncio import AsyncSession
from api.models import UserWatchDog, GuildUser


service = RouteTableDef()


@service.get('/api/users')
async def get_users(req: Request, session: AsyncSession):
  try:
    users = await GuildUser.get_json(session)
    if 'collect' in req.query.keys():
      if 'watchdog' in req.query.get('collect').split(','):
        watching = await UserWatchDog.get_json(session, active=True)
    return json_response(dict(status='success', body=dict(users=users, watching=watching)))
  except Exception as e:
    print(e)
    return json_response(dict(status='error', message=str(e)))


@service.get('/api/user/{uid}')
async def get_users(req: Request, session: AsyncSession):
  uuid = req.match_info.get('uid')
  try:
    user = await GuildUser.first(session, uid=uuid)
    if not user:
      return json_response(dict(status='error', message='User not found!'), status=404)
    return json_response(dict(status='success', body=user.json))
  except Exception as e:
    print(e)
    return json_response(dict(status='error', message=str(e)))


@service.post('/api/user/{uuid}/watch')
async def manage_watchdog_rule(req: Request, session: AsyncSession):
  uuid = req.match_info.get('uuid')
  try:
    user = await GuildUser.first(session, uid=uuid)
    if not user:
      return json_response(dict(status='error', message='User not found!'), status=404)
    watchdog = await UserWatchDog.first(session, uuid=uuid)
    if watchdog:
      wuid = watchdog.uid
      await watchdog.activate(session)
    else:
      wuid = await UserWatchDog.create_uid(session)
      uwd = UserWatchDog(wuid, user.uid)
      await uwd.save(session)
    return json_response(dict(status='success', body=dict(uid=wuid, uuid=uuid, active=True)))
  except Exception as e:
    print(e)
    return json_response(dict(status='error', message=str(e)))


@service.get('/api/users/watch')
async def get_watchdog_rules(req: Request, session: AsyncSession):
  try:
    uwd = await UserWatchDog.get_json(session, active=True)
    return json_response(dict(status='success', body=uwd))
  except Exception as e:
    print(e)
    return json_response(dict(status='error', message=str(e)))


@service.delete('/api/users/watch/{uid}')
async def delete_watchdog_rule(req: Request, session: AsyncSession):
  uwd_uid = req.match_info.get('uid')
  try:
    uwd = await UserWatchDog.first(session, uid=uwd_uid)
    if not uwd:
      return json_response(dict(status='error', message='Rule not found!'), status=404)
    await uwd.deactivate(session)
    return json_response(dict(status='success', body=True))
  except Exception as e:
    print(e)
    return json_response(dict(status='error', message=str(e)), status=400)
   
   

@service.get('/api/status')
async def get_status(req: Request, session: AsyncSession):
  return json_response(dict(status='success', body=True))
