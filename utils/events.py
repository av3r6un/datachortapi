from sqlalchemy.ext.asyncio import AsyncSession
from api.models import Symbol, JackpotRule
from dataclasses import dataclass
from typing import Callable


@dataclass
class JackpotEvent:
  name: str
  condition: Callable[[list], bool]
  reward_multiplier: float


class JackpotEvents:
  EVENTS: list[JackpotEvent] = []
  def __init__(self) -> None:
    pass
   
  @staticmethod
  def triple_match(symbols: list[Symbol]):
    if len(symbols) < 3:
      return False
    return all(s.id == symbols[0].id for s in symbols)
  
  @staticmethod
  def lucky_hit(symbols: list[Symbol]):
    rare_ids = {32}
    return any(s.id in rare_ids for s in symbols)
  
  @staticmethod
  def super_mix(symbols: list[Symbol]):
    special_ids = {5, 6}
    ids = [s.id for s in symbols]
    has_pair = (ids[0] == ids[1]) or (ids[0] == ids[2]) or (ids[1] == ids[2])
    has_special = any(s.id in special_ids for s in symbols)
    return has_pair and has_special
  
  CONDITION_MAP = {
    'triple_match': triple_match.__func__,
    'lucky_hit': lucky_hit.__func__,
    'super_mix': super_mix.__func__,
  }  
  
  async def load_rules(self, sessionmaker):
    self.EVENTS.clear()
    async with sessionmaker() as session:
      rules = await JackpotRule.get(session, active=True)
      for rule in rules:
        cond_fn = self.CONDITION_MAP.get(rule.condition)
        if not cond_fn:
          continue
        self.EVENTS.append(JackpotEvent(name=rule.name, condition=cond_fn, reward_multiplier=rule.multiplier))

  @staticmethod
  def evalute(symbols: list[Symbol]):
    triggered = []
    for event in JackpotEvents.EVENTS:
      if event.condition(symbols):
        triggered.append(event)
    return triggered
