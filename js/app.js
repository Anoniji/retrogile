/**
 * GNU GENERAL PUBLIC LICENSE
 * Version 3, 29 June 2007
 *
 * @author Anoniji <contact@anoniji.dev>
 *
 */

console.log(`\x1b[34m
______     _                   _ _    
| ___ \\   | |                 (_) |    
| |_/ /___| |_ _ __ ___   __ _ _| | ___ 
|    // _ \\ __| '__/ _ \\ / _\` | | |/ _ \\
| |\\ \\  __/ |_| | | (_) | (_| | | |  __/
\\_| \\_\\___|\\__|_|  \\___/ \\__, |_|_|\\___|
                          __/ |       
Do not use the console ! |___/ \x1b[0m`);

function detectDevTool(e){isNaN(+e)&&(e=100);var t=+new Date;debugger;var n=+new Date;(isNaN(t)||isNaN(n)||n-t>e)&&(localStorage.setItem("bad_user",!0),location.reload())}
localStorage.getItem("bad_user")&&setInterval(function(){window.fetch=window.WebSocket=console.error;localStorage.setItem("bad_user",!0)},1);

const hash = window.location.hash;

function removeNonAlphanumeric(str) {
	if (!str) return false;
	return str.replace(/[^a-zA-Z0-9]/g, '');
}

function removeNonAlphanumericSpace(str) {
	if (!str) return false;
	return str.replace(/[^a-zA-Z0-9 ]/g, '');
}

var username = localStorage.getItem('username');
if (username !== null) {
	$('#username').val(username);
}

function start_board() {
	let username = $('#username').val().trim();
	let boardname = $('#boardname').val();

	if (username) {
		username = removeNonAlphanumeric(username).trim();
		if (username == '') {
			$('#username').effect('highlight', { color: '#f44336' });
			return;
		}
		localStorage.setItem('username', username);
	} else {
		$('#username').effect('highlight', { color: '#f44336' });
		return;
	}

	if (boardname) {
		boardname = removeNonAlphanumericSpace(boardname).trim();
		if (boardname == '') {
			$('#boardname').effect('highlight', { color: '#f44336' });
			return;
		}
		if (hash) {
			const hashValue = hash.substring(1);
			location.href = `./board/${hashValue}`;
		} else {
			$.getJSON(`./create_board/${boardname}/${username}`).done(function (data) {
				location.href = data;
			});
		}
	} else {
		$('#boardname').effect('highlight', { color: '#f44336' });
	}
}

function list_board() {
	let username = $('#username').val().trim();

	if (username) {
		username = removeNonAlphanumeric(username).trim();
		if (username == '') {
			$('#username').effect('highlight', { color: '#f44336' });
			return;
		}
		localStorage.setItem('username', username);
		location.href = './board/';
	} else {
		$('#username').effect('highlight', { color: '#f44336' });
		return;
	}
}

$('#username, #boardname').keypress(function (event) {
	if (event.which === 13) {
		start_board()
	}
});

if (hash) {
	const hashValue = hash.substring(1);
	$('#boardname').attr('placeholder', '{{ translates.app_js_1 }}').val(hashValue).prop('disabled', true);
	$('.label_button').html('{{ translates.app_js_2 }}');
	$('#username').focus();
}

$('#username_cleaner').click(function () {
	localStorage.removeItem('username');
	$('#username').val('');
});
