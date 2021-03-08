var message_editor

BalloonEditor.create( document.getElementById( 'message_editor' ), {
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
	message_editor = editor

	editor.keystrokes.set('Enter', (data, stop) => {
    	stop()
		messages.send_message()
    })
})
.catch(error => {
	console.error(error)
})