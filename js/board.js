var username = localStorage.getItem("username");
if (username === null) {
    let username = prompt('Your username');
    if(username) {
        localStorage.setItem('username', username);
    } else {
        location.href = "../";
    }
}

const log = (text, color) => {
    $("#board_log").append(`<span style="color: ${color}">${text}</span><br>`).animate({ scrollTop: $(document).height() }, 200);
};

function board_timer(timerInSeconds) {
    $('#board_timer .title').html(timerInSeconds);
    timerInSeconds -= 1;
    if (timerInSeconds >= 0) {
        setTimeout(function(){ board_timer(timerInSeconds) }, 1000)
    }
    if (timerInSeconds == -1) {
        $( "#wallpaper" ).effect( "highlight" )
        $('#board_timer .title').html('Timer');
    }
}
    
if(username !== null) {
    let ws;
    let reconnectInterval = 1000;
    let board_author;
    let board_id = window.location.pathname.split("/").pop();
    let user_id = false;
    var pos_x;
    var pos_y;
    var curr_highlightUser;


    document.getElementById("board_copy_link").onclick=async() => {
        try {
            await navigator.clipboard.writeText(window.location.href);
            log(username + ' >>> url copied!', 'yellow');
        } catch (err) {
            console.error('Error_copy:', err);
        }
    };

    function startTimer() {
        if (board_author != username) return;
        let timerInSeconds = prompt('Timer in secondes');
        if(timerInSeconds) {
            ws.send(JSON.stringify({
                type: "start_timer",
                board_id: board_id,
                timerInSeconds: timerInSeconds,
            }));
        }
    }

    function start_timer() {
        ws.send(JSON.stringify({
            type: "start_timer",
            board_id: board_id,
            timerInSeconds: timerInSeconds,
        }));
    }

    function addCard(col_id) {
        let cardContent = prompt('Card content');
        if(cardContent) {
            ws.send(JSON.stringify({
                type: "card_add",
                pos: $(`#col_${col_id} ul`).children('li').length,
                author: username,
                board_id: board_id,
                user_id: user_id,
                col_id: col_id,
                votes: 0,
                cardContent: cardContent,
            }));
        }
    }

    function editCard(col_id, pos) {
        let cardContent = prompt('Card content');
        if(cardContent) {
            ws.send(JSON.stringify({
                type: "card_edit",
                author: username,
                board_id: board_id,
                user_id: user_id,
                col_id: col_id,
                pos: pos,
                cardContent: cardContent
            })); 
        }
    }

    function deleteCard(col_id, pos) {
        ws.send(JSON.stringify({
            type: "card_delete",
            author: username,
            board_id: board_id,
            user_id: user_id,
            col_id: col_id,
            pos: pos,
        }));
    }

    function addCol() {
        if (board_author != username) return;
        let colName = prompt('Zone name');
        if(colName) {
            ws.send(JSON.stringify({
                type: "col_add",
                author: username,
                board_id: board_id,
                user_id: user_id,
                colName: colName,
            }));
        }
    }

    function deleteCol(col_id) {
        if (board_author != username) return;
        if (window.confirm("You really want to delete this column?")) {
            ws.send(JSON.stringify({
                type: "col_delete",
                author: username,
                board_id: board_id,
                user_id: user_id,
                colName: col_id,
            }));
        }
    }


    function highlightUser(Husername) {
        if(curr_highlightUser != Husername) {
            $('.col li').each(function() {
                const $li = $(this);
                if ($li.hasClass(`user_${Husername}`)) {
                    $li.animate({'opacity': 1}, 300);
                } else {
                    $li.animate({'opacity': .2}, 300);
                }
            });
        } else {
            $('.col li').each(function() {
                $(this).animate({'opacity': 1}, 300);
            });
        }
        curr_highlightUser = Husername    }

    function connect() {
        ws = new WebSocket('ws://' + location.hostname + ':8009');

        $(document).on("mousemove", function (event) { 
            pos_x = event.pageX;
            pos_y = event.pageY; 
        }); 

        function mouse_position() {
            ws.send(JSON.stringify({
                type: "cursor_user",
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
                $("#users, #cursors").html('');
                $.each(ws_data.users_list,function(index,value){ 
                    if(user_id && user_id != index && value.board_id == board_id) {
                        $("#users").append(`<div id="user_${index}" class="user" title="${value.username}" onclick="highlightUser('${value.username}');"><i class="material-icons">face</i></div>`)
                        $("#cursors").append(`<div id="cursor_${index}" class="cursor"><div class="username">${value.username}</div></div>`)
                    }
                });
            } else if (ws_data.type == 'user_add') {
                if(ws_data.board_id == board_id) {
                    log(ws_data.username + ' >>> connected', 'yellow');
                    $("#users").append(`<div id="user_${ws_data.user_id}" class="user" title="${ws_data.username}" onclick="highlightUser('${ws_data.username}');"><i class="material-icons">face</i></div>`)
                    $("#cursors").append(`<div id="cursor_${ws_data.user_id}" class="cursor"><div class="username">${ws_data.username}</div></div>`)
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

                $("#board").html('');
                $.each(board_data,function(index,value){ 
                    html = `<div id="col_${index}" class="col"><h1>${index}<i onclick="addCard('${index}');" class="add_icon material-icons">add</i>`
                    if (board_author == username) {
                        html += `<i onclick="deleteCol('${index}');" class="drop_icon material-icons">delete</i>`
                    }
                    html += `</h1><ul class="sortable"></ul></div>`
                    $("#board").append(html);

                    value.sort((a, b) => a.pos - b.pos);
                    $.each(value,function(_,value){ 
                        html = `<li class="ui-state-default user_${value.author} pos_${value.pos}">
                            <div class="votes">${value.votes}</div>
                            <div class="info">`

                        if(value.author == username) {
                            html += `<div class="edit_icon material-icons" title="edit card" onclick="editCard('${index}', '${value.pos}');">edit</i></div>`;
                            html += `<div class="delete_icon material-icons" title="delete card" onclick="deleteCard('${index}', '${value.pos}');">delete</i></div>`;
                        }

                        html += `
                                <div class="info_author">by ${value.author}</div>
                                <div class="info_content">${value.content}</div>
                            </div>
                        </li>`;
                        $(`#col_${index} .sortable`).append(html);
                    });
                    $(`#col_${index} .sortable`).sortable();
                });

                $('#board_name').html(ws_data.board_info.board_name);
            } else if (ws_data.type == 'start_timer') {
                board_timer(ws_data.timerInSeconds);
            } else if (ws_data.type == 'card_add') {
                html = `<li class="ui-state-default user_${ws_data.card_add.author} pos_${ws_data.card_add.pos}">
                    <div class="votes">${parseInt(ws_data.card_add.votes)}</div>
                    <div class="info">`

                if(ws_data.card_add.author == username) {
                    html += `<div class="edit_icon material-icons" title="edit card" onclick="editCard('${ws_data.card_add.col_id}', '${ws_data.card_add.pos}');">edit</i></div>`;
                    html += `<div class="delete_icon material-icons" title="delete card" onclick="deleteCard('${ws_data.card_add.col_id}', '${ws_data.card_add.pos}');">delete</i></div>`;
                }

                html += `
                        <div class="info_author">by ${ws_data.card_add.author}</div>
                        <div class="info_content">${ws_data.card_add.cardContent}</div>
                    </div>
                </li>`;
                $(`#col_${ws_data.card_add.col_id} .sortable`).append(html);
            } else if (ws_data.type == 'card_delete') {
                $(`#col_${ws_data.card_delete.col_id} ul .pos_${ws_data.card_delete.pos}`).remove();
            } else if (ws_data.type == 'card_edit') {
                $(`#col_${ws_data.card_edit.col_id} ul .pos_${ws_data.card_edit.pos} .info_content`).html(ws_data.card_edit.cardContent);
            } else if (ws_data.type == 'col_add') {
                html = `<div id="col_${ws_data.col_add.colName}" class="col"><h1>${ws_data.col_add.colName}<i onclick="addCard('${ws_data.col_add.colName}');" class="add_icon material-icons">add</i>`
                if (board_author == username) {
                    html += `<i onclick="deleteCol('${ws_data.col_add.colName}');" class="drop_icon material-icons">delete</i>`
                }
                html += `</h1><ul class="sortable"></ul></div>`
                $("#board").append(html);
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
                type: "message",
                board_id: board_id,
                content: textField.value
            }));
            textField.value = '';
        };

        ws.onopen = () => {
            log(username + ' >>> Your are logged!', 'green');
            ws.send(JSON.stringify({
                type: "connect",
                board_id: board_id,
                username: localStorage.getItem("username")
            }));

            ws.send(JSON.stringify({
                type: "board_info",
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