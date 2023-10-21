from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

db = SQLAlchemy()

#Fetch user id based on active session username
def get_userid():
    sql = text("SELECT user_id FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":session["username"]})
    user = result.fetchone()
    return user[0]

#Fetch username based on user id.
def get_username(user_id):
    sql = text("SELECT username FROM users WHERE user_id=:user_id")
    result = db.session.execute(sql, {"user_id":user_id})
    username = result.fetchone()
    return username

#Fetch all messages on messages table
def get_messages():
    if get_membership:
        result = db.session.execute(text("SELECT id, content FROM messages"))
    else:
        result = db.session.execute(text("SELECT id, content FROM messages WHERE is_for_members=False"))
    messages = result.fetchall()
    return messages

def get_clubmessages():
    result = db.session.execute(text("SELECT id, content FROM messages WHERE is_for_members=True"))
    messages = result.fetchall()
    return messages

#Fetch latest five messages from database
def get_latest():
    if get_membership:
        result = db.session.execute(text("SELECT id, content FROM messages ORDER BY id DESC LIMIT 5"))
    else:
        result = db.session.execute(text("SELECT id, content FROM messages WHERE is_for_members=False ORDER BY id DESC LIMIT 5"))
    messages = result.fetchall()
    return messages

#Fetch all messages posted by people followed by active user
def get_followed():
    user = get_userid()
    helplist = []
    sub_status = get_membership()
    if user:
        sql = text("SELECT following_id FROM follows WHERE user_id=:user")
        result = db.session.execute(sql, {"user":user})
        following = result.fetchall()
        for i in following:
            helplist.append(str(i[0]))
        following = " OR posted_by=".join(helplist)
        if sub_status:
            sql = text(f"SELECT id, content FROM messages WHERE posted_by={following}")
        else:
            sql = text(f"SELECT id, content FROM messages WHERE posted_by={following} AND is_for_members=False")
        result = db.session.execute(sql)
        messages = result.fetchall()
        return messages
    return render_template("error.html", error="Must be logged in to get followed list!")

#Fetch comments for specific message specified by id
def get_comments(id):
    sql = text("SELECT content, posted_by FROM comments WHERE source_msg=:source_msg")
    result = db.session.execute(sql, {"source_msg":id})
    comments = result.fetchall()
    return comments

#Checks users membership status
def get_membership():
    user = get_userid()
    now = datetime.now()
    if user:
        sql = text("SELECT sub_exp FROM users WHERE user_id=:user_id")
        result = db.session.execute(sql, {"user_id":user})
        sub_exp = result.fetchone()
        if sub_exp[0] > now:
            return True
    return False