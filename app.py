from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from os import getenv
from db import get_userid, get_username, get_messages, get_latest, get_followed, get_comments, db, get_membership, get_clubmessages, log_user
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
    return redirect("/messages")

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
def detailed(id:int):
    sql = text("SELECT id, content, posted_by FROM messages WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    message = result.fetchone()
    username = get_username(message[2])
    comments = get_comments(id)
    return render_template("detailed.html", message=message, comments=comments, username=username, user_id=message[2])

#Page that allows new messages to be posted
@app.route("/messages/new")
def messages_new():
    user = get_userid()
    if user and get_membership:
        return render_template("messages_new_mb.html")
    return render_template("messages_new.html")

#Page that adds new messages to database
@app.route("/newmessage", methods=["POST"])
def newmessage():
    content = request.form["message"]
    is_for_members = request.form["is_for_members"]
    if session["csrf_token"] != request.form["csrf_token"]:
        return render_template("error.html", error="Error 403. Forbidden.")
    if content:
        user = get_userid()
        sql = text("INSERT INTO messages (content, posted_by, hidden, is_for_members) VALUES (:content, :posted_by, :hidden :is_for_members);")
        db.session.execute(sql, {"content":content, "posted_by":user, "hidden":"f", "is_for_members":is_for_members})
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
            log_user("login")
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
        log_user("login")
        return redirect("/")
    return redirect("/register")

#Logs out the current user
@app.route("/logout")
def logout():
    log_user("logout")
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
        user = "Anonymous"
        poster_id = "0"
    else:
        poster_id = get_userid()
        if session["csrf_token"] != request.form["csrf_token"]:
            return render_template("error.html", error="Error 403. Forbidden.")
    if content:
        sql = text("INSERT INTO comments (content, source_msg, posted_by, poster_id, hidden) VALUES (:content, :source_msg, :posted_by, :poster_id, :hidden);")
        db.session.execute(sql, {"content":content, "source_msg":id, "posted_by":user, "poster_id":poster_id, "hidden":"f"})
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
def user_details(id:int):
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

#Page for getting Äks-club memberships
@app.route("/membership")
def membership():
    return render_template("membership.html")

#Handles writing new memberships to database
@app.route("/apply_membership", methods=["POST"])
def apply_membership():
    user = get_userid()
    code = request.form["code"]
    exp_time = datetime.now() + timedelta(minutes=15)
    if session["csrf_token"] != request.form["csrf_token"]:
        return render_template("error.html", error="Error 403. Forbidden.")
    if user and code == "Äks4Life":
        sql = text("UPDATE users SET is_sub=True, sub_exp=:exp_time WHERE user_id=:user_id;")
        exp_time = datetime.now() + timedelta(minutes=15)
        db.session.execute(sql, {"exp_time":exp_time, "user_id":user})
        db.session.commit()
        return redirect("/")
    return redirect("/membership")

#Members only page
@app.route("/club")
def aks_club():
    user = get_userid
    if user and get_membership():
        messages = get_clubmessages()
        return render_template("club.html", count=len(messages), messages=messages)
    return render_template("error.html", error="You have to be logged in and a Äks-Club member to access this page.")

