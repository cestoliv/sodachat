import sqlite3
import uuid
import datetime
import os
import sys
import inspect

# Changed the directory to /sources, to make it easier to import locally
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from db.db import DBConnection

# Connection to database
DB = DBConnection()

def signup(name, username, password_hash):
    cur = DB.conn.cursor()
    cur.execute("SELECT username FROM users WHERE username =?",(username,))
    DB.conn.commit()

    username_test = cur.fetchall()
    if username_test != [] :
        return {
            "status": "error",
            "code": "0001"
        }

    uid = uuid.uuid1().hex
    type = "user"
    user_data = [uid, name, username , password_hash, type]

    cur = DB.conn.cursor()
    cur.execute("INSERT INTO users(uid, name, username, password_hash, type) values (?,?,?,?,?)", user_data)
    DB.conn.commit()

    return {
        "status": "success",
        "uid": uid,
        "username": username,
        "name": name
    }

def signin(username, password):
    cur = DB.conn.cursor()
    cur.execute("SELECT uid, name, password_hash FROM users WHERE username =?",(username,))
    DB.conn.commit()

    user_data = cur.fetchall()
    if user_data == [] :
        return {
            "status": "error",
            "code": "0001"
        }

    user_uid = user_data[0][0]
    user_name = user_data[0][1]
    user_password_hash = user_data[0][2]

    if user_password_hash == password:
        return {
            "status": "success", 
            "uid": user_uid, 
            "username": username, 
            "name": user_name
        }

    else:
        return {"status": "error", "code": "0001"}

def get_profile(uid):

    cur = DB.conn.cursor()
    cur.execute("SELECT uid, username, name, type FROM users WHERE uid = ?",(uid,))
    rows = cur.fetchall()

    if rows == []:
        return {
            "status": "error",
            "code": "0001"
        }

    else:
        return {
            "status": "success",
            "uid": rows[0][0],
            "username": rows[0][1],
            "name": rows[0][2],
            "type": rows[0][3]
        }

def get_profile_username(username):

    cur = DB.conn.cursor()
    cur.execute("SELECT uid, username, name, type FROM users WHERE username =?",(username,))
    rows = cur.fetchall()

    if rows == []:
        return {
            "status": "error",
            "code": "0001"
        }

    else:
        return {
            "status": "success",
            "uid": rows[0][0],
            "username": rows[0][1],
            "name": rows[0][2],
            "type": rows[0][3]
        }