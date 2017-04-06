$(function(){
	$('#train').click(function(){
		
		$.ajax({
			url: '/signUp',
			data: "train",
			type: 'POST',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});
