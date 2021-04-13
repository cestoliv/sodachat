var user = {}

var app = document.getElementById("app")

var socket = io()

socket.on('connect', () => {
	console.log("connected to socket")
})

date_to_relative_date = (u_date) => {
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
            this.text = n_text
            this.callback = n_callback
            this.showed = true
        },
        ok() {
            if(this.showed) {
                this.OK_loading = true

                this.callback.call().then(() => {
                    this.showed = false
                    this.text = ""
                })
				.catch((err) => {
					console.log(err)
				})
				.finally(() => {
                    this.OK_loading = false
                })
            }
        },
        cancel() {
            if(this.showed) {
                this.showed = false
                this.text = ""
            }
        }
    }
})

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
		},
		remove_contact(contact_uid) {
			for(i in this.contacts) {
				if(this.contacts[i].uid == contact_uid) {
					this.contacts.splice(i, 1)
				}
			}
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
			contacts.set_contacts(
				contacts.contacts.sort((a, b) => {
					let a_timestamp = a.timestamp
					let b_timestamp = b.timestamp
					
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
				this.reorder_contacts()
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
			show("messages_placeholder")
		},
		toggle_message_date(message) {
			if(message.show_date) {
				message.show_date = false
			}
			else {
				message.show_date = true
			}
		},
		set_contact(contact) {
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
			message["show_date"] = false
			
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
			for(messages_i in this.messages) {
				if(this.messages[messages_i]["id"] == message_id) {
					this.messages[messages_i]["seen"] = 1
				}
			}
		},
		refresh_dates() {
			for(messages_i in this.messages) {
				this.messages[messages_i]["date_string"] = date_to_relative_date(this.messages[messages_i].timestamp)
			}
		},
		reorder_messages() {
			this.set_messages(
				messages.messages.sort((a, b) => {
					return new Date(a.timestamp) - new Date(b.timestamp)
				})
			)
		},
		send_message() {
			message_editor.focus()
			if(message_editor.getData() == "") {
				return
			}
			if(this.is_sending) {
				return
			}

			var formData = new FormData()
			formData.append("token", user.jwt)
			formData.append("receiver_uid", this.contact.uid)
			formData.append("content", message_editor.getData())

			message_editor.isReadOnly = true
			this.is_sending = true

			axios.post("/api/v1/messages/send", formData).then((response) => {
				if(response["data"]["status"] == "success") {
					message_data = {
						"id": response["data"]["id"],
						"sender_uid": response["data"]["sender_uid"],
						"receiver_uid": response["data"]["receiver_uid"],
						"timestamp": response["data"]["timestamp"],
						"content": message_editor.getData(),
						"seen": response["data"]["seen"],
					}

					this.add_message(message_data)

					contacts.change_last_message_of_uid(message_data)

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

				message_editor.isReadOnly = false
				this.is_sending = false
			}).catch((err) => {
				console.error(err)
				error.change_content("An unexpected error occurred")
				error.show()
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
            // set temporarly as seen in contacts list
            contact.last_message.seen = 1

			this.contact = contact
			if(this.contact == {}) {
				return
			}

			this.messages_loading = true

			var formData = new FormData()
			formData.append("token", user.jwt)
			formData.append("receiver_uid", this.contact.uid)

			axios.post("/api/v1/messages/get", formData).then((response) => {
				if(response["data"]["status"] == "success") {
					this.set_messages(response["data"]["messages"])
					show("messages")
				}
				else {
					error.change_content("An unexpected error occurred")
					error.show()
					this.contact = {}
					this.messages = []
				}
				this.messages_loading = false
			}).catch((err) => {
				console.error(err)
				error.change_content("An unexpected error occurred")
				error.show()
				this.messages_loading = false
				this.contact = {}
				this.messages = []
			})
		},
        action_block_contact() {
            return new Promise((resolve, reject) => {
				let contact_uid = this.contact.uid
                var formData = new FormData()
			    formData.append("token", user.jwt)
			    formData.append("contact_uid", contact_uid)

			    axios.post("/api/v1/contacts/block", formData).then((response) => {
				    if(response["data"]["status"] == "success") {
						show("messages_placeholder")
						contacts.remove_contact(contact_uid)
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
            confirmation.ask_confirmation("Would you really like to block <strong>" + this.contact.name + "</strong>?", this.action_block_contact)
        },
		action_delete_contact() {
            return new Promise((resolve, reject) => {
				let contact_uid = this.contact.uid
                var formData = new FormData()
			    formData.append("token", user.jwt)
			    formData.append("contact_uid", contact_uid)

			    axios.post("/api/v1/contacts/delete", formData).then((response) => {
				    if(response["data"]["status"] == "success") {
						show("messages_placeholder")
						contacts.remove_contact(contact_uid)
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
		this.$cookies.config('30d','','',false) // expire, path, domain, secure

		if(!this.$cookies.get('user') || this.$cookies.get('user') == undefined) {
			this.show()
			return
		}

		var formData = new FormData()
		formData.append("token", this.$cookies.get('user').jwt)

		axios.post("/api/v1/users/check-token", formData).then((response) => {
			if(response["data"]["status"] == "success") {
				user = response["data"]

				socket.emit('register', {jwt: user.jwt})
				show("messages_placeholder")
				
				contacts.load()
			}
			else {
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
			this.signup = true
		},
		set_in() {
			this.signup = false
		},
		sign() {
			this.sign_loading = true
			if(this.signup) {
				var formData = new FormData()
				formData.append("name", this.name_input)
				formData.append("username", this.username_input)
				formData.append("password", this.password_input)

				axios.post("/api/v1/users/signup", formData).then((response) => {
					if(response["data"]["status"] == "success") {
						user = response["data"]

						this.$cookies.set('user', user)
						socket.emit('register', {jwt: user.jwt})
						
						this.name_input = ""
						this.username_input = ""
						this.password_input = ""
						show("messages_placeholder")
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
					this.sign_loading = false
				}).catch((err) => {
					console.error(err)
					error.change_content("An unexpected error occurred")
					error.show()
					this.sign_loading = false
				})
			}
			else {
				var formData = new FormData()
				formData.append("username", this.username_input)
				formData.append("password", this.password_input)

				axios.post("/api/v1/users/signin", formData).then((response) => {
					if(response["data"]["status"] == "success") {
						user = response["data"]

						this.$cookies.set('user', user)
						socket.emit('register', {jwt: user.jwt})
						
						this.name_input = ""
						this.username_input = ""
						this.password_input = ""
						show("messages_placeholder")
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
					this.sign_loading = false
				}).catch((err) => {
					console.error(err)
					error.change_content("An unexpected error occurred")
					error.show()
					this.sign_loading = false
				})
			}
		},
		logout() {
			this.set_in()
			user = {}
			this.$cookies.remove('user')
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
			contacts.load()
			show("messages_placeholder")
		},
		add_contact() {
			this.add_contact_loading = true
			this.username_input_enabled = false
			this.request_send_message_showed = false
			
			var formData = new FormData()
			formData.append("token", user.jwt)
			formData.append("contact_username", this.username_input)

			axios.post("/api/v1/contacts/add", formData).then((response) => {
				if(response["data"]["status"] == "success") {
					this.username_input = ""
					this.request_send_message_showed = true

					setTimeout(() => {
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
				this.add_contact_loading = false
				this.username_input_enabled = true
			}).catch((err) => {
				console.error(err)
				error.change_content("An unexpected error occurred")
				error.show()
				this.add_contact_loading = false
				this.username_input_enabled = true
			})
		}
    }
})

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
				this.hide()
			}, 5000)
		},
		hide() {
			this.showed = false
		},
		change_content(content) {
			this.hide()
			this.content = content
		}
    }
})

socket.on('new_message', (message) => {
	if(message["sender_uid"] == messages.contact.uid || message["receiver_uid"] == messages.contact.uid) {
		messages.add_message(message)
	}

	contacts.change_last_message_of_uid(message)
})

socket.on('message_seen', (message_id) => {
	messages.set_message_as_seen(message_id)
})
