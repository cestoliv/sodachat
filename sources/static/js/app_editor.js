var message_editor

BalloonEditor.create(document.getElementById( 'message_editor' ), {
	placeholder: "Send a message",
	toolbar: {
		items: [
			'bold',
			'italic',
			'link',
			'bulletedList',
			'numberedList',
			'|',
			'indent',
			'outdent',
			'|',
			'imageUpload',
			'blockQuote',
			'insertTable',
			'mediaEmbed'
		]
	},
	language: 'en',
	image: {
		toolbar: [
			'imageTextAlternative',
			'imageStyle:full',
			'imageStyle:side'
		]
	},
	table: {
		contentToolbar: [
			'tableColumn',
			'tableRow',
			'mergeTableCells'
		]
	},
	licenseKey: '',
})
.then(editor => {
	// assign th message Ballon Editor
	message_editor = editor

	// handle enter key
	editor.keystrokes.set('Enter', (data, stop) => {
		// prevent line break
		stop()
		// send message
		messages.send_message()
    })
})
.catch(error => {
	console.error(error)
})