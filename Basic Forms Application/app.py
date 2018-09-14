#importing flask
from flask import Flask, request, render_template
import json
import sqlite3

app = Flask(__name__)

"""TODO: 
       initialize the DB 
"""

#starting point to the flask app
@app.route("/")
def homePage():
    return render_template('echo.html')

#triggered once the find forms button is pressed
@app.route("/forms", methods=["GET"])
def listForms():

    return

#triggered when the user wants to create a new form
@app.route("/forms", methods=["POST"])
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