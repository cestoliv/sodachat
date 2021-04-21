from flask import Flask, render_template, safe_join, request, jsonify
from flask_restful import Resource, Api
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import jwt
import os
import sys
import inspect
import time
import threading
from bs4 import BeautifulSoup
import eventlet
eventlet.monkey_patch()

# Import local modules
from users import signup, signin, get_profile
from contacts import get_contacts, add_contact, delete_contact, block_contact, unblock_contact
from messages import get_messages, send_message, set_messages_seen
from bot.weather import bot as weather_bot

# chdir to current file dir
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
os.chdir(os.path.dirname(currentdir))

# set secret
JWT_SECRET = "secret"
APP_SECRET = "secret"

def decode_token(token):
    """
    Decode a JWT and check his data
    """
    # decode token
    token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

    # check profile of decoded data
    user_profile = get_profile(token['uid'])

    if user_profile['status'] == "error":
        # decoded user doesn't exist
        return {
            "status": "error",
            "code": "1315"
        }
    else :
        return user_profile

def encode_token(obj):
    """
    Encode the given object in a JWT
    """
    return jwt.encode(obj, JWT_SECRET, algorithm="HS256").decode("utf-8")

def bot_answer(message_data, bot_profile):
    """
    Ask an answer to a bot.
    Takes the message sended to the bot and the bot profile.
    """
    # remove html tags
    clean_content = BeautifulSoup(message_data["content"], "lxml").text

    # get bot return
    bot_return = "Sorry, I have nothing to say..."
    if bot_profile["username"] == "weather":
        bot_return = weather_bot(clean_content)

    # store bot return
    sended_message = send_message(
        bot_profile["uid"],
        message_data["sender_uid"],
        bot_return
    )

    # send bot return
    if sended_message["status"] == "success":
        bot_message_data = {
            "id": sended_message["id"],
            "sender_uid": sended_message["sender_uid"],
            "receiver_uid": sended_message["receiver_uid"],
            "timestamp": sended_message["timestamp"],
            "content": bot_return,
            "seen": sended_message["seen"],
        }

        # send socket
        time.sleep(0.5)
        socketio.emit("new_message", bot_message_data, room=message_data["sender_uid"])


# FLASK APP
app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = APP_SECRET
# create rest Api
api = Api(app, prefix="/api/v1")
# add socket.io
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# application page
@app.route("/app")
def app_page():
    return render_template("app.html")

# API ENDPOINTS :

########################################
### USERS
########################################

@socketio.on("register")
def add_new_client(data):
    # add new client in a room where they will be alone, named by their uid
    try:
        decoded_token = decode_token(data["jwt"])
        join_room(decoded_token["uid"])
    except Exception as e:
        print(e)

class Signup(Resource):
    """
    Description : Sign up a new user and return his jwt
    Endpoint    : /user/signup
    User input  : name :str, username :str, password :str
    Return      :   Success : {
                        "status": "success",
                        "uid": uid,
                        "username": username,
                        "name": name,
                        "jwt": json_web_token
                    }

                    Error : {
                        "status": "error",
                        "code": error_code
                    }
    Error codes : 0000 => unknown error
                  0001 => username already used
                  1314 => token invalid
                  1315 => the user does not exist
    """
    def post(self):
        try:
            # get signup return with user input
            signup_return = signup(
                request.form.get("name", ""),
                request.form.get("username", ""),
                request.form.get("password", "")
            )

            if signup_return["status"] == "success":
                signup_return["jwt"] = encode_token(signup_return)
            
            return jsonify(signup_return)
        except Exception as e:
            print(e)
            return {
                "status": "error",
                "code": "0000"
            }
api.add_resource(Signup, '/users/signup')

