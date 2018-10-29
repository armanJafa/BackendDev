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
import time, datetime
import myDb
app = Flask(__name__)
app.url_map.strict_slashes = False

#########################################
# Initialzie, create and fill database
#########################################

# Sets the path of the database
DATABASE = './data.db'
shard0 = './shard0.db'
shard1 = './shard1.db'
shard2 = './shard2.db'


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource cannot be found.</p>", 404


#initializes the databases
myDb.init_db(DATABASE,"init.sql",app)
myDb.init_db(shard0,"initShard.sql",app)
myDb.init_db(shard1,"initShard.sql",app)
myDb.init_db(shard2,"initShard.sql",app)

#finds the shard that the post is located
def find_shard(id):
    return "./shard" + str(int(id)%3) + ".db"

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
  def check_credentials(self, username, password, DATABASE):
    valid = False
    conn = myDb.get_connections(DATABASE)
    data = conn.execute('SELECT * FROM auth_users').fetchall()
    for entry in data:
      if entry["username"] == username and entry["password"] == password:
        valid = True
    return valid

#########################################
# forum_id_found:
# param: takes in the
# uses:  used to override the check_credentials to check the Database
# for authorized users
#########################################
def forum_id_found(value):
  conn = myDb.get_connections(DATABASE)
  all_info = conn.execute('SELECT * FROM forums').fetchall()
  validNewForum = False
  for forum in all_info:
    print(forum["id"])
    print(forum["id"] == int(value))
    if forum["id"] == value:
      validNewForum = True
  conn.close()
  print(validNewForum)
  return validNewForum

def valid_username(newUsername):
  conn = myDb.get_connections(DATABASE)
  data = conn.execute('SELECT * FROM auth_users').fetchall()
  validNewUser = True
  for user in data:
    if user["username"] == newUsername:
      validNewUser = False
  return validNewUser

#checks for valid new Forum entry
def check_validForum(value,DATABASE):
  conn = myDb.get_connections(DATABASE)
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
    con = myDb.get_connections(DATABASE)
    all_forums = con.execute('SELECT * FROM forums').fetchall()
    print(all_forums)
    return jsonify(all_forums)

#########################################
# GET - Get all threads as requested
#########################################
@app.route("/forums/<forum_id>", methods=['GET'])
def threads(forum_id):
    con = myDb.get_connections(DATABASE)
    query = 'SELECT * FROM threads WHERE forum_id=' + forum_id + ' ORDER BY id'
    all_threads = con.execute(query).fetchall()
    if len(all_threads)==0:
        return page_not_found(404)
    else:
        return jsonify(all_threads)

#########################################
# GET - Get all posts as requested
#########################################
@app.route("/forums/<forum_id>/<thread_id>", methods=['GET'])
def posts(forum_id, thread_id):
    shard = find_shard(thread_id)
    con = myDb.get_connections(shard)
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
  db = myDb.get_db(DATABASE)
  db.row_factory = myDb.dict_factory
  conn = db.cursor()

  #pulls all forums and makes it to a json obj
  all_forums = conn.execute('SELECT * FROM forums').fetchall()
  req_data = request.get_json()

  #checks for valid forum entry
  if(check_validForum(req_data,DATABASE)):

    #gets input from user
    username = request.authorization['username']
    password = request.authorization['password']

    #checks to see if user has proper auth
    if b_auth.check_credentials(username, password,DATABASE):
      #inserts into the database
      forumName = req_data['name']
      conn.execute('INSERT INTO forums(name,creator) VALUES(?,?)', (forumName,username))
      db.commit()

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

  db.close()
  return response

#########################################
# POST - Create post
#########################################
@app.route("/forums/<forum_id>/<thread_id>", methods=['POST'])
def create_post(forum_id, thread_id):

    #TODO: change the DATABASE to be the shard of thread_id mod 3
    req_data = request.get_json()
    shard = find_shard(thread_id)
    db = myDb.get_db(shard)
    db.row_factory = myDb.dict_factory
    conn = db.cursor()

    #TODO: find out how to add post using only one DB
    db = myDb.get_db(DATABASE)
    db.row_factory = myDb.dict_factory
    con = db.cursor()

    b_auth = myAuthorizor()
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
        if(b_auth.check_credentials(check_user, check_pw, DATABASE)):
          con.execute('INSERT INTO posts VALUES(?,?,?,?,?)',(forum_id,thread_id, post_text,check_user,time_stamp))
          db.commit()
          check_posts = con.execute('SELECT * FROM posts').fetchall()
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

  req_data = request.get_json()

  db = myDb.get_db(DATABASE)
  db.row_factory = myDb.dict_factory
  con = db.cursor()
  b_auth = myAuthorizor(DATABASE)

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
  if(b_auth.check_credentials(username, password, DATABASE)):
    if forum_id_found(int(forum_id)):
      con.execute('UPDATE threads SET id= id+1 WHERE forum_id =' + forum_id)
      con.execute('UPDATE posts SET thread_id= thread_id+1')
      con.execute('INSERT INTO threads(id,forum_id,title,creator,time_created) VALUES(?,?,?,?,?)', (1,forum_id,threadTitle,username,time_stamp))
      con.execute('INSERT INTO posts VALUES(?,?,?,?,?)', (forum_id, 1,text,username,time_stamp))
      db.commit()
      response = Response("HTTP 201 Created\n" + "Location header field set to /forums/"+ forum_id + "/" + str(1) +" for new thread.",201,mimetype = 'application/json')
      response.headers['Location'] = "/forums/" + forum_id + "/" + str(1)
    else:
      invalMsg = "HTTP 404 Not Found"
      response = Response(invalMsg,404,mimetype = 'application/json')
  else:
    invalMsg = "HTTP 401 Not Authorized"
    response = Response(invalMsg,401,mimetype = 'application/json')
  db.close()
  return response

#########################################
# POST - Creating User
#########################################

@app.route("/users", methods=['POST'])
def users():
    db = myDb.get_db(DATABASE)
    db.row_factory = myDb.dict_factory
    conn = db.cursor()

    req_data = request.get_json()
    newUser = req_data['username']
    newPass = req_data['password']

    if valid_username(newUser):
      conn.execute('INSERT INTO auth_users(username,password) VALUES(?,?)',(newUser,newPass))
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
  db = myDb.get_db(DATABASE)
  db.row_factory = myDb.dict_factory
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
