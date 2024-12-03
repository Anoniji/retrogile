function removeNonAlphanumeric(str) {
    return str.replace(/[^a-zA-Z0-9]/g, '');
}

function removeNonAlphanumericSpace(str) {
    return str.replace(/[^a-zA-Z0-9 ]/g, '');
}

var username = localStorage.getItem("username");
if (username !== null) {
	$('#username').val(username);
}

function start_board() {
	let username = $('#username').val().trim();
	let boardname = $('#boardname').val();

	if(username) {
		username = removeNonAlphanumeric(username).trim();
		if(username == "") {
			$('#username').effect('highlight');
			return;
		}
		localStorage.setItem('username', username);
	} else {
		$('#username').effect('highlight');
		return;
	}

	if(boardname) {
		boardname = removeNonAlphanumericSpace(boardname).trim();
		if(boardname == "") {
			$('#boardname').effect('highlight');
			return;
		}
		$.getJSON(`./create_board/${boardname}/${username}`).done(function(data) {
			location.href = data;
		});
	} else {
		$('#boardname').effect('highlight');
	}
}

$("#boardname").keypress(function(event) {
    if (event.which === 13) {
		start_board()
	}
});
