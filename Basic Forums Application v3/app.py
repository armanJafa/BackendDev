#########################################
# FLASK - RESTful API for discussion forum
# Created by:
# Andrew Nguyen, Austin Msuarez, Armin Jafa
# CPSC 476 - Project 1
# September 26, 2018
#########################################

from flask import Flask, request, render_template, g, jsonify,Response
from flask_basicauth import BasicAuth
from cassandra import ConsistencyLevel
from init_cql import init_cassandra
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import json
import sqlite3
import time, datetime
import uuid

app = Flask(__name__)
app.url_map.strict_slashes = False

KEYSPACE = 'forum'

#########################################
# Initialzie, create and fill database
#########################################

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource cannot be found.</p>", 404

init_cassandra()

#########################################
# Authorization section - Check valid user
#########################################

#########################################
# myAuthorizor:
# param: takes in BasicAuth
# uses:  used to override the check_credentials to check the Database
# for authorized users
#########################################

class myAuthorizor(BasicAuth):
  def check_credentials(self, username, password):
    valid = False
    cluster = Cluster(['172.17.0.2'])
    session = cluster.connect()
    session.set_keyspace(KEYSPACE)
    query = SimpleStatement('SELECT username, password FROM auth_users')
    data = session.execute(query)
    for row in data:
        if row.username == username and row.password == password:
            valid = True
    return valid

def forum_id_found(value):
  cluster = Cluster(['172.17.0.2'])
  session = cluster.connect()
  session.set_keyspace(KEYSPACE)

  all_info = session.execute('SELECT * FROM forums')
  validNewForum = False
  for forum in all_info:
    print(forum.id)
    if forum.id == value:
      validNewForum = True
  print(validNewForum)
  return validNewForum

def valid_username(newUsername):
  cluster = Cluster(['172.17.0.2'])
  session = cluster.connect()
  session.set_keyspace(KEYSPACE)

  query = SimpleStatement('SELECT * FROM auth_users')
  data = session.execute(query)
  validNewUser = True
  for user in data:
    if user.username == newUsername:
      validNewUser = False
  return validNewUser

#checks for valid new Forum entry
def check_validForum(value):
  cluster = Cluster(['172.17.0.2'])
  session = cluster.connect()
  session.set_keyspace(KEYSPACE)

  query = SimpleStatement('SELECT * FROM forums')
  data = session.execute(query)
  validNewForum = True
  for forum in data:
    if forum.name == value["name"]:
      validNewForum = False
  return validNewForum

#########################################
# GET - Get all forums
#########################################

@app.route("/forums/", methods=['GET'])
def get_forums():
    cluster = Cluster(['172.17.0.2'])
    session = cluster.connect()
    session.set_keyspace(KEYSPACE)
    all_forums = session.execute('SELECT * FROM forums')
    return jsonify(list(all_forums))

########################################
# GET - Get all threads as requested
#########################################

@app.route("/forums/<forum_id>", methods=['GET'])
def threads(forum_id):
    # con = get_connections()
    cluster = Cluster(['172.17.0.2'])
    session = cluster.connect()
    session.set_keyspace(KEYSPACE)
    all_threads = session.execute('SELECT * FROM threads WHERE forum_id=' + forum_id)
    all_threads = list(all_threads)
    if len(all_threads)==0:
        return page_not_found(404)
    else:
        return jsonify(all_threads)

#########################################
# GET - Get all posts as requested
#########################################

@app.route("/forums/<forum_id>/<thread_id>", methods=['GET'])
def posts(forum_id, thread_id):
    cluster = Cluster(['172.17.0.2'])
    session = cluster.connect()
    session.set_keyspace(KEYSPACE)
    query = SimpleStatement('SELECT * FROM posts WHERE forum_id=' + forum_id +' AND thread_id='+thread_id)
    all_posts = session.execute(query)
    all_posts = list(all_posts)
    if len(all_posts) == 0:
        return page_not_found(404)
    else:
        return jsonify(all_posts)

