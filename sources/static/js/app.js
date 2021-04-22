var user = {}

var app = document.getElementById("app")

// connect to socket with automatic reconnection
var socket = io({
    reconnection: true,
    reconnectionDelay: 500,
    reconnectionDelayMax : 5000,
    reconnectionAttempts: Infinity
})

var first_connection = true
socket.on('connect', () => {
	console.log("connected to socket")
	if(user) {
		socket.emit('register', {jwt: user.jwt})
	}
	// Don't show message on first connection
	if(!first_connection) {
		error.change_content("Re-connected !")
		error.show()
	}
	first_connection = false
})

socket.on('disconnect', () => {
	console.log("disconnected from the socket")
	error.change_content("Disconnected... Trying to re-connect...")
	error.show()
})

date_to_relative_date = (u_date) => {
	/*
	Take a date object and transform it to relative date
	*/
    u_date = new Date(u_date)
    let formatter = new Intl.RelativeTimeFormat(undefined, {
        localeMatcher: "best fit",
        numeric: "always",
        style: "long",
    })

    let divisions = [
        { amount: 60, name: 'seconds' },
        { amount: 60, name: 'minutes' },
        { amount: 24, name: 'hours' },
        { amount: 7, name: 'days' },
        { amount: 4.34524, name: 'weeks' },
        { amount: 12, name: 'months' },
        { amount: Number.POSITIVE_INFINITY, name: 'years' }
    ]
      
    let duration = (u_date - new Date()) / 1000
        
    for (i = 0; i <= divisions.length-1; i++) {
        let division = divisions[i]
        if (Math.abs(duration) < division.amount) {
            return `${formatter.format(Math.round(duration), division.name)}`
        }
        duration /= division.amount
    }

    return "Invalid Date"
}

var confirmation, contacts, messages, messages_placeholder, sign, error, add_contacts

show = (what) => {
	/*
	Show the given panel and hide the others

	Available panels :
	- sign
	- messages_placeholder
	- messages
	- add_contacts
	*/
	app.classList.remove("sign")
	app.classList.remove("messages_placeholder")
	app.classList.remove("add_contacts")
	app.classList.remove("messages")

	contacts.hide()
	add_contacts.hide()
	messages.hide()
	messages_placeholder.hide()
	sign.hide()

	switch(what) {
		case 'sign':
			app.classList.add("sign")
			sign.show()
			break
		case 'messages_placeholder':
			app.classList.add("messages_placeholder")
			contacts.show()
			messages_placeholder.show()
			break
		case 'messages':
			app.classList.add("messages")
			contacts.show()
			messages.show()
			break
		case 'add_contacts':
			app.classList.add("add_contacts")
			add_contacts.show()
			break
	}
}

/* A confirmation popup, work with it's ask_confirmation function */
confirmation = new Vue({
    el: '#confirmation',
    data: {
        showed: false,
        text: "",
        OK_loading: false,
        OK_text: "OK",
        CANCEL_text: "CANCEL",

        callback: console.log,
    },
    methods: {
        ask_confirmation(n_text, n_callback) {
			/* take the text to display and the callback function */
			/* callback must be a promise */
            this.text = n_text
            this.callback = n_callback
            this.showed = true
        },
        ok() {
            if(this.showed) {
                this.OK_loading = true

				/* execute callback */
                this.callback.call().then(() => {
					/* hide popup */
                    this.showed = false
                    this.text = ""
                })
				.catch((err) => {
					console.log(err)
				})
				.finally(() => {
					/* stpo loading animation */
                    this.OK_loading = false
                })
            }
        },
        cancel() {
            if(this.showed) {
				/* hide popup */
                this.showed = false
                this.text = ""
            }
        }
    }
})

