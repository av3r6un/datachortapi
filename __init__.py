from aiohttp.web import Application
from .utils import middlewares, JackpotEvents
from .utils.logger import check_logs_folder
from .config import Settings
import logging
import sys
import os


settings = Settings()
events: JackpotEvents = None


async def start_app(app):
  from .utils.engine import create_db
  try:
    await create_db()
    global events
    events = JackpotEvents()
    await events.load_rules(app['db_sessionmaker'])
  except Exception:
    logging.exception('Failed to start application')
    sys.exit(1)
    
async def on_shutdown(app):
  from .utils.engine import close_db
  await close_db()
  

def create_app():
  from .utils.engine import session_maker
  from .routes import rts
  app = Application(middlewares=middlewares)
  
  log_dir = os.path.dirname(settings.LOG_FILE)
  if log_dir and not os.path.exists(log_dir):
      os.makedirs(log_dir, exist_ok=True)
  
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
  
  
def start_alt():
  from aiohttp.web import run_app
  from dotenv import load_dotenv
  import os
  load_dotenv(os.path.join(settings.ROOT, '..', 'config', '.env'))
  
  run_app(create_app(), host='0.0.0.0', port=8989, access_log_format='%{X-Forwarded-For}i %s - "%r" (%b | %D) %{User-Agent}i')
