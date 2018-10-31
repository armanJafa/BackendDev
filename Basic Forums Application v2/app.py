#########################################
# FLASK - RESTful API for discussion forum
# Created by:
# Andrew Nguyen, Austin Msuarez, Armin Jafa
# CPSC 476 - Project 1
# September 26, 2018
#########################################

#TODO: 
'''
    THREADS:
        Need to be listed in reverse chronological order
        On creation the text needs to be added to the post shard
        Update ids for threads and posts
        
    POSTS:
        Creation needs to update timestamp of thread
        Need to add GUID
'''

from flask import Flask, request, render_template, g, jsonify,Response
from flask_basicauth import BasicAuth
import json
import time, datetime
import myDb
import sqlite3
import uuid

app = Flask(__name__)

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
# init_test_posts:
# param: forum_id, thread_id, body, creator, timestamp
# uses:  initializes the posts
#########################################
def insert_post(forum_id, thread_id, body, creator, timestamp):
    shard_num = int(thread_id) % 3
    if shard_num == 0:
      print("Shard number: " + str(shard_num) + " selected.")
      db = myDb.get_db_s0()
    elif shard_num == 1:
      print("Shard number: " + str(shard_num) + " selected.")
      db = myDb.get_db_s1()
    elif shard_num == 2:
      print("Shard number: " + str(shard_num) + " selected.")
      db = myDb.get_db_s2()

    uuidData = str(uuid.uuid4())

    #initializing POSTs into the shards
    db.row_factory = myDb.dict_factory
    con = db.cursor()
    tmp = datetime.datetime.strptime(timestamp,"%a, %d %b %Y %H:%M:%S %Z")
    con.execute('INSERT INTO posts VALUES(?,?,?,?,?,?)',(uuidData,forum_id,thread_id,body,creator,tmp))
    db.commit()
    myDb.teardown_db("shard" + str(shard_num))

def insert_thread(id,forum_id,title,creator, timestamp):
    db = myDb.get_db(DATABASE)
    #initializing threads into the shards
    db.row_factory = myDb.dict_factory
    con = db.cursor()
    tmp = datetime.datetime.strptime(timestamp,"%a, %d %b %Y %H:%M:%S %Z")
    con.execute('INSERT INTO threads VALUES(?,?,?,?,?)',(id,forum_id,title,creator, tmp))
    db.commit()
    myDb.teardown_db(DATABASE)

# #begins initialization of the posts
with app.app_context():

  insert_thread(1, 1, "Does anyone know how to start Redis?", "bob", "Wed, 05 Sep 2018 16:22:29 GMT")
  insert_thread(2, 1, "Has anyone heard of Edis?", "charlie", "Tue, 04 Sep 2018 13:18:43 GMT")
  insert_thread(3, 1, "Ask MongoDB questeions here!", "alice", "Tue, 06 Sep 2018 17:18:43 GMT")
  insert_thread(1, 2, "Ask PYTHON questeions here!", "alice", "Tue, 06 Sep 2018 17:18:43 GMT")
  insert_thread(2, 2, "Ask Java questeions here!", "alice", "Tue, 06 Sep 2018 17:18:43 GMT")
  insert_thread(3, 2, "Ask JS questeions here!", "bob", "Tue, 06 Sep 2018 17:18:43 GMT")
  insert_thread(4, 2, "Ask Redis questeions here!", "charlie", "Tue, 06 Sep 2018 17:18:43 GMT")
  insert_thread(5, 2, "Ask C questeions here!", "alice", "Tue, 06 Sep 2018 17:18:43 GMT")
  insert_thread(6, 2, "Ask FOO questeions here!", "alice", "Tue, 06 Sep 2018 17:18:43 GMT")
  insert_post(1,1,"Never gonna give you up","Charlie","Tue, 07 Sep 2018 14:49:36 GMT")
  insert_post(1,2,"Never gonna let you down ","Charlie","Tue, 03 Sep 2018 11:49:36 GMT")
  insert_post(1,3,"Never gonna run around and desert you","Charlie","Wed, 04 Sep 2018 01:49:36 GMT")
  insert_post(1,4,"Never gonna make you cry","Charlie","Fri, 02 Sep 2018 12:49:36 GMT")
  insert_post(2,1,"Never gonna say goodbye","Charlie","Tue, 01 Sep 2018 23:49:36 GMT")
  insert_post(2,2,"Never gonna tell a lie and hurt you","Charlie","Mon, 07 Sep 2018 22:49:36 GMT")
  insert_post(2,3,"Never gonna give you up","Charlie","Sat, 09 Sep 2018 12:49:36 GMT")
  insert_post(2,4,"Never gonna let you down","Charlie","Tue, 11 Sep 2018 04:49:36 GMT")
  insert_post(2,5,"Never gonna run around and desert you","Charlie","Tue, 19 Sep 2018 04:49:36 GMT")
  insert_post(2,6,"Never gonna make you cry","Charlie","Tue, 16 Sep 2018 04:49:36 GMT")

