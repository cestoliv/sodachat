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

"""ENVOYER UN MESSAGE"""
def send_message(sender_uid, receiver_uid, content):

    if content == "":
        return {
            "status": "error",
            "code": "0003"
        }

    date = datetime.datetime.now() #Date d'envoi du message : YYYY-MM-DD hh:mm:ss
    message_data = [uuid.uuid1().hex, date, sender_uid, receiver_uid, content, 0]  #uuid.uuid1().hex : id du message, type[str]

    cur = DB.conn.cursor()
    cur.execute("INSERT INTO messages(id, timestamp, sender_uid, receiver_uid, content, seen) values (?,?,?,?,?,?)", message_data)  #écrire le message dans la bdd
    DB.conn.commit()

    return {
        "status": "success",
        "id": message_data[0],
        "sender_uid": sender_uid,
        "receiver_uid": receiver_uid,
        "timestamp": str(date),
        "seen": 0
    }

"""LIRE LES MESSAGES"""
def get_messages(sender_uid, receiver_uid, limit, offset): #limit = nombre de messages à afficher; offset = point de départ; pour avoir les 10 derniers messages : limit = 10, offset = 0 ; pour avoir les messages 16 à 20 (en partant de la fin) : limit = 5, offset = 15

    cur = DB.conn.cursor()
    cur.execute('SELECT id, sender_uid, timestamp, content, seen FROM messages WHERE sender_uid = ? AND receiver_uid = ? OR sender_uid = ? AND receiver_uid = ? ORDER BY timestamp ASC LIMIT ? OFFSET ?',
         (sender_uid, receiver_uid, receiver_uid, sender_uid, str(limit), str(offset))
    ) #retrouver les messages dans la bdd

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
    }  #renvoi des messages

"""METTRE MESSAGES AU STATUT VU"""
def set_messages_seen(uid, message_ids):
    cur = DB.conn.cursor()

    message_ids = message_ids.split(",")

    for i in range(len(message_ids)):
        #print(message_ids[i])
        cur.execute("UPDATE messages SET seen=1 WHERE id = ? AND receiver_uid = ? ", (message_ids[i], uid))  #écrire le message dans la bdd
    DB.conn.commit()

    return {
        "status": "success"
    }