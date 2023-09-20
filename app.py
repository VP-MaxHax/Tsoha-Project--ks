from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "a4540e650c519ab55774ce2e5aad57b3"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///postgres"
db = SQLAlchemy(app)

@app.route("/")
def index():
    messages = get_latest()
    return render_template("index.html", count=len(messages), messages=messages) 

def get_messages():
    result = db.session.execute(text("SELECT id, content FROM messages"))
    messages = result.fetchall()
    return messages

def get_latest():
    result = db.session.execute(text("SELECT id, content FROM messages ORDER BY id LIMIT 5"))
    messages = result.fetchall()
    return messages

@app.route("/messages")
def messages_all():
    messages = get_messages()
    return render_template("messages.html", count=len(messages), messages=messages)

@app.route("/messages/<int:id>")
def detailed(id):
    sql = text("SELECT content FROM messages WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    message = result.fetchone()
    return render_template("detailed.html", message=message)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/loginuser",methods=["POST"])
def login_user():
    username = request.form["username"]
    password = request.form["password"]
    sql = text("SELECT user_id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()  
    if not user:
        raise Exception("Wrong username")
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["username"] = username
            return redirect("/")
        else:
            return redirect("/login")

@app.route("/register")
def register():
    return render_template("/register.html")

@app.route("/registeruser", methods=["POST"])
def register_user():
    username = request.form["username"]
    password = request.form["password"]
    if username and password:
        sql = text("INSERT INTO users (username, password, is_sub, sub_exp, is_active, is_staff, last_login) " \
                   "VALUES (:username, :password, :is_sub, :sub_exp, :is_active, :is_staff, :last_login);")
        time = datetime.now()
        db.session.execute(sql, {"username":username, "password":generate_password_hash(password),"is_sub":"f", \
                                 "sub_exp":time, "is_active":"t", "is_staff":"f", "last_login":time})
        db.session.commit()
        session["username"] = username
        return redirect("/")
    return redirect("/register")

@app.route("/logout")
def logout():
    session["username"] = None
    return redirect("/")