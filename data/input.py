from datetime import datetime

from pymongo.errors import DuplicateKeyError
from data.models import session, Group, Config, Item


class SelfQuantifierAPI(object):
  def __init__(self):
    self.current_group = self.set_default_group()
    self.date = None

  def set_default_group(self, group=None):
    if not group:
      self.current_group = Config.query.get(name='default_group')
    else:
      new_group = Config.query.get(name=group)
      if new_group:
        self.default_group = Config.query.get(name=group)
    return self.current_group

  def remove_group(self, name):
    group = Group.query.get(name=name)
    if group:
      group.delete()
      session.flush()
      return True
    else:
      return False

  def create_group(self, name):
    try:
      group = Group(name=name, item_order=[])
      session.flush()
    except DuplicateKeyError:
      return False
    return group

  def activate_group(self, name):
    new_group = Group.query.get(name)
    if new_group:
      self.current_group = new_group
      return self.current_group
    else:
      return False

  def deactivate_group(self, name):
    self.set_default_group()
    return True

  def add_item(self, name, group=None, value=None):
    date = self.date or None
    current_group = group if group else self.current_group.name

    # TODO: fuzzy logic search to avoid creating weird new items

    item = Item.query.get(name=name)
    if not item:
      item = Item(name=name, values=[], groups=[])

    if group:
      item.groups.append(group)
      Group.query.get(group).item_order.append(item.name)

    if not date and value:
      date = datetime.now()
    if value:
      item.values.append([date, value])

    session.flush()
    return item

  def delete_item(self, name):
    item = Item.query.get(name=name)
    if item:
      item.delete()
      session.flush()
      return True
    else:
      return False

  def set_group_item_order(self, name, *args):
    group = Group.query.get(name=name)
    if not group:
      return False

    group.item_order = []
    for arg in args:
      group.item_order.append(arg)

      # verify item is also registered with group
      item = Item.query.get(arg)
      if group.name not in item.groups:
        item.groups.append(group.name)

    session.flush
    return True

  def set_date(self, date):
    date_val = None
    for format in ('%m %d %y %I:%M %p', '%m %d %I:%M %p', '%d %I:%M %p', '%I:%M %p'):
      try:
        date_val = datetime.strptime(date, format)
        if format == '%m %d %I:%M %p':
          date_val.replace(year=datetime.now().year)
        if format == '%d %I:%M %p':
          date_val.replace(year=datetime.now().year)
          date_val.replace(month=datetime.now().month)
        if format == '%I:%M %p':
          date_val.replace(year=datetime.now().year)
          date_val.replace(month=datetime.now().month)
          date_val.replace(day=datetime.now().day)
        break
      except:
        pass
    if not date_val:
      return False

    self.date = date_val
    return self.date
