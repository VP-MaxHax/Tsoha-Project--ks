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

def get_userid():
    sql = text("SELECT user_id FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":session["username"]})
    user = result.fetchone()
    return user[0]

def get_username(user_id):
    sql = text("SELECT username FROM users WHERE user_id=:user_id")
    result = db.session.execute(sql, {"user_id":user_id})
    username = result.fetchone()
    return username

def get_messages():
    result = db.session.execute(text("SELECT id, content FROM messages"))
    messages = result.fetchall()
    return messages

def get_latest():
    result = db.session.execute(text("SELECT id, content FROM messages ORDER BY id DESC LIMIT 5"))
    messages = result.fetchall()
    return messages

@app.route("/messages/search", methods=["POST"])
def search():
    query = request.form["query"]
    if query:
        sql = text("SELECT id, content FROM messages WHERE content LIKE :query;")
        result = db.session.execute(sql, {"query":"%"+query+"%"})
        messages = result.fetchall()
        return render_template("messages.html", count=len(messages), messages=messages)

@app.route("/messages")
def messages_all():
    messages = get_messages()
    return render_template("messages.html", count=len(messages), messages=messages)

@app.route("/messages/<int:id>")
def detailed(id):
    sql = text("SELECT id, content, posted_by FROM messages WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    message = result.fetchone()
    username = get_username(message[2])
    comments = get_comments(id)
    return render_template("detailed.html", message=message, comments=comments, username=username, user_id=message[2])

@app.route("/messages/new")
def messages_new():
    return render_template("messages_new.html")

@app.route("/newmessage", methods=["POST"])
def newmessage():
    content = request.form["message"]
    if content:
        user = get_userid()
        sql = text("INSERT INTO messages (content, posted_by, hidden) VALUES (:content, :posted_by, :hidden);")
        db.session.execute(sql, {"content":content, "posted_by":user, "hidden":"f"})
        db.session.commit()
    return redirect("/messages")

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

@app.route("/newcomment", methods=["POST"])
def new_comment():
    content = request.form["comment"]
    id = request.form["id"]
    user = session["username"]
    if not user:
        user="Anonymous"
    if content:
        sql = text("INSERT INTO comments (content, source_msg, posted_by, hidden) VALUES (:content, :source_msg, :posted_by, :hidden);")
        db.session.execute(sql, {"content":content, "source_msg":id, "posted_by":user, "hidden":"f"})
        db.session.commit()
    return redirect(f"/messages/{id}")

def get_comments(id):
    sql = text("SELECT content, posted_by FROM comments WHERE source_msg=:source_msg")
    result = db.session.execute(sql, {"source_msg":id})
    comments = result.fetchall()
    return comments

@app.route("/followuser", methods=["POST"])
def follow_user():
    user = get_userid()
    id = request.form["id"]
    if user:
        sql = text("INSERT INTO follows (user_id, following_id) VALUES (:user_id, :following_id);")
        db.session.execute(sql, {"user_id":user, "following_id":id})
        db.session.commit()
        return redirect(f"/user/{id}")
    return render_template("error.html", error="Must be logged in to follow users!")

@app.route("/unfollowuser", methods=["POST"])
def unfollow_user():
    user = get_userid()
    id = request.form["id"]
    if user:
        sql = text("DELETE FROM follows WHERE user_id=:user_id AND following_id=:following_id;")
        db.session.execute(sql, {"user_id":user, "following_id":id})
        db.session.commit()
        return redirect(f"/user/{id}")
    return render_template("error.html", error="Must be logged in to follow users!")

@app.route("/user/<int:id>")
def user_details(id):
    sql = text("SELECT username, last_login FROM users WHERE user_id=:id")
    result = db.session.execute(sql, {"id":id})
    user = result.fetchone()
    sql = text("SELECT following_id FROM follows WHERE user_id=user_id")
    result = db.session.execute(sql, {"user_id":get_userid()})
    following = result.fetchall()
    is_following = False
    for i in following:
        if i[0]==id:
            is_following = True
    return render_template("user.html", user = user, following = is_following, page_id = id)