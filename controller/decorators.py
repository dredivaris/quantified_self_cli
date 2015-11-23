from functools import wraps
from controller.constants import Err


def parseargs(length, end_length=None):
  def _dec(func):
    @wraps(func)
    def _parse(self, line):
      args = line.split(' ')
      if end_length is None:
        if len(args) == 1 and not args[0] and length != 0:
          print(Err.no_arguments_provided)
          return
        elif len(args) > length:
          print(Err.too_many_args)
          return
        elif len(args) < length:
          print(Err.too_few_args)
          return
      else:
        if len(args) == 1 and not args[0] and length != 0 and end_length != 0:
          print(Err.no_arguments_provided)
          return
        elif end_length != -1 and len(args) > end_length:
          print(Err.too_many_args)
          return
        elif len(args) < length:
          print(Err.too_few_args)
          return
      return func(self, args)
    return _parse
  return _dec


def store_last_action():
  def _dec(func):
    @wraps(func)
    def _last_action(self, *args, **kwargs):
      self.last_action = {
        'func': func,
        'args': args,
        'kwargs': kwargs}
      # print('in store last action wrapper', self.last_action)
      return func(self, *args, **kwargs)
    return _last_action
  return _dec
