import sqlite3
import uuid
import datetime
import os
import sys
import inspect

# Import local modules
from db.db import DBConnection
from users import get_profile, get_profile_username

# Connection to database
DB = DBConnection()

####################
# INTERNAL FUNCTIONS
####################

def is_blocked(uid, contact_uid):
    """
    Checks if the given user has blocked the given contact

    Return a bool
    Return false if users aren't in contact
    """

    cur = DB.conn.cursor()
    cur.execute('SELECT blocked FROM contacts WHERE uid = ? AND contact_uid = ?',
        (
            uid,
            contact_uid
        )
    )
    blocked=cur.fetchall()

    if len(blocked) == 0:
        # aren't in contacts
        return False
    else:
        return blocked[0][0] == 1

def last_message(sender_uid, receiver_uid):
    """
    Retrieves the last message sent between two users

    Return a message object
    """

    cur = DB.conn.cursor()
    cur.execute('SELECT id, sender_uid, timestamp, content, seen FROM messages WHERE sender_uid = ? AND receiver_uid = ? OR sender_uid = ? AND receiver_uid = ? ORDER BY timestamp DESC LIMIT 1 OFFSET 0',
        (
            sender_uid,
            receiver_uid,
            receiver_uid,
            sender_uid
        )
    )

    message = cur.fetchall()
    if len(message) > 0:
        return {
            "id": message[0][0],
            "sender_uid": message[0][1],
            "timestamp": message[0][2],
            "content": message[0][3],
            "seen": message[0][4]
        }
    else:
        return {}

def in_contacts(uid_user1, uid_user2):
    """
    Checks if the two given users are in contact (that they have added each other)

    Return a boolean
    """

    # check that the first user is in contact with the second
    user1_with_user2 = False
    
    cur = DB.conn.cursor()
    cur.execute('SELECT contact_uid FROM contacts WHERE uid =?', (uid_user1,)) #prendre les uid de tous les contacts de l'utilisateur
    info_contacts_user1 = cur.fetchall()
    if len(info_contacts_user1) != 0:
        for i in range(len(info_contacts_user1)):
            if info_contacts_user1[i][0] == uid_user2:
                user1_with_user2 = True
    
    # check that the second user is in contact with the first
    user2_with_user1 = False

    cur = DB.conn.cursor()
    cur.execute('SELECT contact_uid FROM contacts WHERE uid =?', (uid_user2,)) #prendre les uid de tous les contacts de l'utilisateur
    info_contacts_user2 = cur.fetchall()
    if len(info_contacts_user2) != 0:
        for i in range(len(info_contacts_user2)):
            if info_contacts_user2[i][0] == uid_user1:
                user2_with_user1 = True
    
    return (user1_with_user2 and user2_with_user1)

###############
# API FONCTIONS
###############

def add_contact(uid, contact_username) :
    """
    Add a contact to the given uid from the username

    Error codes : 0001 => this contact does not exist
                  0002 => you are already in contacts
                  0003 => you can't add yourself as contact
    """

    contact_profile = get_profile_username(contact_username)
    if contact_profile["status"] == "error":
        # contact doesn't exist
        return {
            "status": "error",
            "code": "0001"
        }

    if contact_profile["uid"] == uid:
        # user and contact are the same person
        return {
            "status": "error",
            "code": "0003"
        }

    # Check that users are not already in contact
    user_contacts = get_contacts(uid)["contacts"]
    for i in range(len(user_contacts)):
        if user_contacts[i]["uid"] == contact_profile["uid"]:
            # already in contacts
            return {
                "status": "error",
                "code": "0002"
            }

    sending_date = datetime.datetime.now() # sending date : YYYY-MM-DD hh:mm:ss

    cur = DB.conn.cursor()
    cur.execute("INSERT INTO contacts(uid, timestamp, contact_uid, blocked) values (?,?,?,?)",
        (
            uid,
            sending_date,
            contact_profile["uid"],
            0
        )
    )
    DB.conn.commit()

    return {
        "status": "success",
        "uid": contact_profile["uid"],
        "username": contact_profile["username"],
        "name": contact_profile["name"]
    }

