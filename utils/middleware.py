from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from aiohttp.web import Request, middleware, json_response
import os

@middleware
async def query_mw(req: Request, handler):
  if req.query:
    req.query_dict = {k: req.query.getall(k) for k in req.query}
  return await handler(req)

@middleware
async def db_middleware(request: Request, handler):
  session_factory: async_sessionmaker[AsyncSession] = request.app['db_sessionmaker']
  async with session_factory() as session:
    try:
      request['session'] = session
      response = await handler(request, session)
      await session.commit()
      return response
    except Exception as e:
      print(e) 
      await session.rollback()
      raise

# @middleware
# async def jwt_middleware(req: Request, handler, *args):
#   if req.remote in ('127.0.0.1', '::1'):
#     return await handler(req, req['session'])
  
#   req['remote_lang'] = req.headers.get('X-Language')
  
#   if getattr(handler, 'public', False) or req.path in ['/auth/', '/auth/register']:
#     return await handler(req, req['session'])

#   auth_header = req.headers.get('Authorization', '')
#   if not auth_header.startswith('Bearer '):
#     return json_response(data=dict(status='error', message='Missing or invalid Auhtorization Header'), status=401)

#   token = auth_header.split(' ')[1]
#   from api.models import Admin
  
#   try:
#     payload = decode_token(token)
#     session = req['session']
#     req['current_user'] = await Admin.first(session, uid=payload['uid'])
#   except (ExpiredSignatureError, InvalidTokenError):
#     return json_response(data=dict(status='error', message='Invalid or expired token'), status=401)
  
#   try:
#     return await handler(req, session)
#   except TypeError:
#     return await handler(req)
  
middlewares = [query_mw, db_middleware]
