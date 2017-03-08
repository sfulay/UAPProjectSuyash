window.setInterval(thing, 5000);

function thing() {
	$.ajax({
		url: '/sendText',
		data: "hello",
		type: 'GET',
		success: function(response){
			console.log(response);
		},
		error: function(error){
			console.log(error);
		}
	});
}