class Signin(Resource):
    """
    Description : Retrieve a user's jwt
    Endpoint    : /user/signin
    User input  : username :str, password :str
    Return      :   Success : {
                        "status": "success", 
                        "uid": uid, 
                        "username": username, 
                        "name": name,
                        "jwt": json_web_token
                    }

                    Error : {
                        "status": "error",
                        "code": error_code
                    }
    Error codes : 0000 => unknown error
                  0001 => invalid username
                  0001 => invalid password
                  1314 => token invalid
                  1315 => the user does not exist
    """
    def post(self):
        try:
            # get signin return with user input
            signin_return = signin(
                request.form.get("username", ""),
                request.form.get("password", "")
            )

            if signin_return["status"] == "success":
                signin_return["jwt"] = encode_token(signin_return)
            
            return jsonify(signin_return)
        except Exception as e:
            print(e)
            return {
                "status": "error",
                "code": "0000"
            }
api.add_resource(Signin, '/users/signin')

class CheckToken(Resource):
    """
    Description : Retrieve the profile of a user from his jwt, allow to check the validity of the jwt
    Endpoint    : /user/check-token
    User input  : token :str
    Return      :   Success : {
                        "status": "success",
                        "uid": uid,
                        "username": username,
                        "name": name,
                        "type": type,
                        "jwt": json_web_token
                    }

                    Error : {
                        "status": "error",
                        "code": error_code
                    }
    Error codes : 0000 => unknown error
                  1314 => token invalid
                  1315 => the user does not exist
    """
    def post(self):
        try:
            try:
                decoded_token = decode_token(request.form.get("token", ""))
            except Exception:
                return {
                    "status": "error",
                    "code": "1314"
                }

            decoded_token["jwt"] = request.form.get("token", "")

            return decoded_token
        except Exception as e:
            print(e)
            return {
                "status": "error",
                "code": "0000"
            }
api.add_resource(CheckToken, '/users/check-token')

########################################
### CONTACTS
########################################

class GetContacts(Resource):
    """
    Description : Recover the list of contacts of a user and their last message exchanged
    Endpoint    : /contacts/get
    User input  : token :str
    Return      :   Success : {
                        "status": "success",
                        "contacts": [
                            {
                                "uid": contact_uid,
                                "username": contact_username,
                                "name": contact_name,
                                "last_message": last_message_exchanged,
                                "blocked": is_blocked,
                                "added_back": added_you_back,
                                "timestamp": date_you_added_this_contact,
                                "type": type_of_user
                            },
                            ...
                        ]
                    }

                    Error : {
                        "status": "error",
                        "code": error_code
                    }
    Error codes : 0000 => unknown error
                  1314 => token invalid
                  1315 => the user does not exist
    """
    def post(self):
        try:
            # check token, go to except if the token is invalid
            try:
                decoded_token = decode_token(request.form.get("token", ""))
            except Exception:
                return {
                    "status": "error",
                    "code": "1314"
                }

            user_contacts = get_contacts(decoded_token["uid"])

            return user_contacts

        except Exception as e:
            print(e)
            return {
                "status": "error",
                "code": "0000"
            }
api.add_resource(GetContacts, '/contacts/get')

class AddContact(Resource):
    """
    Description : Add a contact from his username
    Endpoint    : /contacts/add
    User input  : token :str, contact_username :str
    Return      :   Success : {
                        "status": "success",
                        "uid": contact_uid,
                        "username": contact_username,
                        "name": contact_name
                    }

                    Error : {
                        "status": "error",
                        "code": error_code
                    }
    Error codes : 0000 => unknown error
                  0001 => this contact does not exist
                  0002 => you are already in contacts
                  0003 => you can't add yourself as contact
                  1314 => token invalid
                  1315 => the user does not exist
    """
    def post(self):
        try:
            # check token, go to except if the token is invalid
            try:
                decoded_token = decode_token(request.form.get("token", ""))
            except Exception:
                return {
                    "status": "error",
                    "code": "1314"
                }

            added_contact = add_contact(
                decoded_token["uid"],
                request.form.get("contact_username", "")
            )

            return added_contact

        except Exception as e:
            print(e)
            return {
                "status": "error",
                "code": "0000"
            }
