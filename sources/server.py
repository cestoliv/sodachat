from flask import Flask, render_template, safe_join, request, jsonify
from flask_restful import Resource, Api
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import jwt
import os
import sys
import inspect
import eventlet
eventlet.monkey_patch()

from fonctions.users import signup, signin
from fonctions.contacts import get_contacts, add_contact, delete_contact, block_contact, unblock_contact
from fonctions.messages import get_messages, send_message, set_messages_seen

# chdir to current file dir
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
os.chdir(os.path.dirname(currentdir))

JWT_SECRET = "secret"
APP_SECRET = "secret"

def decode_token(token):
    # TODO: vérifier dans la db
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
def encode_token(obj):
    return jwt.encode(obj, JWT_SECRET, algorithm="HS256").decode("utf-8")

# creates a Flask application, named app
app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = APP_SECRET
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
api = Api(app, prefix="/api/v1")

@app.route("/app")
def hello():
    return render_template("app.html")

########################################
### USERS
########################################

@socketio.on("register")
def add_new_client(data):
    try:
        decoded_token = decode_token(data["jwt"])

        join_room(decoded_token["uid"])
    except Exception as e:
        print(e)

class Signup(Resource):
    def post(self):
        try:
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

class Signin(Resource):
    def post(self):
        try:
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

class CheckToken(Resource):
    def post(self):
        try:
            decoded_token = decode_token(
                request.form.get("token", ""))

            user_data = decoded_token

            user_data["jwt"] = request.form.get("token", "")

            return user_data
        except Exception as e:
            #print(e)
            return {
                "status": "error",
                "code": "0000"
            }

api.add_resource(Signup, '/users/signup')
api.add_resource(Signin, '/users/signin')
api.add_resource(CheckToken, '/users/check-token')

########################################
### CONTACTS
########################################

class GetContacts(Resource):
    def post(self):
        try:
            decoded_token = decode_token(
                request.form.get("token", ""))

            # Token verified
            user_contacts = get_contacts(decoded_token["uid"])

            return user_contacts

        except Exception as e:
            print(e)
            return {
                "status": "error",
                "code": "0000"
            }

class AddContact(Resource):
    def post(self):
        try:
            decoded_token = decode_token(
                request.form.get("token", ""))

            # Token verified
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

class DeleteContact(Resource):
    def post(self):
        try:
            decoded_token = decode_token(
                request.form.get("token", ""))

            # Token verified
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

class BlockContact(Resource):
    def post(self):
        try:
            decoded_token = decode_token(
                request.form.get("token", ""))

            # Token verified
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

class UnblockContact(Resource):
    def post(self):
        try:
            decoded_token = decode_token(
                request.form.get("token", ""))

            # Token verified
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

api.add_resource(GetContacts, '/contacts/get')
api.add_resource(AddContact, '/contacts/add')
api.add_resource(DeleteContact, '/contacts/delete')
api.add_resource(BlockContact, '/contacts/block')
api.add_resource(UnblockContact, '/contacts/unblock')

########################################
### MESSAGES
########################################

class GetMessages(Resource):
    def post(self):
        try:
            decoded_token = decode_token(
                request.form.get("token", "")
            )

            # Token verified
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

class SendMessages(Resource):
    def post(self):
        try:
            decoded_token = decode_token(
                request.form.get("token", "")
            )

            # Token verified
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
                socketio.emit("new_message", message_data, room=request.form.get("receiver_uid", ""))
                socketio.emit("new_message", message_data, room=decoded_token["uid"])

            return sended_message

        except Exception as e:
            print(e)
            return {
                "status": "error",
                "code": "0000"
            }

class SetMessagesSeen(Resource):
    def post(self):
        try:
            decoded_token = decode_token(
                request.form.get("token", "")
            )

            # Token verified
            seen_message = set_messages_seen(
                decoded_token["uid"],
                request.form.get("message_ids", ""))

            return seen_message

        except Exception as e:
            print(e)
            return {
                "status": "error",
                "code": "0000"
            }

api.add_resource(GetMessages, '/messages/get')
api.add_resource(SendMessages, '/messages/send')
api.add_resource(SetMessagesSeen, '/messages/seen')

# run the application
if __name__ == "__main__":
    #app.run(debug=True)
    socketio.run(app, port=8667, host='0.0.0.0')
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=8667)