/* contacts panel */
contacts = new Vue({
    el: '#contacts',
    data: {
		showed: false,
		loaded: false,

        contacts: []
    },
	mounted: () => {
		setInterval(() => {
			contacts.reorder_contacts()
		}, 20000) // reorder_contacts every 20secs
	},
    methods: {
		show() {
			this.showed = true
		},
		hide() {
			this.showed = false
		},
		show_messages(contact) {
			// set as seen in contacts list
            contact.last_message.seen = 1

			messages.load(contact)

			show("messages")
		},
		add_contact(contact) {
			if(contact["blocked"]) {
				return
			}

			// remove html tags of last_message content
			if(contact["last_message"]["content"] != undefined) {
				contact["last_message"]["content"] = contact["last_message"]["content"].replace( /(<([^>]+)>)/ig, '')
			}

			this.contacts.push(contact)
			this.reorder_contacts()
		},
		remove_contact(contact_uid) {
			for(i in this.contacts) {
				if(this.contacts[i].uid == contact_uid) {
					this.contacts.splice(i, 1)
				}
			}
			this.reorder_contacts()
		},
		change_last_message_of_uid(message) {
			message = {...message} // spread to "unlink"
			// remove html tags of last_message content
			if(message.content != undefined) {
				message.content = message.content.replace( /(<([^>]+)>)/ig, '')
			}

			for(i_contact in this.contacts) {
				if(this.contacts[i_contact].uid == message.sender_uid ||
					this.contacts[i_contact].uid == message.receiver_uid) {
					this.contacts[i_contact].last_message = message
				}
			}

			this.reorder_contacts()
		},
		set_contacts(contacts) {
			this.contacts = []
			for(i_contacts in contacts) {
				this.add_contact(contacts[i_contacts])
			}
		},
		reorder_contacts() {
			/* reorder contacts by last message date */
			contacts.set_contacts(
				contacts.contacts.sort((a, b) => {
					// default timestamp is the adding in contacts date
					let a_timestamp = a.timestamp
					let b_timestamp = b.timestamp
					
					// if available, timestamp became the last message sending date
					if(a.last_message.content) {
						a_timestamp = a.last_message.timestamp
					}
					if(b.last_message.content) {
						b_timestamp = b.last_message.timestamp
					}
					
					return new Date(b_timestamp) - new Date(a_timestamp)
				})
			)
		},
		load() {
			this.contacts = []
			this.loaded = false

			var formData = new FormData()
			formData.append("token", user.jwt)

			axios.post("/api/v1/contacts/get", formData).then((response) => {
				if(response["data"]["status"] == "success") {
					this.set_contacts(response["data"]["contacts"])
					this.loaded = true
				}
				else {
					error.change_content("An unexpected error occurred")
					error.show()
					this.loaded = false
				}
				this.sign_loading = false
			}).catch((err) => {
				console.error(err)
				error.change_content("An unexpected error occurred")
				error.show()
				this.loaded = false
			})
		},
		logout() {
			sign.logout()
		},
		add_contacts() {
			show("add_contacts")
		}
    }
})

