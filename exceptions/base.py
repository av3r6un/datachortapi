from yaml import safe_load
import sys
import os

class Exc(BaseException):
  message = None

  def __init__(self, dep, *args) -> None:
    super().__init__(*args)
    self.dep = dep
    self.case = None
    self.error = None
    self.messages = self._load_messages()

  @staticmethod
  def _load_messages():
    fp = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'config', 'messages.yaml')
    try:
      with open(fp, 'r', encoding='utf-8') as f:
        data = safe_load(f)
      return data
    except FileNotFoundError:
      print('Exception messages file not found!')
      sys.exit(-1)
  
  def make_error(self, case, error, **kwargs):
    self.case = case
    self.error = error
    self.extra = kwargs
    
  @property
  def message(self):
    if not self.case or not self.error: return None
    text = ' '.join(self.extra.get(word, word) for word in self.messages[self.dep][self.case][self.error].split())
    self._message = text
    return text

  @property
  def json(self): 
    return dict(status='error', message=self.message)
  