#########################################
# Authorization section - Check valid user
#########################################

#####################################################################
# myAuthorizor:
# param: takes in BasicAuth
# uses:  used to override the check_credentials to check the Database
# for authorized users
#####################################################################
class myAuthorizor(BasicAuth):
  def check_credentials(self, username, password, DATABASE):
    valid = False
    conn = myDb.get_connections(DATABASE)
    data = conn.execute('SELECT * FROM auth_users').fetchall()
    for entry in data:
      if entry["username"] == username and entry["password"] == password:
        valid = True
    conn.close()
    return valid

#####################################################################
# forum_id_found:
# param: takes in the
# uses:  used to override the check_credentials to check the Database
#####################################################################
def forum_id_found(value):
  conn = myDb.get_connections(DATABASE)
  all_info = conn.execute('SELECT * FROM forums').fetchall()
  validNewForum = False
  for forum in all_info:
    if forum["id"] == value:
      validNewForum = True
  conn.close()
  return validNewForum

############################################################
# valid_username:
# param: newUsername
# uses:  checks to see if the username isn't already used
#############################################################
def valid_username(newUsername):
  conn = myDb.get_connections(DATABASE)
  data = conn.execute('SELECT * FROM auth_users').fetchall()
  validNewUser = True
  for user in data:
    if user["username"] == newUsername:
      validNewUser = False
  return validNewUser

############################################################
# check_validForum:
# param: value,DATABASE
# uses:  checks to see if the forum isn't already used
#############################################################
def check_validForum(value,DATABASE):
  conn = myDb.get_connections(DATABASE)
  all_info = conn.execute('SELECT * FROM forums').fetchall()
  validNewForum = True
  for forum in all_info:
    if forum["name"] == value["name"]:
      validNewForum = False
  return validNewForum

############################################################
# check_forum:
# param: forum_id
# uses:  checks to see if there is anything in the forum
#############################################################
def check_forum(forum_id):
  conn = myDb.get_connections(DATABASE)
  checkForum = conn.execute('SELECT * FROM forums WHERE id = ' + forum_id).fetchall()
  if len(checkForum) == 0:
    return False
  else:
    return True

############################################################
# check_thread:
# param: thread_id, forum_id
# uses:  checks to see if there is anything in the thread
#############################################################
def check_thread(thread_id, forum_id):
  conn = myDb.get_connections(DATABASE)
  checkThread = conn.execute('SELECT * FROM threads WHERE threads.id = ' + thread_id + ' AND threads.forum_id = ' + forum_id).fetchall()
  if len(checkThread) == 0:
    return False
  else:
    return True