/* messages panel */
messages = new Vue({
    el: '#messages',
    data: {
		showed: false,

		messages_loading: true,
		is_sending: false,

		contact: {},

        messages: []
    },
	mounted: () => {
		setInterval(() => {
			messages.refresh_dates()
		}, 10000) // refresh date every 10secs
		setInterval(() => {
			messages.reorder_messages()
		}, 20000) // reorder_messages every 20secs
	},
    methods: {
		show() {
			this.showed = true
		},
		hide() {
			this.showed = false
		},
		hide_messages() {
			/* return to the "no selected conversation" page */
			show("messages_placeholder")
		},
		toggle_message_date(message) {
			/* show or hide message sending date */
			if(message.show_date) {
				message.show_date = false
			}
			else {
				message.show_date = true
			}
		},
		set_contact(contact) {
			/* change conversation */
			this.contact = contact
			this.messages = []
		},
		set_messages(messages) {
			this.messages = []
			for(messages_i in messages) {
				this.add_message(messages[messages_i])
			}
		},
		add_message(message) {
			message = {...message} // spread to "unlink"
			// check if there's not still the message
			for(i_message in this.messages) {
				if(this.messages[i_message]["id"] == message.id) {
					return
				}
			}

			message["date_string"] = date_to_relative_date(message["timestamp"])
			message["sender"] = "contact"
			if(message["sender_uid"] == user.uid) {
				message["sender"] = "me"
			}
			message["show_date"] = false // show only on click
			
            this.messages.push(message)

			Vue.nextTick(() => {
				this.scroll_to_last_message()
			})

			// set message has seen
			if(message["seen"] == 0 && message["sender_uid"] != user.uid) {
				var formData = new FormData()
				formData.append("token", user.jwt)
				formData.append("message_ids", message["id"])

				axios.post("/api/v1/messages/seen", formData).then((response) => {
					if(response["data"]["status"] == "success") {
						message.seen = 1
					}
					else {
						if(response["data"]["code"] == "0001") {
							error.change_content("This message is not for you")
						}
						else {
							error.change_content("An unexpected error occurred")
						}
						error.show()
					}
				}).catch((err) => {
					console.error(err)
					error.change_content("An unexpected error occurred")
					error.show()
				})
			}
		},
		set_message_as_seen(message_id) {
			/* set as seen, only locally */
			/* message ar setted as seen in the add_message */
			for(messages_i in this.messages) {
				if(this.messages[messages_i]["id"] == message_id) {
					this.messages[messages_i]["seen"] = 1
				}
			}
		},
		refresh_dates() {
			/* refresh relative date display */
			for(messages_i in this.messages) {
				this.messages[messages_i]["date_string"] = date_to_relative_date(this.messages[messages_i].timestamp)
			}
		},
		reorder_messages() {
			/* reorder messages by date (to correct network error) */
			this.set_messages(
				messages.messages.sort((a, b) => {
					return new Date(a.timestamp) - new Date(b.timestamp)
				})
			)
		},
		send_message() {
			message_editor.focus()
			if(message_editor.getData() == "") {
				/* don't send if message is empty */
				return
			}
			if(this.is_sending) {
				/* don't send if there is already a message that is being send */
				return
			}

			var formData = new FormData()
			formData.append("token", user.jwt)
			formData.append("receiver_uid", this.contact.uid)
			formData.append("content", message_editor.getData())

			/* don't allow user to edit while message are sending */
			message_editor.isReadOnly = true
			this.is_sending = true

			/* send message to api */
			axios.post("/api/v1/messages/send", formData).then((response) => {
				if(response["data"]["status"] == "success") {
					/* construct message object to display it */
					message_data = {
						"id": response["data"]["id"],
						"sender_uid": response["data"]["sender_uid"],
						"receiver_uid": response["data"]["receiver_uid"],
						"timestamp": response["data"]["timestamp"],
						"content": message_editor.getData(),
						"seen": response["data"]["seen"],
					}

					/* add message to message list */
					this.add_message(message_data)

					/* add message to contact panel */
					contacts.change_last_message_of_uid(message_data)

					/* empty message input */
					message_editor.setData("")
				}
				else {
					if(response["data"]["code"] == "0001") {
						error.change_content("This person is not one of your contacts")
					}
					else if(response["data"]["code"] == "0004") {
						error.change_content("This person blocked you")
					}
					else if(response["data"]["code"] == "0005") {
						error.change_content("This person has not accepted you as a friend")
					}
					else {
						error.change_content("An unexpected error occurred")
					}
					error.show()
				}

				/* re-allow user to edit (input is cleared on success only) */
				message_editor.isReadOnly = false
				this.is_sending = false
			}).catch((err) => {
				console.error(err)
				error.change_content("An unexpected error occurred")
				error.show()
				/* re-allow user to edit (input is cleared on success only) */
				message_editor.isReadOnly = false
				this.is_sending = false
			})
		},
		scroll_to_last_message() {
			if(document.getElementById("messages_list").children.length > 0) {
				document.getElementById("messages_list").lastChild.scrollIntoView({behavior: 'smooth'})
			}
		},
		load(contact) {
			/* get last 100 messages of the conversation */
			this.contact = contact
			if(this.contact == {}) {
				return
			}

			/* show a loading animation */
			this.messages_loading = true

			var formData = new FormData()
			formData.append("token", user.jwt)
			formData.append("receiver_uid", this.contact.uid)

			/* retrieve from api */
			axios.post("/api/v1/messages/get", formData).then((response) => {
				if(response["data"]["status"] == "success") {
					/* display messages */
					this.set_messages(response["data"]["messages"])
					show("messages")
				}
				else {
					error.change_content("An unexpected error occurred")
					error.show()
					/* empty the current contact and messages */
					this.contact = {}
					this.messages = []
				}
				/* hide loading animation */
				this.messages_loading = false
			}).catch((err) => {
				console.error(err)
				error.change_content("An unexpected error occurred")
				error.show()
				/* hide loading animation */
				this.messages_loading = false
				/* empty the current contact and messages */
				this.contact = {}
				this.messages = []
			})
		},
        action_block_contact() {
			/* block a contact */
			/* return a promise because it will be launched by the confirmation popup */
            return new Promise((resolve, reject) => {
				let contact_uid = this.contact.uid
                var formData = new FormData()
			    formData.append("token", user.jwt)
			    formData.append("contact_uid", contact_uid)

				/* send to api */
			    axios.post("/api/v1/contacts/block", formData).then((response) => {
				    if(response["data"]["status"] == "success") {
						/* return to the "no conversation selected" panel*/
						show("messages_placeholder")
						/* remove contact from contact panel */
						contacts.remove_contact(contact_uid)
						/* empty the current contact and messages */
						this.contact = {}
						this.messages = []
                        resolve()
                    }
				    else {
					    error.change_content("An unexpected error occurred")
					    error.show()
                        reject()
				    }
			    }).catch((err) => {
				    console.error(err)
				    error.change_content("An unexpected error occurred")
				    error.show()
                    reject()
			    })
            })
        },
        confirm_action_block_contact() {
			/* show the confirmation popup */
            confirmation.ask_confirmation("Would you really like to block <strong>" + this.contact.name + "</strong>?", this.action_block_contact)
        },
		action_delete_contact() {
			/* delete a contact */
			/* return a promise because it will be launched by the confirmation popup */
            return new Promise((resolve, reject) => {
				let contact_uid = this.contact.uid
                var formData = new FormData()
			    formData.append("token", user.jwt)
			    formData.append("contact_uid", contact_uid)

				/* send to api */
			    axios.post("/api/v1/contacts/delete", formData).then((response) => {
				    if(response["data"]["status"] == "success") {
						/* return to the "no conversation selected" panel*/
						show("messages_placeholder")
						/* remove contact from contact panel */
						contacts.remove_contact(contact_uid)
						/* empty the current contact and messages */
						this.contact = {}
						this.messages = []
                        resolve()
                    }
				    else {
					    error.change_content("An unexpected error occurred")
					    error.show()
                        reject()
				    }
			    }).catch((err) => {
				    console.error(err)
				    error.change_content("An unexpected error occurred")
				    error.show()
                    reject()
			    })
            })
        },
        confirm_action_delete_contact() {
			/* show the confirmation popup */
            confirmation.ask_confirmation("Do you really want to remove <strong>" + this.contact.name + "</strong> from your friends?", this.action_delete_contact)
        }
    }
})

