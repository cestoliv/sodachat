import sqlite3
import uuid
import datetime
import os
import sys
import inspect

# Import local modules
from db.db import DBConnection
from users import get_profile
from contacts import is_blocked, in_contacts

# Connection to database
DB = DBConnection()

###############
# API FUNCTIONS
###############

def send_message(sender_uid, receiver_uid, content):
    """
    Send a message to the given user

    Error codes : 0001 => this contact does not exist
                  0003 => the content cannot be empty
                  0004 => you have blocked this contact
                  0005 => you are not in contact
    """

    # check that receiver exist and get it
    receiver_profile = get_profile(receiver_uid)
    if receiver_profile["status"] == "error" :
        return {
            "status": "error",
            "code": "0001"
        }

    # check that content isn't empty
    if content == "":
        return {
            "status": "error",
            "code": "0003"
        }
    
    # check that receiver aren't blocked
    if is_blocked(receiver_uid, sender_uid) == True :
        return {
            "status": "error",
            "code": "0004"
        }

    # check that users are in contacts
    if in_contacts(sender_uid, receiver_uid) == False :
        if receiver_profile['type'] != "bot":
            # send a message to a bot
            sender_profile = get_profile(sender_uid) # sender must exist
            if sender_profile["type"] != "bot":
                return {
                    "status": "error",
                    "code": "0005"
                }

    sending_date = datetime.datetime.now() #Date d'envoi du message : YYYY-MM-DD hh:mm:ss
    message_id = uuid.uuid1().hex

    cur = DB.conn.cursor()
    cur.execute("INSERT INTO messages(id, timestamp, sender_uid, receiver_uid, content, seen) values (?,?,?,?,?,?)", (
        message_id,
        sending_date,
        sender_uid,
        receiver_uid,
        content,
        0
    ))
    DB.conn.commit()

    return {
        "status": "success",
        "id": message_id,
        "sender_uid": sender_uid,
        "receiver_uid": receiver_uid,
        "timestamp": str(sending_date),
        "seen": 0
    }

def get_messages(sender_uid, receiver_uid, limit, offset): #limit = nombre de messages à afficher; offset = point de départ; pour avoir les 10 derniers messages : limit = 10, offset = 0 ; pour avoir les messages 16 à 20 (en partant de la fin) : limit = 5, offset = 15
    """
    Recover a conversation between two users

    limit is the limit of the message to be displayed
    offset is the starting index (e.g. 0 for the first, 10 to cut the first 10)
    """

    cur = DB.conn.cursor()
    cur.execute('SELECT id, sender_uid, timestamp, content, seen FROM messages WHERE sender_uid = ? AND receiver_uid = ? OR sender_uid = ? AND receiver_uid = ? ORDER BY timestamp ASC LIMIT ? OFFSET ?',
        (
            sender_uid, 
            receiver_uid, 
            receiver_uid, 
            sender_uid, 
            str(limit), 
            str(offset)
        )
    )

    rows = cur.fetchall()

    return {
        "status": "success",
        "messages": [
            {
                "id": rows[i][0],
                "sender_uid": rows[i][1],
                "receiver_uid": receiver_uid,
                "timestamp": rows[i][2],
                "content": rows[i][3],
                "seen": rows[i][4]
            } for i in range(len(rows))
        ]
    }

def set_messages_seen(uid, message_ids):
    """
    Sets the given messages to seen status

    Take an array of messages ids
    """

    cur = DB.conn.cursor()

    message_ids = message_ids.split(",")

    seen_messages = []

    for i in range(len(message_ids)):
        cur.execute("UPDATE messages SET seen=1 WHERE id = ? AND receiver_uid = ? ", (message_ids[i], uid)) # set message has read
        cur.execute("SELECT sender_uid FROM messages WHERE id = ?", (message_ids[i],)) # retrieve sender_uid to notify him

        seen_messages.append({
            "id": message_ids[i],
            "sender_uid": cur.fetchall()[0][0] # because [('uid',)]
        })

    DB.conn.commit()

    return {
        "status": "success",
        "seen_messages": seen_messages
    }