from .slots import slots
from .roles import roles
from .commands import commands
from .main import main
from .service import service

rts = [
  *slots,
  *commands,
  *roles,
  *main,
  *service
]