messages_placeholder = new Vue({
    el: '#messages_placeholder',
    data: {
		showed: false,
    },
    methods: {
		show() {
			/* empty the messages panel selected conversation (normally, it's already done) */
			messages.contact = {}
			messages.messages = []
			this.showed = true
		},
		hide() {
			this.showed = false
		}
    }
})

sign = new Vue({
    el: '#sign',
    data: {
		showed: false,
		sign_loading: false,
		signup: false,

		name_input: "",
		username_input: "",
		password_input: ""
	},
	mounted() {
		/* configure cookie */
		this.$cookies.config('30d','','',false) // expire, path, domain, secure

		/* if there's no "user" cookie */
		if(!this.$cookies.get('user') || this.$cookies.get('user') == undefined) {
			this.show()
			return
		}

		var formData = new FormData()
		formData.append("token", this.$cookies.get('user').jwt)

		/* check cookie stored token with api */
		axios.post("/api/v1/users/check-token", formData).then((response) => {
			if(response["data"]["status"] == "success") {
				/* store the user profile */
				user = response["data"]

				/* tell the socket that we are here */
				socket.emit('register', {jwt: user.jwt})
				/* show the "no conversation selected" panel */
				show("messages_placeholder")
				
				/* start loading the user's contacts in contacts panel */
				contacts.load()
			}
			else {
				/* token is invalid */
				/* remove everything and show sign panel */
				user = {}
				this.$cookies.remove('user')
				show("sign")
			}
		}).catch((err) => {
			this.show()
			console.error(err)
			error.change_content("An unexpected error occurred")
			error.show()
		})
	},
    methods: {
		show() {
			this.showed = true
		},
		hide() {
			this.showed = false
		},
		set_up() {
			/* change to signup */
			this.signup = true
		},
		set_in() {
			/* change to signin */
			this.signup = false
		},
		sign() {
			/* show loading animation */
			this.sign_loading = true
			if(this.signup) { /* on signup */
				var formData = new FormData()
				formData.append("name", this.name_input)
				formData.append("username", this.username_input)
				formData.append("password", this.password_input)

				/* send to api */
				axios.post("/api/v1/users/signup", formData).then((response) => {
					if(response["data"]["status"] == "success") {
						/* store user profile */
						user = response["data"]

						/* store user in cookies */
						this.$cookies.set('user', user)
						/* tell the socket that we are here */
						socket.emit('register', {jwt: user.jwt})
						
						/* empty inputs */
						this.name_input = ""
						this.username_input = ""
						this.password_input = ""
						/* show the "no conversation selected" panel */
						show("messages_placeholder")
						/* start loading the user's contacts in contacts panel */
						contacts.load()
					}
					else {
						if(response["data"]["code"] == "0001") {
							error.change_content("This username is already assigned")
						}
						else {
							error.change_content("An unexpected error occurred")
						}

						error.show()
					}
					/* hide loading animation */
					this.sign_loading = false
				}).catch((err) => {
					console.error(err)
					error.change_content("An unexpected error occurred")
					error.show()
					/* hide loading animation */
					this.sign_loading = false
				})
			}
			else { /* on signin */
				var formData = new FormData()
				formData.append("username", this.username_input)
				formData.append("password", this.password_input)

				/* send to api */
				axios.post("/api/v1/users/signin", formData).then((response) => {
					if(response["data"]["status"] == "success") {
						/* store user profile */
						user = response["data"]

						/* store user in cookies */
						this.$cookies.set('user', user)
						/* tell the socket that we are here */
						socket.emit('register', {jwt: user.jwt})
						
						/* empty inputs */
						this.name_input = ""
						this.username_input = ""
						this.password_input = ""
						/* show the "no conversation selected" panel */
						show("messages_placeholder")
						/* start loading the user's contacts in contacts panel */
						contacts.load()
					}
					else {
						if(response["data"]["code"] == "0001") {
							error.change_content("One of your login is incorrect")
						}
						else {
							error.change_content("An unexpected error occurred")
						}

						error.show()
					}
					/* hide loading animation */
					this.sign_loading = false
				}).catch((err) => {
					console.error(err)
					error.change_content("An unexpected error occurred")
					error.show()
					/* hide loading animation */
					this.sign_loading = false
				})
			}
		},
		logout() {
			/* set signin */
			this.set_in()
			/* empty local user profile */
			user = {}
			/* remove user cookie */
			this.$cookies.remove('user')
			/* show sign panel */
			show("sign")
		}
    }
})

