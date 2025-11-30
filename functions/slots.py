from sqlalchemy.ext.asyncio import AsyncSession
from api.models import Slot, Symbol
from random import choices


class SlotMachine:
  session = None
  
  def __init__(self):
    self.app = None
    
  @staticmethod
  def spin_once(weighted_symbols: list[tuple]):
    symbols, weights = zip(*weighted_symbols)
    return choices(symbols, weights=weights, k=1)[0]
  
  @staticmethod
  def build_weight_table(symbols: list[Symbol]):
    weighted = []
    for s in symbols:
      if not s.enabled:
        continue
      weight = s.chance.weight if s.chance else 0
      if weight > 0:
        weighted.append((s, weight))
    return weighted
  
  @staticmethod
  def _find_args(val: str = None):
    if not val: return None
    return val.split(',')[0] if len(val.split(',')) > 0 else val
  
  def spin_wheel(self, slot: Slot) -> list[Symbol]:
    weighted = self.build_weight_table(slot.symbols)
    if not weighted:
      return []
    result = []
    for _ in range(slot.wheel_size):
      symbol = self.spin_once(weighted)
      result.append(symbol)
    return result
    
  async def spin_slot(self, session: AsyncSession, name: str = None, **kwargs):
    from api import events
    found_name = self._find_args(name)
    name = found_name.replace('_', '').capitalize() if found_name else 'Default'
    slot = await Slot.first(session, name=name)
    if not slot:
      raise ValueError('No such slot')
    result = self.spin_wheel(slot)
    jackpots = events.evalute(result)
    return result, jackpots
    # return dict(symbols=result, jackpots=[{'name': j.name, 'multiplier': j.reward_multiplier} for j in jackpots])

    




