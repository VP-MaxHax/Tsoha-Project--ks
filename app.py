from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///postgres"
db = SQLAlchemy(app)

@app.route("/")
def index():
    result = db.session.execute(text("SELECT content FROM messages"))
    messages = result.fetchall()
    #raise Exception(messages)
    return render_template("index.html", count=len(messages), messages=messages) 

@app.route("/login")
def login():
    return "Login page"

@app.route("/register")
def register():
    return "Register page"