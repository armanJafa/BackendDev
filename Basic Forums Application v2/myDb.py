import sqlite3
from flask import Flask, request, render_template, g, jsonify,Response

# Connects to the database
def get_db(DATABASE):
  db = getattr(g, '_database', None)
  if db is None:
       db = g._database = sqlite3.connect(DATABASE)
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
  print("*********************\nDATABASE INITALIZED\n*********************")

#connects to DB
def get_connections(DATABASE):
  conn = get_db(DATABASE)
  conn.row_factory = dict_factory
  cur = conn.cursor()
  return cur