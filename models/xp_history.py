from sqlalchemy import Enum, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import TINYINT
from .base import Base
import enum


class Source(enum.Enum):
  SPIN = 'spin'
  QUIZ = 'quiz'
  GIVEAWAY = 'giveaway'
  
  
class XPHistory(Base):
  __tablename__ = 'experience_history'
  
  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  uuid: Mapped[str] = mapped_column(String(6), ForeignKey('users.uid'), nullable=False) 
  source: Mapped[Source] = mapped_column(Enum(Source), nullable=False)
  delta: Mapped[int] = mapped_column(TINYINT, nullable=False)
  multiplier: Mapped[str] = mapped_column(String(100), nullable=True)
  
  user: Mapped["GuildUser"] = relationship('GuildUser', back_populates="xp_history") # type: ignore
  
  def __init__(self, uuid, source, delta, multiplier=None, **kwargs):
    self.uuid = uuid
    self.source = Source(source)
    self.delta = delta
    self.multiplier = multiplier
    
  @property
  def json(self):
    return dict(id=self.id, uuid=self.uuid, source=self.source.value, delta=self.delta, multiplier=self.multiplier)