add_contacts = new Vue({
    el: '#add_contacts',
    data: {
		showed: false,
		add_contact_loading: false,
		username_input_enabled: true,
		request_send_message_showed: false,

		username_input: ""
	},
	mounted() {
	},
    methods: {
		show() {
			this.showed = true
		},
		hide() {
			this.showed = false
		},
		show_messages() {
			/* load user contacts in contact panel */
			contacts.load()
			/* show the "no conversation selected" panel */
			show("messages_placeholder")
		},
		add_contact() {
			/* show loading animation */
			this.add_contact_loading = true
			/* disable input edition */
			this.username_input_enabled = false
			/* hide the "sent" message */
			this.request_send_message_showed = false
			
			var formData = new FormData()
			formData.append("token", user.jwt)
			formData.append("contact_username", this.username_input)

			/* send to api */
			axios.post("/api/v1/contacts/add", formData).then((response) => {
				if(response["data"]["status"] == "success") {
					/* empty input */
					this.username_input = ""
					/* show "sent" message */
					this.request_send_message_showed = true

					setTimeout(() => {
						/* hide "sent" message after 3sec */
						this.request_send_message_showed = false
					}, 3000)
				}
				else {
					if(response["data"]["code"] == "0001") {
						error.change_content("No one has this name here...")
					}
					else if(response["data"]["code"] == "0002") {
						error.change_content(this.username_input + " is already your friend")
					}
					else if(response["data"]["code"] == "0003") {
						error.change_content("You can't add yourself as a friend")
					}
					else {
						error.change_content("An unexpected error occurred")
					}

					error.show()
				}
				/* hide loading animation */
				this.add_contact_loading = false
				/* re-enable input edition */
				this.username_input_enabled = true
			}).catch((err) => {
				console.error(err)
				error.change_content("An unexpected error occurred")
				error.show()
				/* hide loading animation */
				this.add_contact_loading = false
				/* re-enable input edition */
				this.username_input_enabled = true
			})
		}
    }
})

/* error popup */
error = new Vue({
    el: '#error',
    data: {
		showed: false,

		content: ""
    },
    methods: {
		show() {
			this.showed = true
			setTimeout(() => {
				/* hide error popup after 5sec */
				this.hide()
			}, 5000)
		},
		hide() {
			this.showed = false
		},
		change_content(content) {
			this.hide()
			/* set new text */
			this.content = content
		}
    }
})

socket.on('new_message', (message) => {
	/* on new message received */

	/* if the received message are from the current conversation */
	if(message["sender_uid"] == messages.contact.uid || message["receiver_uid"] == messages.contact.uid) {
		/* add to message list */
		messages.add_message(message)

		// set temporarly as seen in contacts list (only if it's the current conversation)
		message.seen = 1
	}

	/* add to contacts panel */
	/* if it's from the current contact, it is set as seen by the previous line */
	contacts.change_last_message_of_uid(message)
})

socket.on('message_seen', (message_id) => {
	/* on contact seen a user message */
	/* mark as seen in messages list */
	messages.set_message_as_seen(message_id)
})
