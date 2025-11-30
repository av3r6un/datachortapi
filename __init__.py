from aiohttp.web import Application, run_app
from .utils import middlewares, JackpotEvents
from config import Settings
import logging


settings = Settings()
events: JackpotEvents = None


async def start_app(app):
  from .utils.engine import create_db
  await create_db()
  global events
  events = JackpotEvents()
  await events.load_rules(app['db_sessionmaker'])
  

def create_app():
  from .utils.engine import session_maker
  from .routes import rts
  app = Application(middlewares=middlewares)
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] WEB: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=settings.LOG_FILE
  )
  app['db_sessionmaker'] = session_maker
  app.on_startup.append(start_app)
  app.add_routes(rts)
  if settings.DEBUG:
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s", "%Y-%m-%d %H:%M:%S"))
    logging.getLogger().addHandler(console)
  return app


def start():
  import os
  run_app(create_app(), host=settings.WEB_HOST, port=settings.WEB_PORT,
          access_log_format='%{X-Forwarded-For}i %s - "%r" (%b | %D) %{User-Agent}i')
