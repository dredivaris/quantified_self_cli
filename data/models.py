from ming import create_datastore
from ming.odm import ThreadLocalODMSession
from ming import schema
from ming.odm import MappedClass
from ming.odm import FieldProperty

session = ThreadLocalODMSession(bind=create_datastore('quantifier'))


class Group(MappedClass):
  class __mongometa__:
    session = session
    name = 'groups'
    # indexes = ['author.name', 'comments.author.name']

  _id = FieldProperty(schema.ObjectId)
  name = FieldProperty(schema.String, unique=True)
  item_order = FieldProperty([schema.String])


class Item(MappedClass):
  class __mongometa__:
    session = session
    name = 'items'

  _id = FieldProperty(schema.ObjectId)
  name = FieldProperty(schema.String, unique=True)
  values = FieldProperty([])
  groups = FieldProperty([schema.String])


class Config(MappedClass):
  class __mongometa__:
    session = session
    name = 'configs'

  _id = FieldProperty(schema.ObjectId)
  name = FieldProperty(schema.String)
  value = FieldProperty(schema.String)