def get_contacts(uid):
    """
    Returns the list of contacts of the given user

    Error codes : no
    """

    cur = DB.conn.cursor()
    cur.execute('SELECT contact_uid, timestamp FROM contacts WHERE uid =?', (uid,)) #prendre les uid de tous les contacts de l'utilisateur

    contacts_infos = cur.fetchall()

    # get contacts detailed profile
    contacts_profile = [get_profile(contacts_infos[i][0]) for i in range(len(contacts_infos))]

    return {
        "status": "success",
        "contacts": [
            {
                "uid": contacts_profile[i]["uid"],
                "username": contacts_profile[i]["username"],
                "name": contacts_profile[i]["name"],
                "last_message": last_message(uid, contacts_profile[i]["uid"]),
                "blocked": is_blocked(uid, contacts_profile[i]["uid"]),
                "added_back": in_contacts(uid, contacts_profile[i]["uid"]),
                "timestamp": contacts_infos[i][1],
                "type": contacts_profile[i]["type"]
            } for i in range(0, len(contacts_profile))
        ]
    }

def delete_contact(uid, contact_uid) :
    """
    Removes the given contact from the user's contacts

    Error codes : 0001 => you are not in contact
    """

    # check that users are in contacts
    user_contacts = get_contacts(uid)["contacts"]
    for i in range(len(user_contacts)):
        if user_contacts[i]["uid"] == contact_uid:
            # user are in contacts
            return {
                "status": "error",
                "code": "0001"
            }
     
    cur = DB.conn.cursor()
    # delete from user contacts
    cur.execute('DELETE FROM contacts WHERE uid = ? AND contact_uid = ?', (
        uid,
        contact_uid
    ))
    # delete messages sended by user
    cur.execute('DELETE FROM messages WHERE sender_uid = ? AND receiver_uid = ?', (
        uid, 
        contact_uid
    ))
    # delete messages sended by contact
    cur.execute('DELETE FROM messages WHERE sender_uid = ? AND receiver_uid = ?', (
        contact_uid,
        uid
    ))
    DB.conn.commit()

    return {
        "status": "success"
    }

def block_contact(uid, contact_uid):
    """
    Blocks the given contact

    Error codes : 0001 => you are not in contact
                  0002 => you have blocked this contact
    """

    # check that users are in contacts
    user_contacts = get_contacts(uid)["contacts"]
    for i in range(len(user_contacts)):
        if user_contacts[i]["uid"] == contact_uid:
            # user are in contacts
            return {
                "status": "error",
                "code": "0001"
            }

    # check that the contact is not blocked
    if is_blocked(uid, contact_uid):
        return {
            "status": "error",
            "code": "0002"
        }

    cur = DB.conn.cursor()
    cur.execute('UPDATE contacts SET blocked = 1 WHERE uid = ? AND contact_uid = ?', (
        uid,
        contact_uid
    ))
    DB.conn.commit()

    return {
        "status": "success",
        "blocked": True
    }

def unblock_contact(uid, contact_uid):
    """
    Unblocks the given contact

    Error codes : 0001 => you are not in contact
                  0002 => you didn't block this contact
    """

    # check that users are in contacts
    user_contacts = get_contacts(uid)["contacts"]
    for i in range(len(user_contacts)):
        if user_contacts[i]["uid"] == contact_uid:
            # user are in contacts
            return {
                "status": "error",
                "code": "0001"
            }

    # check that the contact is not blocked
    if not is_blocked(uid, contact_uid):
        return {
            "status": "error",
            "code": "0002"
        }

    cur = DB.conn.cursor()
    cur.execute('UPDATE contacts SET blocked = 0 WHERE uid = ? AND contact_uid = ?', (
        uid,
        contact_uid
    ))
    DB.conn.commit()

    return {
        "status": "success",
        "blocked": False
    }