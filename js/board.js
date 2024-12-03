function removeNonAlphanumeric(str) {
    return str.replace(/[^a-zA-Z0-9]/g, '');
}

function removeNonNumeric(str) {
    return str.replace(/[^0-9]/g, '');
}

var username = localStorage.getItem('username');
if (username === null) {
    let username = prompt('Your username');
	if(username) {
		username = removeNonAlphanumeric(username).trim();
		if(username == "") {
			location.href = '../';
			username = null;
		}
        localStorage.setItem('username', removeNonAlphanumeric(username));
        location.reload();
	} else {
		location.href = '../';
		username = null;
	}
}

function play_confetti(duration = 5000) {
    $('#board_confetti').prop('disabled', true);
    const canvas = document.createElement('canvas');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    document.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');

    const confettiCount = 100;
    const confetti = [];
    for (let i = 0; i < confettiCount; i++) {
        confetti.push({
            x: Math.random() * canvas.width,
            y: canvas.height,
            width: Math.random() * 10 + 5,
            height: Math.random() * 10 + 5,
            angle: Math.random() * 2 * Math.PI,
            speed: Math.random() * 2 + 1,
            color: '#' + Math.floor(Math.random() * 16777215).toString(16),
        });
    }

    const startTime = Date.now();
    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        confetti.forEach(confetto => {
            confetto.y -= confetto.speed;
            confetto.x += Math.cos(confetto.angle) * confetto.speed;

            ctx.fillStyle = confetto.color;
            ctx.fillRect(confetto.x, confetto.y, confetto.width, confetto.height);

            if (confetto.y < -confetto.height) {
                confetto.y = canvas.height;
                confetto.x = Math.random() * canvas.width;
            }
        });

        if (Date.now() - startTime >= duration) {
            $('#board_confetti').prop('disabled', false);
            canvas.remove();
            return;
        }
        requestAnimationFrame(draw);
    }
    draw();
}

function customPrompt(message, defaultValue) {
    const dialog = document.createElement('div');
    dialog.classList.add('custom-prompt');

    const title = document.createElement('p');
    title.textContent = message;
    dialog.appendChild(title);

    const input = document.createElement('input');
    input.type = 'text';
    input.value = defaultValue || '';
    input.autofocus = true;
    dialog.appendChild(input);

    const button = document.createElement('button');
    button.textContent = 'OK';
    dialog.appendChild(button);

    document.body.appendChild(dialog);
    dialog.style.display = 'block';

    return new Promise((resolve) => {
        button.addEventListener('click', () => {
            const value = input.value;
            dialog.remove();
            resolve(value);
        });

        input.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') {
                const value = input.value;
                dialog.remove();
                resolve(value);
            }
        });

        document.addEventListener('keyup', (event) => {
            if (event.key === 'Escape') {
                dialog.remove();
                resolve(null);
            }
        });
    });
}

const log = (text, color) => {
    $('#board_log').append(`<span style='color: ${color}'>${text}</span><br>`).animate({ scrollTop: $(document).height() }, 200);
};

function searchKey(object, classes) {
    for (const key in object) {
        if (object.hasOwnProperty(key)) {
            if (key.includes(classes)) {
                return object[key];
            }
        }
    }
    return false;
}

function board_timer(timerInSeconds) {
    $('#board_timer .title').html(timerInSeconds);
    timerInSeconds -= 1;
    if (timerInSeconds >= 0) {
        setTimeout(function(){ board_timer(timerInSeconds) }, 1000)
    }
    if (timerInSeconds == -1) {
        $( '#wallpaper' ).effect( 'highlight' )
        $('#board_timer .title').html('Timer');
    }
}

function board_vote(maxVote) {
    $('#board_vote .title').html(maxVote);
}

function board_vote_order() {
    $(".sortable").each(function() {
        const $sortableList = $(this);
        $sortableList.find("li").sort(function(a, b) {
            const aVotes = parseInt($(a).find(".votes").text());
            const bVotes = parseInt($(b).find(".votes").text());
            return bVotes - aVotes;
        }).appendTo($sortableList);
    });
}
    