api.add_resource(AddContact, '/contacts/add')

class DeleteContact(Resource):
    """
    Description : Delete a contact from his uid
    Endpoint    : /contacts/delete
    User input  : token :str, contact_uid :str
    Return      :   Success : {
                        "status": "success"
                    }

                    Error : {
                        "status": "error",
                        "code": error_code
                    }
    Error codes : 0000 => unknown error
                  0001 => you are not in contact
                  1314 => token invalid
                  1315 => the user does not exist
    """
    def post(self):
        try:
            # check token, go to except if the token is invalid
            try:
                decoded_token = decode_token(request.form.get("token", ""))
            except Exception:
                return {
                    "status": "error",
                    "code": "1314"
                }

            deleted_contact = delete_contact(
                decoded_token["uid"],
                request.form.get("contact_uid", "")
            )

            return deleted_contact

        except Exception as e:
            print(e)
            return {
                "status": "error",
                "code": "0000"
            }
api.add_resource(DeleteContact, '/contacts/delete')

class BlockContact(Resource):
    """
    Description : Block a contact from his uid
    Endpoint    : /contacts/block
    User input  : token :str, contact_uid :str
    Return      :   Success : {
                        "status": "success",
                        "blocked": True
                    }

                    Error : {
                        "status": "error",
                        "code": error_code
                    }
    Error codes : 0000 => unknown error
                  0001 => you are not in contact
                  0002 => you have blocked this contact
                  1314 => token invalid
                  1315 => the user does not exist
    """
    def post(self):
        try:
            # check token, go to except if the token is invalid
            try:
                decoded_token = decode_token(request.form.get("token", ""))
            except Exception:
                return {
                    "status": "error",
                    "code": "1314"
                }

            blocked_contact = block_contact(
                decoded_token["uid"],
                request.form.get("contact_uid", "")
            )

            return blocked_contact

        except Exception as e:
            print(e)
            return {
                "status": "error",
                "code": "0000"
            }
api.add_resource(BlockContact, '/contacts/block')

class UnblockContact(Resource):
    """
    Description : Unblock a contact from his uid
    Endpoint    : /contacts/unblock
    User input  : token :str, contact_uid:str
    Return      :   Success : {
                        "status": "success",
                        "blocked": False
                    }

                    Error : {
                        "status": "error",
                        "code": error_code
                    }
    Error codes : 0000 => unknown error
                  0001 => you are not in contact
                  0002 => you didn't block this contact
                  1314 => token invalid
                  1315 => the user does not exist
    """
    def post(self):
        try:
            # check token, go to except if the token is invalid
            try:
                decoded_token = decode_token(request.form.get("token", ""))
            except Exception:
                return {
                    "status": "error",
                    "code": "1314"
                }

            unblocked_contact = unblock_contact(
                decoded_token["uid"],
                request.form.get("contact_uid", "")
            )

            return unblocked_contact

        except Exception as e:
            print(e)
            return {
                "status": "error",
                "code": "0000"
            }
api.add_resource(UnblockContact, '/contacts/unblock')

########################################
### MESSAGES
########################################

class GetMessages(Resource):
    """
    Description : Retrieves the last 100 messages between the user and a contact
    Endpoint    : /messages/get
    User input  : token :str, receiver_uid :str
    Return      :   Success : {
                        "status": "success",
                        "messages": [
                            {
                                "id": message_id,
                                "sender_uid": sender_uid,
                                "receiver_uid": receiver_uid,
                                "timestamp": sending_date,
                                "content": message_content,
                                "seen": is_message_seen
                            },
                            ...
                        ]
                    }

                    Error : {
                        "status": "error",
                        "code": error_code
                    }
    Error codes : 0000 => unknown error
                  1314 => token invalid
                  1315 => the user does not exist
    """
    def post(self):
        try:
            # check token, go to except if the token is invalid
            try:
                decoded_token = decode_token(request.form.get("token", ""))
            except Exception:
                return {
                    "status": "error",
                    "code": "1314"
                }

            user_messages = get_messages(
                decoded_token["uid"],
                request.form.get("receiver_uid", ""),
                100,
                0
            )

            return user_messages

        except Exception as e:
            print(e)
            return {
                "status": "error",
                "code": "0000"
            }
