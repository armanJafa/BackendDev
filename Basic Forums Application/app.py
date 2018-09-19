#importing flask
from flask import Flask, request, render_template,g
import json
import sqlite3

app = Flask(__name__)

"""TODO:
       figure out how to initialize the DB and connect the rest of the time
       parse json
       insert data to json
       update data
"""

#sets the path of the database
DATABASE = './data.db'

#connects to the database
def get_db():
    db = getattr(g, '_data', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

#initializes the data base using flask
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('init.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

#starting point to the flask app
@app.route("/")
def homePage():
    init_db()
    return render_template('echo.html')

#triggered once the find forums button is pressed
@app.route("/forums", methods=["GET"])
def listforums():

    return

#triggered when the user wants to create a new form
@app.route("/forums", methods=["POST"])
def createForm():
    return

def getJson():
    with open("data.json",'r') as inputFile:
        data = json.load(inputFile)
    return data

def setJson(data):

    return

if __name__ == "__main__":
    app.run(debug=True)
