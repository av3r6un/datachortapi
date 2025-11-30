from sqlalchemy.ext.asyncio import AsyncSession
from aiohttp.web import Request, json_response
from functools import wraps
from typing import Callable


class Responder:
  
  def __call__(self, handler) -> Callable:
    @wraps(handler)
    async def wrapper(req: Request, session: AsyncSession, *args, **kwargs):
      if req.headers.get('X-Department') and req.query.get('format') == 'discord':
        variables = dict(**req.query)
        variables.pop('format')
        if req.has_body:
          try:
            variables.update((await req.json()).get('data', {}))
          except Exception as e:
            print(e)
        kwargs.update(variables)
        return await handler(req, session, *args, **kwargs)
      return json_response(dict(status='error', message='Not found!'), status=404)
    return wrapper

  def response(self, reply, action=None):
    return dict(status='success', body=dict(reply=str(reply), action=action))