api.add_resource(GetMessages, '/messages/get')

class SendMessages(Resource):
    """
    Description : Send a message to the given contact
    Endpoint    : /messages/send
    User input  : token :str, receiver_uid :str, content :str
    Return      :   Success : {
                        "status": "success",
                        "id": message_id,
                        "sender_uid": sender_uid,
                        "receiver_uid": receiver_uid,
                        "timestamp": sending_date,
                        "seen": 0
                    }

                    Error : {
                        "status": "error",
                        "code": error_code
                    }
    Error codes : 0000 => unknown error
                  0001 => this contact does not exist
                  0003 => the content cannot be empty
                  0004 => you have blocked this contact
                  0005 => you are not in contact
                  1314 => token invalid
                  1315 => the user does not exist
    """
    def post(self):
        try:
            # check token, go to except if the token is invalid
            try:
                decoded_token = decode_token(request.form.get("token", ""))
            except Exception:
                return {
                    "status": "error",
                    "code": "1314"
                }

            sended_message = send_message(
                decoded_token["uid"],
                request.form.get("receiver_uid", ""),
                request.form.get("content", "")
            )

            if sended_message["status"] == "success":
                message_data = {
                    "id": sended_message["id"],
                    "sender_uid": sended_message["sender_uid"],
                    "receiver_uid": sended_message["receiver_uid"],
                    "timestamp": sended_message["timestamp"],
                    "content": request.form.get("content", ""),
                    "seen": sended_message["seen"],
                }

                # send socket
                socketio.emit("new_message", message_data, room=request.form.get("receiver_uid", ""))
                socketio.emit("new_message", message_data, room=decoded_token["uid"])

                # check if user is a bot
                receiver_profile = get_profile(message_data["receiver_uid"])
                if receiver_profile["status"] == "success" and receiver_profile["type"] == "bot":
                    # ask bot to answer in a new thread
                    threading.Thread(target=bot_answer, args=(message_data, receiver_profile)).start()

            return sended_message

        except Exception as e:
            print(e)
            return {
                "status": "error",
                "code": "0000"
            }
api.add_resource(SendMessages, '/messages/send')

class SetMessagesSeen(Resource):
    """
    Description : Sets the given messages to seen status
    Endpoint    : /messages/seen
    User input  : token :str, message_ids :[str]
    Return      :   Success : {
                        "status": "success",
                        "seen_messages": [
                            {
                                "id": message_id,
                                "sender_uid": sender_uid
                            },
                            ...
                        ]
                    }

                    Error : {
                        "status": "error",
                        "code": error_code
                    }
    Error codes : 0000 => unknown error
                  1314 => token invalid
                  1315 => the user does not exist
    """
    def post(self):
        try:
            # check token, go to except if the token is invalid
            try:
                decoded_token = decode_token(request.form.get("token", ""))
            except Exception:
                return {
                    "status": "error",
                    "code": "1314"
                }

            seen_message = set_messages_seen(
                decoded_token["uid"],
                request.form.get("message_ids", ""))

            # send socket
            for message in seen_message["seen_messages"]:
                socketio.emit("message_seen", message["id"], room=message["sender_uid"])    

            return seen_message

        except Exception as e:
            print(e)
            return {
                "status": "error",
                "code": "0000"
            }
api.add_resource(SetMessagesSeen, '/messages/seen')

# run the application
if __name__ == "__main__":
    print("SODACHAT server running on port 8667")
    socketio.run(app, port=8667, host='0.0.0.0')
