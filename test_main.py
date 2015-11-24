import pytest


# setup database
f = open('database.py', 'w')
f.write("datastore = 'test_database'")
f.close()

from main import *
from data.models import *

# Fixtures
@pytest.fixture(scope='module')
def cli(request):
  s = SelfQuantifierCLI()

  def fin():
    Group.query.remove({})
    Item.query.remove({})
    f = open('database.py', 'w')
    f.write("datastore = 'quantifier'")
    f.close()

  request.addfinalizer(fin)
  return s


def test_creation_and_removal_of_group(capsys, cli):
  # create test group and verify it shows up in the list of groups
  cli.do_create('test_group')
  cli.do_list('groups')
  out, err = capsys.readouterr()
  assert 'test_group' in out

  # remove the test group and verify it no longer appears in the list of groups
  cli.do_remove('group test_group')
  out, err = capsys.readouterr()
  assert 'test_group' not in out


def test_creation_and_removal_of_grouped_items_with_individual_adds(capsys, cli):
  # create test group and verify it shows up in the list of groups
  cli.do_create('test_group')
  cli.do_list('groups')
  out, err = capsys.readouterr()
  assert 'test_group' in out

  # verify nonexistant group will fail
  cli.do_activate('fake_group')
  out, err = capsys.readouterr()
  assert 'Group not found' in out

  # verify group activates
  cli.do_activate('test_group')
  out, err = capsys.readouterr()
  assert 'Group activated' in out

  cli.do_current('')
  out, err = capsys.readouterr()
  assert 'test_group' in out

  cli.do_add('item1')
  cli.do_add('item2')
  cli.do_add('item3')
  cli.do_add('item4')
  cli.do_add('item5')

  cli.do_list('items')
  out, err = capsys.readouterr()
  assert 'item1' in out
  assert 'item2' in out
  assert 'item3' in out
  assert 'item4' in out
  assert 'item5' in out

  cli.do_link('item1 test_group')
  cli.do_link('item2 test_group')
  cli.do_link('item3 test_group')
  cli.do_link('item4 test_group')
  cli.do_link('item5 test_group')

  cli.do_list('test_group items')
  out, err = capsys.readouterr()

  assert 'item1' in out
  assert 'item2' in out
  assert 'item3' in out
  assert 'item4' in out
  assert 'item5' in out

  cli.do_list('item1 groups')
  out, err = capsys.readouterr()
  assert 'test_group' in out

  cli.do_list('item2 groups')
  out, err = capsys.readouterr()
  assert 'test_group' in out

  cli.do_list('item3 groups')
  out, err = capsys.readouterr()
  assert 'test_group' in out

  cli.do_list('item4 groups')
  out, err = capsys.readouterr()
  assert 'test_group' in out

  cli.do_list('item5 groups')
  out, err = capsys.readouterr()
  assert 'test_group' in out


  cli.do_seq_add('23.4 23.1 44 828932 2387492374.23273924')
  cli.do_seq_add('23.4 23.1 44 828932 2387492374.23273924')
  cli.do_seq_add('23.4 23.1 44 828932 2387492374.23273924')

  for i in range(5):
    cli.do_countvalues('item' + str(i + 1))
    out, err = capsys.readouterr()
    assert str(3) in out

  # remove the test group and verify it no longer appears in the list of groups
  cli.do_remove('group test_group')
  out, err = capsys.readouterr()
  assert 'test_group' not in out

  # verify once group is gone, none of the items have a group reference
  cli.do_list('item1 groups')
  out, err = capsys.readouterr()
  assert 'test_group' not in out

  cli.do_list('item2 groups')
  out, err = capsys.readouterr()
  assert 'test_group' not in out

  cli.do_list('item3 groups')
  out, err = capsys.readouterr()
  assert 'test_group' not in out

  cli.do_list('item4 groups')
  out, err = capsys.readouterr()
  assert 'test_group' not in out

  cli.do_list('item5 groups')
  out, err = capsys.readouterr()
  assert 'test_group' not in out

  cli.do_remove('item item1')
  cli.do_remove('item item2')
  cli.do_remove('item item3')
  cli.do_remove('item item4')
  cli.do_remove('item item5')
  cli.do_list('items')
  out, err = capsys.readouterr()
  assert 'item1' not in out
  assert 'item2' not in out
  assert 'item3' not in out
  assert 'item4' not in out
  assert 'item5' not in out
