from flask import Flask, request, render_template, g, jsonify,Response
from flask_basicauth import BasicAuth
from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import json
import sqlite3
import time, datetime
import uuid

KEYSPACE = 'forum'

def init_cassandra():
  cluster = Cluster(['172.17.0.2'])
  session = cluster.connect()

  rows = session.execute("SELECT * from system_schema.keyspaces")
  if KEYSPACE in [row[0] for row in rows]:
      session.execute("DROP KEYSPACE " + KEYSPACE)

  session.execute("""CREATE KEYSPACE IF NOT EXISTS %s
                     WITH replication =
                     {'class': 'SimpleStrategy', 'replication_factor': '3'}"""
                     % KEYSPACE)

  session.set_keyspace(KEYSPACE)

  session.execute("""DROP TABLE IF EXISTS forums""")
  session.execute("""DROP TABLE IF EXISTS threads""")
  session.execute("""DROP TABLE IF EXISTS auth_users""")
  session.execute("""DROP TABLE IF EXISTS posts""")

  session.execute("""CREATE TABLE forums (
                  	id int,
                  	name text,
                  	creator text,
                  	PRIMARY KEY (id)
                  )""")

  session.execute("""CREATE TABLE threads (
                    id UUID,
                  	thread_id int,
                  	forum_id int,
                  	title text,
                  	creator text,
                  	time_created text,
                    PRIMARY KEY (id)
                  )""")

  session.execute("""CREATE TABLE posts (
                    id UUID,
                    forum_id int,
                    thread_id int,
                    body text,
                    creator text,
                    created text,
                    PRIMARY KEY((forum_id, thread_id), id)
                  )""")

  session.execute("""CREATE TABLE auth_users (
                  	username text,
                  	password text,
                  	PRIMARY KEY(username)
                  )""")
  #
  session.execute("CREATE INDEX forum_number ON threads (forum_id)")
  # session.execute("CREATE INDEX forum_id ON posts (forum_id)")
  # session.execute("CREATE INDEX thread_id ON posts (thread_id)")
  query = SimpleStatement("INSERT INTO auth_users (username, password) VALUES(%s, %s)")
  session.execute(query, ("alice", "Gr3atPA$$W0Rd"))
  session.execute(query, ("bob", "Gr3atPA$$W0Rd"))
  session.execute(query, ("charlie", "Gr3atPA$$W0Rd"))

  query = SimpleStatement("INSERT INTO forums(id, name, creator) VALUES(%s, %s, %s)")

  session.execute(query, (1, "redis", "alice"))
  session.execute(query, (2, "mongodb", "bob"))

  query = SimpleStatement("INSERT INTO threads(id, thread_id, forum_id, title, creator, time_created) VALUES(%s, %s, %s, %s, %s, %s)")

  uuidData = uuid.uuid4()
  session.execute(query, (uuidData, 1, 1, "Does anyone know how to start Redis?", "bob", "Wed, 05 Sep 2018 16:22:29 GMT"))
  uuidData = uuid.uuid4()
  session.execute(query, (uuidData, 2, 1, "Has anyone heard of Edis?", "charlie", "Tue, 04 Sep 2018 13:18:43 GMT"))
  uuidData = uuid.uuid4()
  session.execute(query, (uuidData, 1, 2, "Ask MongoDB questeions here!", "alice", "Tue, 06 Sep 2018 17:18:43 GMT"))
  query = SimpleStatement("INSERT INTO forum.posts(id, forum_id, thread_id, body, creator, created) VALUES(%s, %s, %s, %s, %s, %s)")

  uuidData = uuid.uuid4()
  session.execute(query, (uuidData, 1, 1, "I'm trying to connect to MongoDB, but it doesn't seem to be running.", "bob", "Tue, 04 Sep 2018 15:42:28 GMT"))
  uuidData = uuid.uuid4()
  session.execute(query, (uuidData, 1, 1, "Ummm. maybe 'sudo service start mongodb'?", "bob", "Tue, 04 Sep 2018 15:45:36 GMT"))
  uuidData = uuid.uuid4()
  session.execute(query, (uuidData, 1, 2, "I need help with it", "charlie", "Tue, 06 Sep 2018 17:18:43 GMT"))
  uuidData = uuid.uuid4()
  session.execute(query, (uuidData, 2, 1, "It is some new framework for Redis.. disregard..", "charlie", "Tue, 04 Sep 2018 13:49:36 GMT"))

  print("**************************************")
  print(" D A T A B A S E   C R E A T E D")
  print("**************************************")

  cluster.shutdown()
