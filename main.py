import cmd

from controller.constants import Err
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

  date 3 23 15 1:34 PM
  date 3 23 1:34 PM (assumes current year)
  date 23 1:34 PM (assumes current month)
  date 1:34 PM (assumes current day)

  list items
  list groups

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
    if current_group.name != 'default_group':
      self.prompt = 'sq ({}): '.format(current_group.name)

  @staticmethod
  def do_greet(line):
    print('hello')

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
  def do_remove(self, args):
    group = args[0]
    self.input.remove_group(group)

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
      print('--- Added ', name, ' with: ', ', '.join(values))
    else:
      self.input.add_item(name)

  @parseargs(2, -1)
  def do_link(self, args):
    name, groups = args[0], args[1:]
    self.input.link_item(name, *groups)

  @parseargs(1)
  def do_list(self, args):
    list_target = args[0]
    if 'items' in list_target:
      print('--- Items:')
      print('\n'.join(['  ' + i for i in self.input.show_all_items()]))
    if 'groups' in list_target:
      print('--- Groups:')
      print('\n'.join(['  ' + i for i in self.input.show_all_groups()]))


  def parseline(self, line):
    ret = cmd.Cmd.parseline(self, line)
    command = ret[0]
    if command and not getattr(self, 'do_' + command):
      ret = ('add', command + ' ' + ret[1], command + ' ' + ret[2])
    # print(ret)
    return ret




if __name__ == '__main__':
  s = SelfQuantifierCLI()
  s.cmdloop()


