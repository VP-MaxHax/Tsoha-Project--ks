from datetime import datetime
from flask import render_template, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

db = SQLAlchemy()

#Fetch user id based on active session username
def get_userid():
    if session["username"]:
        sql = text("SELECT user_id FROM users WHERE username=:username")
        result = db.session.execute(sql, {"username":session["username"]})
        user = result.fetchone()
        return user[0]
    return None

#Fetch username based on user id.
def get_username(user_id: int):
    sql = text("SELECT username FROM users WHERE user_id=:user_id")
    result = db.session.execute(sql, {"user_id":user_id})
    username = result.fetchone()
    return username

#Fetch all messages on messages table
def get_messages():
    if get_membership():
        result = db.session.execute(text("SELECT id, content FROM messages"))
        count = db.session.execute(text("SELECT COUNT(*) FROM messages"))
    else:
        result = db.session.execute(text("SELECT id, content FROM messages\
                                          WHERE is_for_members=False"))
        count = db.session.execute(text("SELECT COUNT(*) FROM messages\
                                         WHERE is_for_members=False"))
    messages = result.fetchall()
    amount = count.fetchone()
    return messages, amount

#Fetch all members only messages
def get_clubmessages():
    result = db.session.execute(text("SELECT id, content FROM messages\
                                      WHERE is_for_members=True"))
    count = db.session.execute(text("SELECT COUNT(*) FROM messages\
                                     WHERE is_for_members=True"))
    messages = result.fetchall()
    amount = count.fetchone()
    return messages, amount

#Fetch latest five messages from database
def get_latest():
    if get_membership():
        result = db.session.execute(text("SELECT id, content FROM messages\
                                          ORDER BY id DESC LIMIT 5"))
    else:
        result = db.session.execute(text("SELECT id, content FROM messages\
                                          WHERE is_for_members=False ORDER BY id DESC LIMIT 5"))
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
            result = db.session.execute(text(f"SELECT id, content FROM messages\
                                              WHERE posted_by={following}"))
            count = db.session.execute(text(f"SELECT COUNT(*) FROM messages\
                                             WHERE posted_by={following}"))
        else:
            result = db.session.execute(text(f"SELECT id, content FROM messages\
                                              WHERE posted_by={following}\
                                                  AND is_for_members=False"))
            count = db.session.execute(text(f"SELECT COUNT(*) FROM messages\
                                             WHERE posted_by={following}\
                                                  AND is_for_members=False"))
        messages = result.fetchall()
        amount = count.fetchone()
        return messages, amount
    return render_template("error.html", error="Must be logged in to get followed list!")

#Fetch comments for specific message specified by id
def get_comments(message_id: int):
    sql = text("SELECT content, posted_by, poster_id FROM comments WHERE source_msg=:source_msg")
    result = db.session.execute(sql, {"source_msg":message_id})
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

def is_admin():
    user = get_userid()
    if user:
        sql = text("SELECT is_staff FROM users WHERE user_id=:user_id")
        result = db.session.execute(sql, {"user_id":user})
        staff = result.fetchone()
        return staff[0]
    return False

#Updates user_log table with user login/logout info.
def log_user(action_type: str):
    user = get_userid()
    now = datetime.now()
    sql = text("INSERT INTO user_log (user_id, action, time) VALUES (:user_id, :action, :time);")
    db.session.execute(sql, {"user_id":user, "action":action_type, "time":now})
    db.session.commit()

#Fetches all all rows from tables users, messages and comments. Used in admin page.
def fetch_all():
    sql_users = db.session.execute(text("SELECT user_id, username FROM users ORDER BY user_id"))
    sql_messages = db.session.execute(text("SELECT id, content, posted_by FROM messages ORDER BY id"))
    sql_comments = db.session.execute(text("SELECT comment_id, content, source_msg, poster_id FROM comments ORDER BY comment_id"))
    users = sql_users.fetchall()
    messages = sql_messages.fetchall()
    comments = sql_comments.fetchall()
    return users, messages, comments