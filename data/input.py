from datetime import datetime, timedelta

from pymongo.errors import DuplicateKeyError

from controller.decorators import store_last_action
from data.models import session, Group, Config, Item


class SelfQuantifierAPI(object):
  def __init__(self):
    self.current_group = self.set_default_group()
    self.date = None

  def set_default_group(self, group=None):
    if not group:
      self.current_group = Config.query.get(name='default_group')
    else:
      new_group = Config.query.get(name='default_group')
      if not new_group:
        new_group = Config(name='default_group')
      new_group.value = group

      if new_group:
        self.current_group = new_group
        session.flush()
    return self.current_group

  def exists_item(self, name):
    return True if Item.query.get(name) else False

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

  @store_last_action()
  def add_item(self, name, *values):
    date = self.date or None
    # TODO: fuzzy logic search to avoid creating weird new items

    item = Item.query.get(name=name)
    if not item:
      item = Item(name=name, values=[], groups=[])

    if not date:
      date = datetime.now()

    if values:
      for arg in values:
        print('  adding ', arg, ' to ', item.name)
        item.values.append({'timestamp': date, 'value': arg})

    session.flush()
    return item

  @store_last_action()
  def add_items(self, items_values):
    for item, value in items_values:
      if item and value and value != '_':
        self.add_item(item, value)

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
    for format_val in ('%m %d', '%m %d %y', '%m %d %Y', '%m %d %y %I:%M %p', '%m %d %I:%M %p',
                   '%d %I:%M %p', '%I:%M %p'):
      try:
        date_val = datetime.strptime(date, format_val)
        if format_val == '%m %d':
          date_val = date_val.replace(year=datetime.now().year)
        if format_val == '%m %d %I:%M %p':
          date_val = date_val.replace(year=datetime.now().year)
        if format_val == '%d %I:%M %p':
          date_val = date_val.replace(month=datetime.now().month, year=datetime.now().year)
        if format_val == '%I:%M %p':
          date_val = date_val.replace(
              day=datetime.now().day,
              month=datetime.now().month,
              year=datetime.now().year)
        break
      except:
        pass
    if not date_val:
      return False

    self.date = date_val
    print('set date', self.date)
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

  def show_all_item_values(self, name):
    item = Item.query.get(name=name)
    print(item)
    return item.values

  # TODO: why doesnt this work?
  def remove_value_on_day(self, name, date):
    next_day = date + timedelta(days=1)
    print('between', date, next_day)
    resp = Item.query.update(
        {'name': name},
        {'$pull': {'values': {'elemMatch': {'timestamp': {'$gte': date, '$lte': next_day}}}}},
        multi=True
    )
    print(resp)
    session.flush()

  def remove_last_addition(self):
    if hasattr(self, 'last_action') and self.last_action:
      print(self.last_action['func'])
      if self.last_action['func'].__name__ == self.add_items.__name__:
        items_values = self.last_action['args'][0]
        for name, value in items_values:
          item = Item.query.get(name=name)
          item.values.pop()
      if self.last_action['func'].__name__ == self.add_item.__name__:
        name, values = self.last_action['args'][0], self.last_action['args'][1:]
        print(name, values)
        item = Item.query.get(name=name)
        for val in values:
          item.values.pop()
      session.flush()
