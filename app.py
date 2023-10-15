from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from os import getenv
from db import get_userid, get_username, get_messages, get_latest, get_followed, get_comments, db
from secrets import token_hex

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")

db.init_app(app)

if __name__ == "__main__":
    app.run()

#Index page
@app.route("/")
def index():
    messages = get_latest()
    return render_template("index.html", count=len(messages), messages=messages)

#Message search method
@app.route("/messages/search", methods=["POST"])
def search():
    query = request.form["query"]
    if session["username"]:
        if session["csrf_token"] != request.form["csrf_token"]:
            return render_template("error.html", error="Error 403. Forbidden.")
    if query:
        sql = text("SELECT id, content FROM messages WHERE content LIKE :query;")
        result = db.session.execute(sql, {"query":"%"+query+"%"})
        messages = result.fetchall()
        return render_template("messages.html", count=len(messages), messages=messages)

#Page shows all messages
@app.route("/messages")
def messages_all():
    messages = get_messages()
    return render_template("messages.html", count=len(messages), messages=messages)

#page shows followed peoples messages
@app.route("/followed")
def messages_followed():
    messages = get_followed()
    return render_template("followed.html", count=len(messages), messages=messages)

#Page shows detailed info on message
@app.route("/messages/<int:id>")
def detailed(id):
    sql = text("SELECT id, content, posted_by FROM messages WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    message = result.fetchone()
    username = get_username(message[2])
    comments = get_comments(id)
    return render_template("detailed.html", message=message, comments=comments, username=username, user_id=message[2])

#Page that allows new messages to be posted
@app.route("/messages/new")
def messages_new():
    return render_template("messages_new.html")

#Page that adds new messages to database
@app.route("/newmessage", methods=["POST"])
def newmessage():
    content = request.form["message"]
    if session["csrf_token"] != request.form["csrf_token"]:
        return render_template("error.html", error="Error 403. Forbidden.")
    if content:
        user = get_userid()
        sql = text("INSERT INTO messages (content, posted_by, hidden) VALUES (:content, :posted_by, :hidden);")
        db.session.execute(sql, {"content":content, "posted_by":user, "hidden":"f"})
        db.session.commit()
    return redirect("/messages")

#Login info can be give on thi page
@app.route("/login")
def login():
    return render_template("login.html")

#Login info is handled trough this operation
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
            session["csrf_token"] = token_hex(16)
            return redirect("/")
        else:
            return redirect("/login")

#New user can be registered on this page
@app.route("/register")
def register():
    return render_template("/register.html")

#Handles the database input for new users
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
        session["csrf_token"] = token_hex(16)
        return redirect("/")
    return redirect("/register")

#Logs out the current user
@app.route("/logout")
def logout():
    session["username"] = None
    session["csrf_token"] = None
    return redirect("/")

#Handles adding a new commet to database
@app.route("/newcomment", methods=["POST"])
def new_comment():
    content = request.form["comment"]
    id = request.form["id"]
    user = session["username"]
    if not user:
        user="Anonymous"
    else:
        if session["csrf_token"] != request.form["csrf_token"]:
            return render_template("error.html", error="Error 403. Forbidden.")
    if content:
        sql = text("INSERT INTO comments (content, source_msg, posted_by, hidden) VALUES (:content, :source_msg, :posted_by, :hidden);")
        db.session.execute(sql, {"content":content, "source_msg":id, "posted_by":user, "hidden":"f"})
        db.session.commit()
    return redirect(f"/messages/{id}")

#Adds followed information to database
@app.route("/followuser", methods=["POST"])
def follow_user():
    user = get_userid()
    id = request.form["id"]
    if session["csrf_token"] != request.form["csrf_token"]:
        return render_template("error.html", error="Error 403. Forbidden.")
    if user:
        sql = text("INSERT INTO follows (user_id, following_id) VALUES (:user_id, :following_id);")
        db.session.execute(sql, {"user_id":user, "following_id":id})
        db.session.commit()
        return redirect(f"/user/{id}")
    return render_template("error.html", error="Must be logged in to follow users!")

#Removes followed information from database
@app.route("/unfollowuser", methods=["POST"])
def unfollow_user():
    user = get_userid()
    id = request.form["id"]
    if session["csrf_token"] != request.form["csrf_token"]:
        return render_template("error.html", error="Error 403. Forbidden.")
    if user:
        sql = text("DELETE FROM follows WHERE user_id=:user_id AND following_id=:following_id;")
        db.session.execute(sql, {"user_id":user, "following_id":id})
        db.session.commit()
        return redirect(f"/user/{id}")
    return render_template("error.html", error="Must be logged in to follow users!")

#Page detailing information of specific users
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