from sqlalchemy import Table, String, Integer, BigInteger, Boolean, ForeignKey, Float, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Role(Base):
  __tablename__ = 'roles'
  
  uid: Mapped[str] = mapped_column(String(10), primary_key=True)
  name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
  color: Mapped[str] = mapped_column(String(6), nullable=False, default='8d50a6')
  permissions: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  reason: Mapped[int] = mapped_column(String(150), nullable=True)

  def __init__(self, uid, name, color, permissions, reason=None, **kwargs) -> None:
    self.uid = uid
    self.name = name
    self.color = self._validate_color(color)
    self.permissions = permissions
    self.reason = reason
    
  @staticmethod
  def _validate_color(color: str):
    if isinstance(color, str) and len(color) > 6:
      if color.startswith('#'): return color[1:]
    if isinstance(color, tuple) or isinstance(color, list):
      if len(color) == 3 and all(v > 0 for v in color):
        return '%02x%02x%02x' % (color)
    else: return color
    
    
  @property
  def json(self):
    return dict(uid=self.uid, name=self.name, color=self.color, permissions=self.permissions, reason=self.reason)
