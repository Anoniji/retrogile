
var username = localStorage.getItem("username");
if (username !== null) {
	$('#username').val(username);
}

function start_board() {
	username = $('#username').val();
	const boardname = $('#boardname').val();

	localStorage.setItem('username', username.replaceAll(' ', '_'));

	if(boardname) {
		$.getJSON(`./create_board/${boardname}/${username}`).done(function(data) {
			location.href = data;
		});
	} else {
		$( "#boardname" ).effect( "highlight" )
	}
}

$("#boardname").keypress(function(event) {
    if (event.which === 13) {
		start_board()
	}
});
