import sqlite3
from flask import Flask, request, render_template, g, jsonify,Response


# Connects to the database
def get_db(dbName):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(dbName)
    return db

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

###################################
# Testing to see if we need to
# create separate connections
##################################

DATABASE = './data.db'
shard0 = './shard0.db'
shard1 = './shard1.db'
shard2 = './shard2.db'

#Create connection for first shard
def get_db_s0():
    db = getattr(g, '_database_s0', None)
    if db is None:
        db = g._database_s0 = sqlite3.connect(shard0)
    return db

#Create connection for second shard
def get_db_s1():
    db = getattr(g, '_database_s1', None)
    if db is None:
        db = g._database_s1 = sqlite3.connect(shard1)
    return db

#Create connection for third shard
def get_db_s2():
    db = getattr(g, '_database_s2', None)
    if db is None:
        db = g._database_s2 = sqlite3.connect(shard2)
    return db

##Teardown databases
# from app import app

# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()
        
# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database_s0', None)
#     if db is not None:
#         db.close()

# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database_s1', None)
#     if db is not None:
#         db.close()

# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database_s2', None)
#     if db is not None:
#         db.close()