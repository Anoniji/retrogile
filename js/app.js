
var username = localStorage.getItem("username");
if (username !== null) {
	$('#username').val(username);
}

function start_board() {
	username = $('#username').val();
	const boardname = $('#boardname').val();

	localStorage.setItem('username', username);

	if(boardname) {
		$.getJSON(`./create_board/${boardname}`).done(function(data) {
			location.href = data;
		}).fail(function() {
			console.log('NOK');
		});
	} else {
		$( "#boardname" ).effect( "highlight" )
	}



}