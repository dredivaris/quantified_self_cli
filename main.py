import cmd
from datetime import datetime

from controller.constants import Err, date_display
from controller.decorators import parseargs
from data.input import SelfQuantifierAPI

doc = """
  Example of basic data entries:
  (date is automatically recorded as now if not specified with a date command)

  create mygroup
  remove mygroup

  activate groupname
  act groupname
  add weight (after toggle of group that group is active, adding stuff will add to that group)
  add height 23.4 23 (add height item if doesnt exist and add value(s) to height)
  link height group1 group2

  deactivate
  dea (deactivate current group - resets to default)

  width 23.2 (prompt if doesnt exist or not sufficiently close to existing)

  add weight statistics (add weight item to statistics group)

  grouporder workout reps sets weight (specify both what items in group and order to enter them)
  activate workout
  23.4 23.3 80 (once activated stuff can be added to the group automatically in order)

  setglobal workout (sets group as the global default - automatically activated when launched)

  date 3 23
  date 3 23 16
  date 3 23 15 1:34 PM
  date 3 23 1:34 PM (assumes current year)
  date 23 1:34 PM (assumes current month)
  date 1:34 PM (assumes current day)

  list items
  list groups

  show itemname (show all values for item)

  remove item itemname
  remove group groupname

  h     (help documentation)
  help  (help documentation)

  quit
  exit (quit the app)

"""


class SelfQuantifierCLI(cmd.Cmd):
  """Simple command processor example."""
  prompt = 'sq: '
  input = SelfQuantifierAPI()

  def __init__(self):
    self.set_prompt(self.input.current_group)
    super(SelfQuantifierCLI, self).__init__()

  def set_prompt(self, current_group):
    self.prompt = 'sq ({}): '.format(current_group)

  def do_quit(self, line):
    return self.do_EOF(line)

  def do_exit(self, line):
    return self.do_EOF(line)

  @staticmethod
  def do_EOF(line):
    return True

  @parseargs(1)
  def do_create(self, args):
    group = args[0]
    try:
      created = self.input.create_group(group)
    except Exception as e:
      print(e)

  @parseargs(1)
  def do_activate(self, args):
    group = args[0]

    if self.input.activate_group(group):
      print('--- Group activated')
    else:
      print('--- Group not found')
    self.set_prompt(self.input.current_group)

  def do_act(self, line):
    return self.do_activate(line)

  @parseargs(0)
  def do_current(self, args):
    print(self.input.current_group)

  @parseargs(0)
  def do_deactivate(self, args):
    self.input.deactivate_group()
    self.set_prompt(self.input.current_group)

  def do_dea(self, line):
    return self.do_deactivate(line)

  @parseargs(1, -1)
  def do_add(self, args):
    name, values = args[0], args[1:]
    if values:
      self.input.add_item(name, *values)
      print('--- Added', name, 'with: ', ', '.join(values))
    else:
      self.input.add_item(name)
      print('--- Added', name)

  @parseargs(2, -1)
  def do_link(self, args):
    name, groups = args[0], args[1:]
    self.input.link_item(name, *groups)

  @parseargs(1, 2)
  def do_list(self, args):
    list_target = args[0]
    if 'items' in list_target:
      print('--- Items:')
      print('\n'.join(['  ' + i for i in self.input.show_all_items()]))
    elif 'groups' in list_target:
      print('--- Groups:')
      print('\n'.join(['  ' + i for i in self.input.show_all_groups()]))
    elif 'items' in args[1]:
      print('--- Group items:')
      print('\n'.join(['  ' + i for i in self.input.show_all_group_items(list_target)]))
    elif 'groups' in args[1]:
      print('--- Item groups:')
      print('\n'.join(['  ' + i for i in self.input.show_all_item_groups(list_target)]))

  @parseargs(2)
  def do_remove(self, args):
    type = args[0]
    if type == 'item':
      self.input.remove_item(args[1])
    elif type == 'group':
      self.input.remove_group(args[1])

  @parseargs(1, -1)
  def do_seq_add(self, values):
    items = self.input.show_all_group_items(self.input.current_group)
    if len(values) > len(items):
      print(Err.num_value_mismatch)
    self.input.add_items(list(zip(items, values)))

  def do_date(self, line):
    if line:
      self.input.set_date(line)
      print(self.input.date.strftime(date_display))
    elif self.input.date:
      print(self.input.date.strftime(date_display))
    else:
      print(datetime.now().strftime(date_display))

  @parseargs(1)
  def do_setglobal(self, args):
    self.input.set_default_group(group=args[0])

  @parseargs(1)
  def do_show(self, args):
    item = args[0]
    values = self.input.show_all_item_values(item)
    for val in values:
      date = val['timestamp']
      value = val['value']
      print('  ' + value + '  --  ' + date.strftime(date_display))

  @parseargs(2, -1)
  def do_linkgroup(self, args):
    group = args[0]
    items = args[1:]
    for item in items:
      if not self.input.exists_item(item):
        self.input.add_item(item)
      self.input.link_item(item, *[group])

  def do_undo(self, args):
    self.input.remove_last_addition()

  def parseline(self, line):
    ret = cmd.Cmd.parseline(self, line)
    command = ret[0]
    if command and not getattr(self, 'do_' + command, None):
      # if the first word is an item, we are adding values to an item
      if command in self.input.show_all_items():
        ret = ('add', command + ' ' + ret[1], command + ' ' + ret[2])
      # otherwise, we are sequentially adding values to group items
      else:
        ret = ('seq_add', ret[2], ret[2])
    return ret

  @parseargs(1)
  def do_undolast(self, args):
    # TODO
    pass

  @parseargs(1)
  def do_countvalues(self, args):
    print(self.input.count_item_values(args[0]))


  def emptyline(self):
    return

if __name__ == '__main__':
  s = SelfQuantifierCLI()
  s.cmdloop()




