/**
 * GNU GENERAL PUBLIC LICENSE
 * Version 3, 29 June 2007
 *
 * @author Anoniji <contact@anoniji.dev>
 *
 */

const hash = window.location.hash;

function removeNonAlphanumeric(str) {
	if(!str) return false;
    return str.replace(/[^a-zA-Z0-9]/g, '');
}

function removeNonAlphanumericSpace(str) {
	if(!str) return false;
    return str.replace(/[^a-zA-Z0-9 ]/g, '');
}

var username = localStorage.getItem('username');
if (username !== null) {
	$('#username').val(username);
}

function start_board() {
	let username = $('#username').val().trim();
	let boardname = $('#boardname').val();

	if(username) {
		username = removeNonAlphanumeric(username).trim();
		if(username == '') {
			$('#username').effect('highlight', {color: '#f44336'});
			return;
		}
		localStorage.setItem('username', username);
	} else {
		$('#username').effect('highlight', {color: '#f44336'});
		return;
	}

	if(boardname) {
		boardname = removeNonAlphanumericSpace(boardname).trim();
		if(boardname == '') {
			$('#boardname').effect('highlight', {color: '#f44336'});
			return;
		}
		if (hash) {
			const hashValue = hash.substring(1);
			location.href = `./board/${hashValue}`;
		} else {
			$.getJSON(`./create_board/${boardname}/${username}`).done(function(data) {
				location.href = data;
			});
		}
	} else {
		$('#boardname').effect('highlight', {color: '#f44336'});
	}
}

function list_board() {
	let username = $('#username').val().trim();

	if(username) {
		username = removeNonAlphanumeric(username).trim();
		if(username == '') {
			$('#username').effect('highlight', {color: '#f44336'});
			return;
		}
		localStorage.setItem('username', username);
		location.href = './board/';
	} else {
		$('#username').effect('highlight', {color: '#f44336'});
		return;
	}
}

$('#username, #boardname').keypress(function(event) {
    if (event.which === 13) {
		start_board()
	}
});

if (hash) {
    const hashValue = hash.substring(1);
    $('#boardname').attr('placeholder', 'Board ID').val(hashValue).prop('disabled', true);
    $('.label_button').html('Join the board');
}

$('#username_cleaner').click(function() {
	localStorage.removeItem('username');
	$('#username').val('');
});
