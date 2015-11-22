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
        self.current_group = Config.query.get(name=group)
    return self.current_group

  def remove_group(self, name):
    session.clear()
    group = Group.query.get(name=name)
    if not group:
      return
    if group:
      Item.query.update(
          {'groups': {'$elemMatch': {'$in': [group.name]}}},
          {'$pull': {'groups': {'$in': [group.name]}}}, multi=True)
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
      raise Exception('--- That group already exists')
    return group

  def activate_group(self, name):
    new_group = Group.query.get(name=name)
    if new_group:
      self.current_group = new_group
      return self.current_group
    else:
      return False

  def deactivate_group(self):
    self.set_default_group()
    return True

  def add_item(self, name, *values):
    date = self.date or None
    # TODO: fuzzy logic search to avoid creating weird new items

    item = Item.query.get(name=name)
    if not item:
      item = Item(name=name, values=[], groups=[])

    if not date:
      date = datetime.now()

    if values:
      print (values)
      for arg in values:
        item.values.append([date, arg])

    session.flush()
    return item

  def remove_item(self, name):
    item = Item.query.get(name=name)
    if item:
      Group.query.update(
          {'item_order': {'$elemMatch': {'$in': [item.name]}}},
          {'$pull': {'item_order': {'$in': [item.name]}}}, multi=True)
      item.delete()
      session.flush()
      return True
    else:
      return False

  def link_item(self, name, *args):
    item = Item.query.get(name=name)
    if not item:
      item = Item(name=name, values=[], groups=[])

    if args:
      for arg in args:
        group = Group.query.get(name=arg)
        if not group:
          Group(name=arg, item_order=[item.name])
        else:
          group.item_order.append(item.name)
        item.groups.append(arg)

    session.flush()
    return item.groups

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

    session.flush()
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

  def show_all_items(self):
    session.clear()
    items = Item.query.find({}).all()
    return [i.name for i in items]

  def show_all_groups(self):
    session.clear()
    groups = Group.query.find({}).all()
    return [i.name for i in groups]

  def show_all_group_items(self, name):
    session.clear()
    group = Group.query.get(name=name)
    if not group:
      return ''
    else:
      return group.item_order

  def show_all_item_groups(self, name):
    session.clear()
    item = Item.query.get(name=name)
    if not item:
      return ''
    else:
      return item.groups



