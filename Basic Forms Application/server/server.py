from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def homePage():
    return render_template('.\index.html')

@app.route("/fourms")
def listForms():
        return

if __name__ == "__main__":
    app.run(debug=True)