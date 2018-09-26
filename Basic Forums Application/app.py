#########################################
# FLASK - RESTful API for discussion forum
# Created by:
# Andrew Nguyen, Austin Msuarez, Armin Jafa
# CPSC 476 - Project 1
# September 26, 2018
#########################################

from flask import Flask, request, render_template, g, jsonify,Response
from flask_basicauth import BasicAuth
import json
import sqlite3
import time, datetime

app = Flask(__name__)
app.url_map.strict_slashes = False

#########################################
# Initialzie, create and fill database
#########################################

# Sets the path of the database
DATABASE = './data.db'

# Connects to the database
def get_db():
  db = getattr(g, '_database', None)
  if db is None:
       db = g._database = sqlite3.connect(DATABASE)
  return db

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource cannot be found.</p>", 404

#initializes the data base using flask
def init_db():
  with app.app_context():
      db = get_db()
      with app.open_resource('init.sql', mode='r') as f:
          db.cursor().executescript(f.read())
      db.commit()
  print("*********************\nDATABASE INITALIZED\n*********************")

#connects to DB
def get_connections():
  conn = get_db()
  conn.row_factory = dict_factory
  cur = conn.cursor()
  return cur

init_db()

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
    conn = get_connections()
    data = conn.execute('SELECT * FROM auth_users').fetchall()
    for entry in data:
      if entry["username"] == username and entry["password"] == password:
        valid = True
    return valid

def valid_username(newUsername):
  conn = get_connections()
  data = conn.execute('SELECT * FROM auth_users').fetchall()
  validNewUser = True
  for user in data:
    if user["username"] == newUsername:
      validNewUser = False
  return validNewUser


#checks for valid new Forum entry
def check_validForum(value):
  conn = get_connections()
  all_info = conn.execute('SELECT * FROM forums').fetchall()
  validNewForum = True
  for forum in all_info:
    if forum["name"] == value["name"]:
      validNewForum = False
  return validNewForum

#########################################
# GET - Get all forums
#########################################

@app.route("/forums/", methods=['GET'])
def get_forums():
    con = get_connections()
    all_forums = con.execute('SELECT * FROM forums').fetchall()
    print(all_forums)
    return jsonify(all_forums)

#########################################
# GET - Get all threads as requested
#########################################

@app.route("/forums/<forum_id>", methods=['GET'])
def threads(forum_id):
    con = get_connections()
    query = 'SELECT * FROM threads WHERE forum_id=' + forum_id
    all_threads = con.execute(query).fetchall()
    if len(all_threads)==0:
        return page_not_found(404)
    else:
        return jsonify(all_threads)

#########################################
# GET - Get all threads as requested
#########################################

@app.route("/forums/<forum_id>/<thread_id>", methods=['GET'])
def posts(forum_id, thread_id):
    con = get_connections()
    all_posts = con.execute('SELECT * FROM posts WHERE posts.forum_id = ' + forum_id + ' AND posts.thread_id = ' + thread_id).fetchall()
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
  db = get_db()
  db.row_factory = dict_factory
  conn = db.cursor()

  #pulls all forums and makes it to a json obj
  all_forums = conn.execute('SELECT * FROM forums').fetchall()
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
      conn.execute('INSERT INTO forums(name,creator) VALUES(\''+forumName+'\',\''+ username+'\')')
      db.commit()

      #returns a success response
      response = Response("HTTP 201 Created\n" + "Location header field set to /forums/<forum_id> for new forum.",201,mimetype = 'application/json')
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
    db = get_db()
    db.row_factory = dict_factory
    con = db.cursor()

    b_auth = myAuthorizor()
    req_data = request.get_json()
    check_user = request.authorization['username']
    check_pw = request.authorization['password']

    forumCheck = con.execute('SELECT 1 FROM forums where id=' + forum_id).fetchall()
    threadCheck = con.execute('SELECT 1 FROM threads where id=' + thread_id).fetchall()

    if len(forumCheck) != 0 or len(threadCheck) != 0:
        # Get the post text
        post_text = req_data['text']

        # Create the timestamp
        ts = time.time()
        time_stamp = st = datetime.datetime.fromtimestamp(ts).strftime('%a, %d %b %Y %H:%M:%S %Z')
        print(time_stamp)

        #If authorized user, insert
        if(b_auth.check_credentials(check_user, check_pw)):
          con.execute('INSERT INTO posts VALUES(' + forum_id + ', ' + thread_id + ',\'' + post_text + '\', \'' + check_user + '\',\'' + time_stamp + '\')')
          db.commit()
          check_posts = con.execute('SELECT * FROM posts').fetchall()
          response = Response("HTTP 201 Created\n" + "Location Header field set to /forums/" + forum_id + "/" + thread_id + str(1) + "for new forum.", 201, mimetype = 'application/json')
          response.headers['Location'] = "/forums/" + forum_id + "/" + thread_id + str(1)
        else:
          invalMsg = "HTTP 401 Not Authorized"
          response = Response(invalMsg, 404, mimetype = 'application/json')
    else:
        invalMsg = "HTTP 404 Not Found"
        response = Response(invalMsg, 404, mimetype = 'application/json')
    return response
#########################################
# POST - Creating User
#########################################

@app.route("/users", methods=['POST'])
def users():
    db = get_db()
    db.row_factory = dict_factory
    conn = db.cursor()

    req_data = request.get_json()
    newUser = req_data['username']
    newPass = req_data['password']

    if valid_username(newUser):
      conn.execute('INSERT INTO auth_users(username,password) VALUES(\''+newUser+'\',\''+ newPass+'\')')
      db.commit()
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
  db = get_db()
  db.row_factory = dict_factory
  con = db.cursor()

  check_user = con.execute('SELECT * FROM auth_users WHERE username= "' + username + '"').fetchall()

  if len(check_user)==0:
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

  user_update = request.get_json()

  con.execute('UPDATE auth_users SET password="' + user_update['password'] + '" WHERE username="' + username + '"')
  updated_user = con.execute('SELECT * FROM auth_users WHERE username="' + username + '"').fetchall()

  print("*****Checking Credentials*****")
  print(check_user)
  print(updated_user)
  print("*****Checking Credentials*****")

  db.commit()

  return jsonify(updated_user)

if __name__ == "__main__":

  app.run(debug=True)