#########################################
# POST - Create forum
#########################################

@app.route("/forums/", methods=['POST'])
def post_forums():

  b_auth = myAuthorizor()
  cluster = Cluster(['172.17.0.2'])
  session = cluster.connect()
  session.set_keyspace(KEYSPACE)

  #Get the next ID for new forum
  query = SimpleStatement('SELECT * FROM forums')
  data = session.execute(query)
  count = len(list(data))
  count += 1

  #pulls all forums and makes it to a json obj
  all_forums = session.execute('SELECT * FROM forums')
  req_data = request.get_json()

  #checks for valid forum entry
  if(check_validForum(req_data)):

    #gets input from user
    username = request.authorization['username']
    password = request.authorization['password']

    #checks to see if user has proper auth
    if b_auth.check_credentials(username, password):
      #inserts into the database
      forumName = req_data['name']
      session.execute(
            """
                INSERT INTO forums (id, name, creator)
                VALUES (%s,%s,%s)
            """, (count, forumName, username)
        )

      #returns a success response
      response = Response("HTTP 201 Created\n" + "Location header field set to /forums/"+ forumName +" for new forum.",201,mimetype = 'application/json')
      response.headers['Location'] = "/forums/" + forumName
    else:
      invalMsg = "User not authenticated"
      response = Response(invalMsg,409,mimetype = 'application/json')
  #if th conflict exisits return an error message
  else:
    invalMsg = "HTTP 409 Conflict if forum already exists"
    response = Response(invalMsg,409,mimetype = 'application/json')
  return response

#########################################
# POST - Create post
#########################################

@app.route("/forums/<forum_id>/<thread_id>", methods=['POST'])
def create_post(forum_id, thread_id):
    cluster = Cluster(['172.17.0.2'])
    session = cluster.connect()
    session.set_keyspace(KEYSPACE)

    b_auth = myAuthorizor()
    req_data = request.get_json()
    check_user = request.authorization['username']
    check_pw = request.authorization['password']

    forumCheck = session.execute('SELECT 1 FROM forums where id=%s',(forum_id,))
    threadCheck = session.execute('SELECT 1 FROM threads where id=%s',(thread_id,))

    if len(forumCheck) != 0 or len(threadCheck) != 0:
        # Get the post text
        post_text = req_data['text']

        # Create the timestamp
        ts = time.time()
        time_stamp = st = datetime.datetime.fromtimestamp(ts).strftime('%a, %d %b %Y %H:%M:%S %Z')
        print(time_stamp)

        #If authorized user, insert
        if(b_auth.check_credentials(check_user, check_pw)):
          session.execute('INSERT INTO posts VALUES(%s,%s,%s,%s,%s)',(forum_id,thread_id,post_text,check_user,time_stamp,))
          response = Response("HTTP 201 Created\n" + "Location Header field set to /forums/" + forum_id + "/" + thread_id + " for new forum.", 201, mimetype = 'application/json')
          response.headers['Location'] = "/forums/" + forum_id + "/" + thread_id + str(1)
        else:
          invalMsg = "HTTP 401 Not Authorized"
          response = Response(invalMsg, 404, mimetype = 'application/json')
    else:
        invalMsg = "HTTP 404 Not Found"
        response = Response(invalMsg, 404, mimetype = 'application/json')
    return response

#########################################
 # POST - Create Threads
 #########################################
