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
from fonctions.users import get_profile, get_profile_username

# Connection to database
DB = DBConnection()

"""AJOUTER UN CONTACT"""
def add_contact(uid, contact_username) :

    user = get_profile_username(contact_username)
    if user["status"] == "error" :
        return {
            "status": "error",
            "code": "0001"
        }

    # test user still in contacts
    user_contacts = get_contacts(uid)["contacts"]
    for i in range(len(user_contacts)):
        if user_contacts[i]["uid"] == user["uid"]:
            return {
                "status": "error",
                "code": "0002"
            }

    date = datetime.datetime.now() #Date d'envoi du message : YYYY-MM-DD hh:mm:ss
    t = [uid, date, user["uid"], 0]

    cur = DB.conn.cursor()
    cur.execute("INSERT INTO contacts(uid, timestamp, contact_uid, blocked) values (?,?,?,?)", t)  #ajouter le contact dans la bdd
    DB.conn.commit()

    return {
        "status": "success",
        "uid": user["uid"],
        "username": user["username"],
        "name": user["name"]
    } #message de succès

"""SAVOIR SI UN UTILISATEUR EST BLOQUE"""
def is_blocked(uid, contact_uid) :
    cur = DB.conn.cursor()
    cur.execute('SELECT blocked FROM contacts WHERE uid = "' + uid + '" AND contact_uid = "' + contact_uid + '"')
    blocked=cur.fetchall()
    if len(blocked) == 0:
        return False
    else:
        return blocked[0][0] == 1

"""DERNIER MESSAGE ENTRE DEUX UTILISATEUR"""
def last_message(sender_uid, receiver_uid):

    cur = DB.conn.cursor()
    cur.execute('SELECT id, sender_uid, timestamp, content, seen FROM messages WHERE sender_uid = "'
         + sender_uid + '" AND receiver_uid = "'
         + receiver_uid + '" OR sender_uid = "'
         + receiver_uid + '" AND receiver_uid = "'
         + sender_uid + '" ORDER BY timestamp DESC LIMIT 1 OFFSET 0') #retrouver les messages dans la bdd

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

"""SAVOIR SI 2 UTILISATEURS SONT EN CONTACTS"""
def in_contacts(uid_user1, uid_user2):

    user1_with_user2 = False
    
    cur = DB.conn.cursor()
    cur.execute('SELECT contact_uid FROM contacts WHERE uid =?', (uid_user1,)) #prendre les uid de tous les contacts de l'utilisateur
    info_contacts_user1 = cur.fetchall()
    if len(info_contacts_user1) != 0:
        for i in range(len(info_contacts_user1)):
            if info_contacts_user1[i][0] == uid_user2:
                user1_with_user2 = True
    
    user2_with_user1 = False

    cur = DB.conn.cursor()
    cur.execute('SELECT contact_uid FROM contacts WHERE uid =?', (uid_user2,)) #prendre les uid de tous les contacts de l'utilisateur
    info_contacts_user2 = cur.fetchall()
    if len(info_contacts_user2) != 0:
        for i in range(len(info_contacts_user2)):
            if info_contacts_user2[i][0] == uid_user1:
                user2_with_user1 = True
    
    return (user1_with_user2 and user2_with_user1)


"""INFO SUR LES CONTACTS D'UN UTILISATEUR"""
def get_contacts(uid):
    cur = DB.conn.cursor()
    cur.execute('SELECT contact_uid, timestamp FROM contacts WHERE uid =?', (uid,)) #prendre les uid de tous les contacts de l'utilisateur

    contacts_infos = cur.fetchall()

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

"""SUPPRIMER UN CONTACT"""
def delete_contact(uid, contact_uid) :

    # test user in contacts
    user_contacts = get_contacts(uid)["contacts"]
    user_in_contact = False
    for i in range(len(user_contacts)):
        if user_contacts[i]["uid"] == contact_uid:
            user_in_contact = True
    if not user_in_contact:
        return {
            "status": "error",
            "code": "0001"
        }


    cur = DB.conn.cursor()
    cur.execute('DELETE FROM contacts WHERE uid = "' + uid + '" AND contact_uid = "' + contact_uid + '"')
    DB.conn.commit()

    return {
        "status": "success"
    }

"""BLOQUER UN CONTACT"""
def block_contact(uid, contact_uid) :

    test_user_added_to_contacts = get_contacts(uid)
    i = 0
    user_in_contacts = False
    while i<len(test_user_added_to_contacts["contacts"]) and user_in_contacts == False:

        if test_user_added_to_contacts["contacts"][i]["uid"] == contact_uid :
            user_in_contacts = True

        else :
            i+=1

    if user_in_contacts == False :
        return {
            "status": "error",
            "code": "0001"
        }

    test_user_blocked = is_blocked(uid, contact_uid)
    if test_user_blocked == True :
        return {
            "status": "error",
            "code": "0002"
        }


    cur = DB.conn.cursor()
    cur.execute('UPDATE contacts SET blocked = 1 WHERE uid = "' + uid + '" AND contact_uid = "' + contact_uid + '"')
    DB.conn.commit()

    return {
        "status": "success",
        "blocked": True
        }

"""DEBLOQUER UN CONTACT"""
def unblock_contact(uid, contact_uid) :

    test_user_added_to_contacts = get_contacts(uid)
    i = 0
    user_in_contacts = False
    while i<len(test_user_added_to_contacts["contacts"]) and user_in_contacts == False:

        if test_user_added_to_contacts["contacts"][i]["uid"] == contact_uid :
            user_in_contacts = True

        else :
            i+=1

    if user_in_contacts == False :
        return {
            "status": "error",
            "code": "0001"
        }

    test_user_blocked = is_blocked(uid, contact_uid)
    if test_user_blocked == False :
        return {
            "status": "error",
            "code": "0002"
        }


    cur = DB.conn.cursor()
    cur.execute('UPDATE contacts SET blocked = 0 WHERE uid = "' + uid + '" AND contact_uid = "' + contact_uid + '"')
    DB.conn.commit()

    return {
        "status": "success",
        "blocked": False
        }