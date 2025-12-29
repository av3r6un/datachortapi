from sqlalchemy import Table, String, Integer, BigInteger, Boolean, ForeignKey, Float, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


slot_symbols = Table(
  'slot_symbols',
  Base.metadata,
  Column('slot_uid', String(7), ForeignKey('slots.uid'), primary_key=True),
  Column('symbol_id', Integer, ForeignKey('symbols.id'), primary_key=True)
)


class Symbol(Base):
  __tablename__ = 'symbols'
  
  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  name: Mapped[str] = mapped_column(String(25), nullable=False, unique=True)
  emoji: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
  discord_emoji: Mapped[int] = mapped_column(BigInteger, nullable=True)
  enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
  
  chance: Mapped["ProbabilityRule"] = relationship("ProbabilityRule", back_populates="symbol", uselist=False, cascade="all, delete-orphan", lazy="selectin")
  slots: Mapped[list["Slot"]] = relationship("Slot", secondary=slot_symbols, back_populates="symbols")
  
  def __init__(self, name, emoji, discord_emoji, **kwargs) -> None:
    self.name = name
    self.emoji = emoji
    self.discord_emoji = discord_emoji
    
  @property
  def json(self):
    return dict(id=self.id, name=self.name, chance=self.chance.weight, emoji=self.emoji, discord_emoji=self.discord_emoji, enabled=self.enabled)


class ProbabilityRule(Base):
  __tablename__ = 'probability_rules'
  
  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  symbol_id: Mapped[int] = mapped_column(Integer, ForeignKey('symbols.id'), nullable=False)
  weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
  
  symbol: Mapped["Symbol"] = relationship("Symbol", back_populates="chance")
  
  def __init__(self, symbol_id, weight, **kwargs) -> None:
    self.symbol_id = symbol_id
    self.weight = weight
  
  @property
  def json(self):
    return dict(emoji_id=self.symbol_id, weight=self.weight)


class Slot(Base):
  __tablename__ = 'slots'
  
  uid: Mapped[str] = mapped_column(String(7), primary_key=True)
  name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
  wheel_size: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
  prize: Mapped[str] = mapped_column(String(50), nullable=True)

  symbols: Mapped[list["Symbol"]] = relationship("Symbol", secondary=slot_symbols, back_populates="slots")

  def __init__(self, uid, name, wheel_size=None, prize=None, **kwargs) -> None:
    self.uid = uid
    self.name = name
    self.wheel_size = wheel_size
    self.prize = prize
  
  @property
  def json(self):
    return dict(uid=self.uid, name=self.name, wheel_size=self.wheel_size, prize=self.prize, symbols=[s.json for s in self.symbols])


class JackpotRule(Base):
  __tablename__ = 'jackpot_rules'
  
  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  name: Mapped[str] = mapped_column(String(50), nullable=False)
  condition: Mapped[str] = mapped_column(String(50), nullable=False)
  multiplier: Mapped[float] = mapped_column(Float, nullable=False)
  active: Mapped[bool] = mapped_column(Boolean, default=True)

  def __init__(self, name, condition, multplier) -> None:
    self.name = name
    self.condition = condition
    self.multiplier = multplier

  @property
  def json(self):
    return dict(id=self.id, name=self.name, condition=self.condition, multiplier=self.multiplier)
