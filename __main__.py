from aiohttp.web import run_app
from . import create_app

if __name__ == '__main__':
  run_app(create_app(), host='0.0.0.0', port=8989, access_log_format='%{X-Forwarded-For}i %s - "%r" (%b | %D) %{User-Agent}i')
