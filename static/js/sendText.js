$(document).ready(function() {
	console.log("ready in sendTExt.js")
		$.ajax({
			url: '/loadContacts',
			data: "",
			type: 'GET',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
});