@app.route("/forums/<forum_id>", methods=['POST'])
def create_threads(forum_id):
  b_auth = myAuthorizor()
  req_data = request.get_json()

  cluster = Cluster(['172.17.0.2'])
  session = cluster.connect()
  session.set_keyspace(KEYSPACE)

  #gets input from user
  username = request.authorization['username']
  password = request.authorization['password']

  #gets json input
  threadTitle = req_data["title"]
  text = req_data["text"]

  # Create the timestamp
  ts = time.time()
  time_stamp = st = datetime.datetime.fromtimestamp(ts).strftime('%a, %d %b %Y %H:%M:%S %Z')

  #If authorized user, insert
  if(b_auth.check_credentials(username, password)):
    if forum_id_found(int(forum_id)):
      session.execute('UPDATE threads SET id=id+1 WHERE forum_id =%s',(forum_id,))
      session.execute('UPDATE posts SET thread_id=thread_id+1')
      session.execute('INSERT INTO threads(id,forum_id,title,creator,time_created) VALUES(%s,%s,%s,%s,%s)', (1,forum_id,threadTitle,username,time_stamp))
      session.execute('INSERT INTO posts VALUES(%s,%s,%s,%s,%s)', (forum_id,1,text,username,time_stamp))

      response = Response("HTTP 201 Created\n" + "Location header field set to /forums/"+ forum_id + "/" + str(1) +" for new thread.",201,mimetype = 'application/json')
      response.headers['Location'] = "/forums/" + forum_id + "/" + str(1)
    else:
      invalMsg = "HTTP 404 Not Found"
      response = Response(invalMsg,404,mimetype = 'application/json')
  else:
    invalMsg = "HTTP 401 Not Authorized"
    response = Response(invalMsg,401,mimetype = 'application/json')
  return response

#########################################
# POST - Creating User
#########################################

@app.route("/users", methods=['POST'])
def users():
    cluster = Cluster(['172.17.0.2'])
    session = cluster.connect()
    session.set_keyspace(KEYSPACE)

    req_data = request.get_json()
    newUser = req_data['username']
    newPass = req_data['password']

    if valid_username(newUser):
      session.execute('INSERT INTO auth_users(username,password) VALUES(%s,%s)',(newUser,newPass,))
      #returns a success response
      response = Response("HTTP 201 Created",201,mimetype = 'application/json')
    else:
      #returns a success response
      response = Response("HTTP 409 Conflict if username already exists\n",409,mimetype = 'application/json')
    return response

#########################################
# PUT - Changing password per user request
#########################################

@app.route("/users/<username>", methods=['PUT'])
def change_password(username):
  #Connect to DB
  b_auth = myAuthorizor()
  cluster = Cluster(['172.17.0.2'])
  session = cluster.connect()
  session.set_keyspace(KEYSPACE)

  #Get data from request
  username = request.authorization['username']
  password = request.authorization['password']

  #Check if username is in DB
  valid = False
  query = SimpleStatement('SELECT username FROM auth_users')
  data = session.execute(query)
  for row in data:
      if row.username == username:
          valid = True

  if valid is False:
      ## RETURN 404 - USER NOT FOUND
      message = {
              'status': 404,
              'message': 'User Not Found: ' + username,
      }
      resp = jsonify(message)
      resp.status_code = 404

      return resp
  elif request.authorization['username'] != username:
      message = {
              'status': 409,
              'message': 'Username: ' + username + ' does not match authorized user: ' + request.authorization['username'],
      }
      resp = jsonify(message)
      resp.status_code = 409

      return resp

  if b_auth.check_credentials(username, password):
      user_update = request.get_json()
      newPassword = user_update['password']
      session.execute('UPDATE auth_users SET password=%s WHERE username=%s',(newPassword, username,))
      updated_user = session.execute('SELECT * FROM auth_users WHERE username=%s',(username,))

      print("*****Checking Credentials*****")
      for row in updated_user:
          print ("Username: " + row.username)
          print ("Password: " + row.password)
      print("*****Checking Credentials*****")

      message = {
              'Message': "Password updated successfully",
              'Username': row.username,
              'Password': row.password,
      }
      updated_pw = jsonify(message)
      return updated_pw
  else:
       message = {
               'status': 401,
               'message': 'Not Authorized',
       }
       resp = jsonify(message)
       resp.status_code = 401
       return resp

if __name__ == "__main__":

  app.run(debug=True)
