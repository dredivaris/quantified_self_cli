import cmd
from ming import create_datastore
from controller.controller import SelfQuantifierController

doc = """
  Example of basic data entries:
  (date is automatically recorded as now if not specified with a date command)

  create group mygroup
  remove group mygroup

  activate groupname
  act groupname
  add weight (after toggle of group that group is active, adding stuff will add to that group)
  add height
  deactivate groupname
  dea groupname

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

  h     (help documentation)
  help  (help documentation)

  quit
  exit (quit the app)

"""


class SelfQuantifierCLI(cmd.Cmd):
  """Simple command processor example."""
  prompt = 'sq: '

  def __init__(self):
    # self.ctrl = SelfQuantifierController()
    super(SelfQuantifierCLI, self).__init__()

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

  @staticmethod
  def do_create(line):
    print(line)
    return True

    # def main():
    #   pp = pprint.PrettyPrinter(indent=4)
    #   p = optparse.OptionParser()
    # p.add_option('--multfile', '-m', default="")
    # p.add_option('--num_to_print', '-n', default=-1)
    # options, arguments = p.parse_args()
    # print 'Hello %s' % options.person

if __name__ == '__main__':
  s = SelfQuantifierCLI()
  s.cmdloop()