#########################################
# GET - Get all forums
#########################################
@app.route("/forums", methods=['GET'])
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
    query = 'SELECT id, forum_id, title, creator, time_created FROM threads WHERE forum_id=' + forum_id + ' ORDER  BY time_created DESC'
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
@app.route("/forums", methods=['POST'])
def post_forums():

  b_auth = myAuthorizor()
  db = myDb.get_db(DATABASE)
  db.row_factory = myDb.dict_factory
  conn = db.cursor()

  #pulls all forums and makes it to a json obj
  #all_forums = conn.execute('SELECT * FROM forums').fetchall()
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

    #Check to see if forum and thread exists
    forumCheck = check_forum(forum_id)
    threadCheck =  check_thread(thread_id, forum_id)

    req_data = request.get_json()
    b_auth = myAuthorizor()
    check_user = request.authorization['username']
    check_pw = request.authorization['password']
    authed = b_auth.check_credentials(check_user, check_pw, DATABASE)

    shard_num = int(thread_id) % 3
    if shard_num == 0:
      print("Shard number: " + str(shard_num) + " selected.")
      db = myDb.get_db_s0()
    elif shard_num == 1:
      print("Shard number: " + str(shard_num) + " selected.")
      db = myDb.get_db_s1()
    elif shard_num == 2:
      print("Shard number: " + str(shard_num) + " selected.")
      db = myDb.get_db_s2()

    db.row_factory = myDb.dict_factory
    con = db.cursor()

    dataUUID = str(uuid.uuid4())

    if forumCheck == True and threadCheck == True:
        check_posts = con.execute('SELECT * FROM posts').fetchall()
        # Get the post text
        post_text = req_data['text']

        # Create the timestamp
        ts = time.time()
        time_stamp = st = datetime.datetime.fromtimestamp(ts).strftime('%a, %d %b %Y %H:%M:%S %Z')
        tmp = time_stamp + "GMT"
        time_stamp = datetime.datetime.strptime(tmp,'%a, %d %b %Y %H:%M:%S %Z')
        
        #If authorized user, insert
        if(authed):
          con.execute('INSERT INTO posts VALUES(?,?,?,?,?,?)',(dataUUID, forum_id,thread_id, post_text,check_user,time_stamp))
          db.commit()
          check_posts = con.execute('SELECT * FROM posts').fetchall()
          response = Response("HTTP 201 Created\n" + "Location Header field set to /forums/" + forum_id + "/" + thread_id + " for new forum.", 201, mimetype = 'application/json')
          response.headers['Location'] = "/forums/" + forum_id + "/" + thread_id + str(1)
          myDb.teardown_db("shard"+str(shard_num))
         
          db = myDb.get_db(DATABASE)
          db.row_factory = myDb.dict_factory
          con = db.cursor()
          con.execute('UPDATE threads SET time_created = ? WHERE forum_id = ? AND id = ?', (time_stamp,forum_id,thread_id))
          db.commit()
          myDb.teardown_db(DATABASE)

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

  b_auth = myAuthorizor()

  #gets input from user
  username = request.authorization['username']
  password = request.authorization['password']

  #gets json input
  threadTitle = req_data['title']
  text = req_data['text']

  # Create the timestamp
  ts = time.time()
  time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%a, %d %b %Y %H:%M:%S %Z')
  tmp = time_stamp + "GMT"
  time_stamp = datetime.datetime.strptime(tmp,'%a, %d %b %Y %H:%M:%S %Z')
  #If authorized user, insert
  if(b_auth.check_credentials(username, password, DATABASE)):
    if forum_id_found(int(forum_id)):
      db = myDb.get_db(DATABASE)
      db.row_factory = myDb.dict_factory
      con = db.cursor()
    # gets the top id
      threadsList = con.execute('Select * FROM threads WHERE forum_id = ? ORDER BY id DESC LIMIT 0,1', (forum_id)).fetchall()
      for thread in threadsList:
          currentId = int(thread['id'])

    # inserting new items
      con.execute('INSERT INTO threads(id,forum_id,title,creator,time_created) VALUES(?,?,?,?,?)', (currentId+1,forum_id,threadTitle,username,time_stamp))
      db.commit()
      db.close()

      insert_post(forum_id, currentId+1, text, username, tmp)
      response = Response("HTTP 201 Created\n" + "Location header field set to /forums/"+ forum_id + "/" + str(currentId+1) +" for new thread.",201,mimetype = 'application/json')
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