if(username !== null) {
    let ws;
    let reconnectInterval = 1000;
    let board_author;
    let board_id = window.location.pathname.split('/').pop();
    let user_id = false;
    var pos_x;
    var pos_y;
    var curr_highlightUser;
    var maxVoteTotal;
    var stockList = {};


    function board_copy_link() {
        try {
            navigator.clipboard.writeText(window.location.href);
            log(username + ' >>> url copied!', 'yellow');
        } catch (err) {
            console.error('Error_copy:', err);
        }
    };

    function startTimer() {
        if (board_author != username) return;
        let timerInSeconds = prompt('Timer in secondes');

	timerInSeconds = removeNonNumeric(timerInSeconds);	
        if(timerInSeconds && timerInSeconds != "") {
            ws.send(JSON.stringify({
                type: 'start_timer',
                board_id: board_id,
                timerInSeconds: timerInSeconds,
            }));
        }
    }

    function startVote() {
        if (board_author != username) return;
        let maxVote = prompt('Max votes');

	maxVote = removeNonNumeric(maxVote);	    
        if(maxVote && maxVote != "") {
            ws.send(JSON.stringify({
                type: 'start_vote',
                board_id: board_id,
                maxVote: maxVote,
            }));
        }
    }

    function startConfetti() {
        ws.send(JSON.stringify({
            type: 'start_confetti',
            board_id: board_id,
        }));
    }

    function start_timer() {
        ws.send(JSON.stringify({
            type: 'start_timer',
            board_id: board_id,
            timerInSeconds: timerInSeconds,
        }));
    }

    function addCard(col_id) {
        customPrompt('Add new Card', '').then(cardContent => {
            if(cardContent) {
                ws.send(JSON.stringify({
                    type: 'card_add',
                    pos: $(`#col_${col_id} ul`).children('li').length,
                    author: username,
                    board_id: board_id,
                    user_id: user_id,
                    col_id: col_id,
                    votes: 0,
                    cardContent: cardContent,
                }));
            }
        });
    }

    function editCard(col_id, card_uuid) {
        customPrompt('Editing Card content', $(`#col_${col_id} .uuid_${card_uuid} .info .info_content`).text()).then(cardContent => {
            if(cardContent) {
                ws.send(JSON.stringify({
                    type: 'card_edit',
                    author: username,
                    board_id: board_id,
                    user_id: user_id,
                    col_id: col_id,
                    card_uuid: card_uuid,
                    cardContent: cardContent
                })); 
            }
        });
    }

    function voteCard(col_id, card_uuid) {
        var maxVote = $('#board_vote .title').text();
        if (!isNaN(maxVote)) {
            maxVote = parseInt(maxVote);
            maxVote -= 1
            if (maxVote >= 0) {
                $('#board_vote .title').text(maxVote);
                ws.send(JSON.stringify({
                    type: 'card_vote',
                    author: username,
                    board_id: board_id,
                    user_id: user_id,
                    col_id: col_id,
                    card_uuid: card_uuid
                })); 
            }
        } 
    }

    function deleteCard(col_id, card_uuid) {
        ws.send(JSON.stringify({
            type: 'card_delete',
            author: username,
            board_id: board_id,
            user_id: user_id,
            col_id: col_id,
            card_uuid: card_uuid,
        }));
    }

    function addCol() {
        if (board_author != username) return;
        let colName = prompt('Zone name');
        if(colName) {
            ws.send(JSON.stringify({
                type: 'col_add',
                author: username,
                board_id: board_id,
                user_id: user_id,
                colName: colName,
            }));
        }
    }

    function orderCol(name, data) {
        uuid_list = []

        $.each(data, function(_, element) {
            const uuidClass = element.split(' ').filter(cls => cls.startsWith('uuid_'))[0];
            if (uuidClass) {
                uuid_list.push(uuidClass);
            }
        });

        ws.send(JSON.stringify({
            type: 'col_order',
            author: username,
            board_id: board_id,
            user_id: user_id,
            colName: name.slice(4),
            uuidList: uuid_list
        }));
    }

    function deleteCol(col_id) {
        if (board_author != username) return;
        if (window.confirm('You really want to delete this column?')) {
            ws.send(JSON.stringify({
                type: 'col_delete',
                author: username,
                board_id: board_id,
                user_id: user_id,
                colName: col_id,
            }));
        }
    }

    function highlightUser(Husername) {
        if(curr_highlightUser != Husername) {
            $('#users div').each(function() {
                const $user = $(this);
                if ($user.attr('data-username') == Husername) {
                    $user.animate({'opacity': 1}, 300);
                } else {
                    $user.animate({'opacity': .2}, 300);
                }
            });

            $('.col li').each(function() {
                const $li = $(this);
                if ($li.hasClass(`user_${Husername}`)) {
                    $li.css('display', 'block');
                } else {
                    $li.css('display', 'none');
                }
            });
            curr_highlightUser = Husername;
        } else {
            $('#users div').each(function() {
                $(this).animate({'opacity': 1}, 300);
            });

            $('.col li').each(function() {
                $(this).css('display', 'block');
            });
            curr_highlightUser = false;
        }
    }

    function connect() {
        ws = new WebSocket('ws://' + location.hostname + ':8009');

        $(document).on('mousemove', function (event) { 
            pos_x = event.pageX;
            pos_y = event.pageY; 
        }); 

        function mouse_position() {
            ws.send(JSON.stringify({
                type: 'cursor_user',
                board_id: board_id,
                pos_x: pos_x,
                pos_y: pos_y
            }));
        }

        ws.addEventListener('message', ev => {
            ws_data = JSON.parse(ev.data);
            if (ws_data.board_id != board_id) {
                return
            }
            if (ws_data.type == 'connect_status') {
                if (!ws_data.error) {
                    user_id = ws_data.user_id;
                }
            } else if (ws_data.type == 'users_list') {
                $('#users, #cursors').html('');
                $.each(ws_data.users_list,function(index,value){ 
                    if(user_id && user_id != index && value.board_id == board_id) {
                        $('#cursors').append(`<div id='cursor_${index}' class='cursor'><div class='username'>${value.username}</div></div>`)
                    } 
                    if(value.board_id == board_id) {
                        $('#users').append(`<div id='user_${index}' class='user' title='${value.username}' data-username='${value.username}' onclick='highlightUser("${value.username}");'><i class='material-icons' style='color: ${value.color}'>face</i></div>`)
                        $(document).tooltip({position: {my: "center top",at: "center bottom"}});
                    }
                });
            } else if (ws_data.type == 'user_add') {
                if(user_id != ws_data.user_id && ws_data.board_id == board_id) {
                    log(ws_data.username + ' >>> connected', 'yellow');
                    $('#users').append(`<div id='user_${ws_data.user_id}' class='user' title='${ws_data.username}' data-username='${ws_data.username}' onclick='highlightUser("${ws_data.username}");'><i class='material-icons' style='color: ${ws_data.color}'>face</i></div>`)
                    $('#cursors').append(`<div id='cursor_${ws_data.user_id}' class='cursor'><div class='username'>${ws_data.username}</div></div>`);
                    $(document).tooltip({position: {my: "center top",at: "center bottom"}});
                }
            } else if (ws_data.type == 'user_remove') {
                log(ws_data.username + ' >>> disconnected', 'red');
                $(`#user_${ws_data.user_id}`).hide('fade', 300).remove();
                $(`#cursor_${ws_data.user_id}`).hide('fade', 300).remove();
            } else if (ws_data.type == 'cursor_user') {
                if(user_id != ws_data.user_id) {
                    if(ws_data.pos_y && ws_data.pos_x) {
                        $(`#cursor_${ws_data.user_id}`).animate({ top: `${ws_data.pos_y}px`, left: `${ws_data.pos_x}px`}, 300);    
                    }                            
                }
            } else if (ws_data.type == 'board_info') {
                board_author = ws_data.board_info.author;
                board_data = ws_data.board_info.data;
                check_timer = ws_data.board_info.timer;

                if(check_timer) {
                    const now = new Date();
                    difSecs = parseInt((check_timer - now.getTime()) / 1000);
                    if(difSecs > 0) {
                        board_timer(difSecs);
                    }
                }

                $('#board').html('');
                if(!board_data){
                    $('#board_name').html('This board does not exist, <a href="../">return to home page</a>');
                    $('#board_timer, #board_vote, #r_menu').remove();
                    return;
                }

                $.each(board_data,function(index,value){ 
                    html = `<div id='col_${index}' class='col'><h1>${index}<i onclick='addCard("${index}");' class='add_icon material-icons'>add</i>`
                    if (board_author == username) {
                        html += `<i onclick='deleteCol("${index}");' class='drop_icon material-icons'>delete</i>`
                    }
                    html += `</h1><ul class='sortable'></ul></div>`
                    $('#board').append(html);

                    const entries = Object.entries(value);
                    entries.sort((a, b) => a[1].pos - b[1].pos);
                    const sortedData = Object.fromEntries(entries);

                    $.each(sortedData,function(uuid,value){ 
                        html = `<li class='ui-state-default user_${value.author} uuid_${uuid} pos_${value.pos}'>
                            <div class='votes' onclick='voteCard("${index}", "${uuid}");'>${value.votes}</div>
                            <div class='info'>`

                        if(value.author == username) {
                            html += `<div class='edit_icon material-icons' title='edit card' onclick='editCard("${index}", "${uuid}");'>edit</i></div>`;
                            html += `<div class='delete_icon material-icons' title='delete card' onclick='deleteCard("${index}", "${uuid}");'>delete</i></div>`;
                        }

                        html += `
                                <div class='info_author'>by ${value.author}</div>
                                <div class='info_content'>${value.content}</div>
                            </div>
                        </li>`;
                        $(`#col_${index} .sortable`).append(html);
                    });
                    $(`#col_${index} .sortable`).sortable({connectWith:".sortable",update:function(e,u){var l=[];$(this).children().each(function(i,e){l.push($(e).attr('class'))});orderCol($(this).parent().attr('id'),l)}});
                });

                $('#board_name').html(ws_data.board_info.board_name);
            } else if (ws_data.type == 'start_timer') {
                board_timer(ws_data.timerInSeconds);
            } else if (ws_data.type == 'start_confetti') {
                play_confetti();
            } else if (ws_data.type == 'start_vote') {
                maxVoteTotal = $("#users .user").length * ws_data.maxVote;
                $(".votes").text("0");
                log('Vote Session >>> started', 'red');
                board_vote(ws_data.maxVote);
            } else if (ws_data.type == 'card_add') {
                html = `<li class='ui-state-default user_${ws_data.card_add.author} uuid_${ws_data.card_uuid} pos_${ws_data.card_add.pos}'>
                    <div class='votes' onclick='voteCard("${ws_data.card_add.col_id}", "${ws_data.card_uuid}");'>${parseInt(ws_data.card_add.votes)}</div>
                    <div class='info'>`

                if(ws_data.card_add.author == username) {
                    html += `<div class='edit_icon material-icons' title='edit card' onclick='editCard("${ws_data.card_add.col_id}", "${ws_data.card_uuid}");'>edit</i></div>`;
                    html += `<div class='delete_icon material-icons' title='delete card' onclick='deleteCard("${ws_data.card_add.col_id}", "${ws_data.card_uuid}");'>delete</i></div>`;
                }

                html += `
                        <div class='info_author'>by ${ws_data.card_add.author}</div>
                        <div class='info_content'>${ws_data.card_add.cardContent}</div>
                    </div>
                </li>`;
                $(`#col_${ws_data.card_add.col_id} .sortable`).append(html);
                $(`#col_${ws_data.card_add.col_id} .sortable`).sortable({connectWith:".sortable",update:function(e,u){var l=[];$(this).children().each(function(i,e){l.push($(e).attr('class'))});orderCol($(this).parent().attr('id'),l)}});
            } else if (ws_data.type == 'card_edit') {
                $(`#col_${ws_data.card_edit.col_id} ul .uuid_${ws_data.card_edit.card_uuid} .info_content`).html(ws_data.card_edit.cardContent);
            } else if (ws_data.type == 'card_vote') { 
                $(`#col_${ws_data.card_vote.col_id} ul .uuid_${ws_data.card_vote.card_uuid} .votes`).html(ws_data.card_votes);
                if (board_author == username) {
                    var elementsVotes = $(".votes");
                    var totalVotes = 0;
                    elementsVotes.each(function() {
                        var valeurVote = parseInt($(this).text());
                        if (!isNaN(valeurVote)) {
                            totalVotes += valeurVote;
                        }
                    });
                    log(`Total Vote >>> ${totalVotes} / ${maxVoteTotal}`, 'cyan');
                } 
            } else if (ws_data.type == 'card_delete') {
                $(`#col_${ws_data.card_delete.col_id} ul .uuid_${ws_data.card_delete.card_uuid}`).remove();
            } else if (ws_data.type == 'col_add') {
                html = `<div id='col_${ws_data.col_add.colName}' class='col'><h1>${ws_data.col_add.colName}<i onclick='addCard("${ws_data.col_add.colName}");' class='add_icon material-icons'>add</i>`
                if (board_author == username) {
                    html += `<i onclick='deleteCol("${ws_data.col_add.colName}");' class='drop_icon material-icons'>delete</i>`
                }
                html += `</h1><ul class='sortable'></ul></div>`
                $('#board').append(html);
            } else if (ws_data.type == 'col_order') {
                const sortableList = document.querySelector(`#col_${ws_data.col_order.colName} .sortable`);
                const fragment = document.createDocumentFragment();
                ws_data.col_order.uuidList.forEach(uuid => {
                    const li = sortableList.querySelector(`li[class*="${uuid}"]`);
                    if (li) {
                        fragment.appendChild(li);
                    } else {
                        ws.send(JSON.stringify({
                            type: 'board_info',
                            board_id: board_id
                        }));
                    }
                });

                sortableList.innerHTML = '';
                sortableList.appendChild(fragment);
            } else if (ws_data.type == 'col_delete') {
                $(`#col_${ws_data.col_delete.colName}`).remove();
            } else {
                log(`${ws_data.username} >>> ${ws_data.content}`, 'cyan');
            }                    
        });

        document.getElementById('form').onsubmit = ev => {
            ev.preventDefault();
            const textField = document.getElementById('chat_msg');
            ws.send(JSON.stringify({
                type: 'message',
                board_id: board_id,
                content: textField.value
            }));
            textField.value = '';
        };

        ws.onopen = () => {
            log(username + ' >>> Your are logged!', 'green');
            ws.send(JSON.stringify({
                type: 'connect',
                board_id: board_id,
                username: localStorage.getItem('username')
            }));

            ws.send(JSON.stringify({
                type: 'board_info',
                board_id: board_id
            }));

            setInterval(function() { mouse_position() }, 2000);
        };

        // ws.onmessage = (event) => {
        //     console.log('Message reçu:', event.data);
        // };

        // ws.onerror = (error) => {
        //     console.error('Erreur de connexion:', error);
        // };

        ws.onclose = () => {
            log(username + ' >>> Please Wait, your are disconnected!', 'red');
            setTimeout(connect, reconnectInterval);
            reconnectInterval *= 2; // Double le délai à chaque tentative
        };
    }
    connect();
}
