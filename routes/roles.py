from aiohttp.web import RouteTableDef, Request, json_response
from datetime import datetime as dt, timedelta as delta
from sqlalchemy.ext.asyncio import AsyncSession
from api.models import Role


roles = RouteTableDef()


@roles.post('/api/roles')
async def add_role(req: Request, session: AsyncSession):
  data = (await req.json()).get('data', {})
  try:
    ruid = await Role.create_uid(session)
    role = Role(ruid, **data)
    await role.save(session)
    return json_response(dict(status='success', message='Role successfully created!'))
  except Exception as e:
    print(e)
    return json_response(dict(status='error', message=str(e)), status=400)


@roles.get('/api/roles')
async def get_roles(req: Request, session: AsyncSession):
  try:
    roles = await Role.get_json(session)
    return json_response(dict(status='success', body=roles))
  except Exception as e:
    print(e)
    return json_response(dict(status='error', message=str(e)), status=400)


@roles.post('/api/roles/{uid}')
@roles.delete('/api/roles/{uid}')
async def manage_role(req: Request, session: AsyncSession):
  action = 'deleted!'
  uid = req.match_info.get('uid')
  try:
    role = await Role.first(session, uid=uid)
    if not role:
      return json_response(dict(status='error', message='Role not found!'), status=404)
    if req.method == 'POST':
      action = 'edited!'
      data = (await req.json()).get('data', {})
      await role.edit(session, **data)
    elif req.method == 'DELETE':
      await role.delete(session)
    return json_response(dict(status='success', message=f'Role successfully {action}'))
  except Exception as e:
    return json_response(dict(status='error', message=str(e)), status=400)


@roles.get('/api/roles/permissions')
async def get_permissions(req: Request, session: AsyncSession):
  from api import settings
  try:
    return json_response(dict(status='success', body=settings.PERMISSIONS))
  except Exception as e:
    return json_response(dict(status='error', message=str(e)), status=400)
