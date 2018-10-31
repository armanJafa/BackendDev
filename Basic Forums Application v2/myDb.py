import sqlite3
import uuid
from flask import Flask, request, render_template, g, jsonify,Response


#########################################
# Generate GUID for posts
#########################################

sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: buffer(u.bytes_le))

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

#initializes the data base using flask
def init_db(database, file_initializer,app):
  with app.app_context():
      db = get_db(database)
      with app.open_resource(str(file_initializer), mode='r') as f:
          db.cursor().executescript(f.read())
      db.commit()
      db.close()

#connects to DB
def get_connections(DATABASE):
  conn = get_db(DATABASE)
  conn.row_factory = dict_factory
  cur = conn.cursor()
  return cur

DATABASE = './data.db'
shard0 = './shard0.db'
shard1 = './shard1.db'
shard2 = './shard2.db'

# Connects to the database
def get_db(dbName):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(dbName, detect_types=sqlite3.PARSE_DECLTYPES)
    return db

#Create connection for first shard
def get_db_s0():
    db = getattr(g, '_database_s0', None)
    if db is None:
        db = g._database_s0 = sqlite3.connect(shard0, detect_types=sqlite3.PARSE_DECLTYPES)
    return db

#Create connection for second shard
def get_db_s1():
    db = getattr(g, '_database_s1', None)
    if db is None:
        db = g._database_s1 = sqlite3.connect(shard1, detect_types=sqlite3.PARSE_DECLTYPES)
    return db

#Create connection for third shard
def get_db_s2():
    db = getattr(g, '_database_s2', None)
    if db is None:
        db = g._database_s2 = sqlite3.connect(shard2, detect_types=sqlite3.PARSE_DECLTYPES)
    return db

def teardown_db(database):
    db = g.pop(database, None)
    if db is not None:
        db.close()