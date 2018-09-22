from flask import Flask, request, render_template, g, jsonify,Response
import json
import sqlite3

app = Flask(__name__)

###### DATABASE SETUP SECTION ######
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

#initializes the data base using flask
def init_db():
  with app.app_context():
      db = get_db()
      with app.open_resource('init.sql', mode='r') as f:
          db.cursor().executescript(f.read())
      db.commit()
  print("*********************\nDATABASE INITALIZED\n*********************")

init_db()

#connects to DB
def get_connections():
  conn = sqlite3.connect(DATABASE)
  conn.row_factory = dict_factory
  cur = conn.cursor()
  return cur

###################################

###### VALIDATION SECTION ######

#checks for valid new Forum entry
def check_validForum(value):
  conn = get_connections()
  all_info = conn.execute('SELECT * FROM forums').fetchall()
  validNewForum = True 
  print(all_info)
  for forum in all_info:
    if forum["name"] == value["name"]:
      validNewForum = False
  return validNewForum

###################################

#starting point to the flask app
@app.route("/")
def homePage():
    check_validForum("h")
    return "<h1>Test Page</h1>"

'''TODO: 
      check to see if auth user is doing POST
      add the authorized creator to the insert for the POST to sql
      add the location header 
'''
@app.route("/forums/", methods=['GET','POST'])
def forums():
  if request.method == 'POST':
    #connects to db
    conn = get_connections()
    #pulls all forums and makes it to a json obj
    all_forums = conn.execute('SELECT * FROM forums').fetchall()
    req_data = request.get_json()
    
    #this keeps anyone from posting unneeded data fields
    temp = {"name":req_data['name']}

    if(check_validForum(req_data)):

      #inserts into the database
      conn.execute('INSERT INTO forums(name, creator) VALUES(' + temp["name"] +', creator')
      
      #pulls all forums and makes it to a json obj
      all_forums = conn.execute('SELECT * FROM forums').fetchall()
      print(all_forums)
      
      #returns a response
      response = Response("",201,mimetype = 'application/json')
      response.headers['Location'] = ""
    
    #if th conflict exisits return an error message
    else:
      invalMsg = {"error":"Conflict if forum exists"}
      response = Response(json.dumps(invalMsg),409,mimetype = 'application/json')
    return response

  else:
    con = get_connections()
    all_forums = con.execute('SELECT * FROM forums').fetchall()
    return jsonify(all_forums)

''' TODO:
          create the post method
              check for a valid forum entry 
              get timestamp for the post 
              get author for the post
'''
@app.route("/forums/<int:forum_id>", methods=['GET','POST'])
def threads():
  if request.method == 'POST':
    

    return None
  else:
    con = get_connections()
    all_forums = con.execute('SELECT * FROM forums').fetchall()
    return print("forum_id")

'''TODO:
          create a GET for all posts
          create a POST for posts
'''
@app.route("/forums/<int:forum_id>/<int:thread_id>", methods=['GET','POST'])
def posts():
  if request.method == 'POST':
    return None
  else:
    return None

'''TODO:
          create a GET for all users 
          create a POST for users
'''
@app.route("/users", methods=['GET','POST'])
def users():

  return None

if __name__ == "__main__":
  app.run(debug=True)