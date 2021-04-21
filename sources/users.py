import sqlite3
import uuid
import datetime
import os
import sys
import inspect

# Import local modules
from db.db import DBConnection

# Connection to database
DB = DBConnection()

####################
# INTERNAL FUNCTIONS
####################

def get_profile(uid):
    """
    Returns the profile of a user from its uid

    Error codes : 0001 => user doesn't exist
    """

    cur = DB.conn.cursor()
    cur.execute("SELECT uid, username, name, type FROM users WHERE uid = ?", (uid,))
    rows = cur.fetchall()

    if rows == []:
        # user doesn't exist
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
    """
    Returns the profile of a user from his username

    Error codes : 0001 => user doesn't exist
    """

    cur = DB.conn.cursor()
    cur.execute("SELECT uid, username, name, type FROM users WHERE username =?", (username,))
    rows = cur.fetchall()

    if rows == []:
        # user doesn't exist
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

###############
# API FUNCTIONS
###############

def signup(name, username, password_hash):
    """
    Adds a user in the database with the given data
    
    Error codes : 0001 => username already used
    """

    cur = DB.conn.cursor()
    cur.execute("SELECT username FROM users WHERE username =?",(username,))
    DB.conn.commit()

    username_test = cur.fetchall()
    if username_test != []:
        # username is taken
        return {
            "status": "error",
            "code": "0001"
        }

    uid = uuid.uuid1().hex

    cur = DB.conn.cursor()
    cur.execute("INSERT INTO users(uid, name, username, password_hash, type) values (?,?,?,?,?)", (
        uid,
        name,
        username,
        password_hash,
        "user"
    ))
    DB.conn.commit()

    return {
        "status": "success",
        "uid": uid,
        "username": username,
        "name": name
    }

def signin(username, password):
    """
    Checks that the username and password are correct and returns the profile

    Error codes : 0001 => invalid username
                  0002 => invalid password
    """

    cur = DB.conn.cursor()
    cur.execute("SELECT uid, name, password_hash FROM users WHERE username =?", (username,))
    user_data = cur.fetchall()
    if user_data == [] :
        # user doesn't exist
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
        return {
            "status": "error", 
            "code": "0002"
        }