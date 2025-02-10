/**
 * GNU GENERAL PUBLIC LICENSE
 * Version 3, 29 June 2007
 *
 * @author Anoniji <contact@anoniji.dev>
 *
 */

function removeNonAlphanumericSpace(str) {
    if(!str) return false;
    return str.replace(/[^a-zA-Z0-9 ]/g, '');
}

var username = localStorage.getItem('username');
if (username === null) {
	location.href = '../';
} else {
    $( "#board_name" ).html(`List of "${username}" boards`);

    let ws;
    let reconnectInterval = 1000;

    function renameBoard(board_uuid) {
        if (!board_uuid) return;
        let board_name = prompt('New name for the board');
        board_name = removeNonAlphanumericSpace(board_name);
        if (board_name) {
            ws.send(JSON.stringify({
                type: 'board_rename',
                username: localStorage.getItem('username'),
                board_uuid: board_uuid,
                board_name: board_name
            }));
        }
    }

    function templateBoard(board_uuid) {
        if (!board_uuid) return;
        let new_name = prompt('Name for the new board');
        new_name = removeNonAlphanumericSpace(new_name);
        if (new_name) {
            ws.send(JSON.stringify({
                type: 'board_template',
                username: localStorage.getItem('username'),
                board_uuid: board_uuid,
                new_name: new_name
            }));
        }
    }

    function deleteBoard(board_uuid) {
        if (!board_uuid) return;
        let check_confirm = confirm('Are you sure you want to delete this board?');
        if (check_confirm) {
            ws.send(JSON.stringify({
                type: 'board_delete',
                username: localStorage.getItem('username'),
                board_uuid: board_uuid
            }));
        }
    }

    function openBoard(board_link) {
        if (!board_link) return;
        location.href = `.${board_link.replace('.json', '')}`;
    }

    function connect() {
        ws_path = `ws://${location.hostname}:8009`;
        if (window.location.protocol === 'https:') {
            ws_path = `wss://wss-${location.hostname}`;
        }
        ws = new WebSocket(ws_path);
        ws.addEventListener('message', ev => {
            ws_data = JSON.parse(ev.data);
            if (ws_data.type == 'board_list') {
                $('#board').html('');
                board_list = ws_data.board_list;
                $.each(board_list,function(_,value){
                    html = `<div id='col_${value['board_uuid']}' class='col col_board'>`;
                    html += `   <h1 class="board_list">${value['board_name']}</h1>`;
                    html += '   <ul>';
                    html += '       <li>';
                    html += `           <div class='edit_board'><i onclick='renameBoard("${value['board_uuid']}");' class='material-icons' title='Rename board'>edit_note</i></div>`;
                    html += `           <div class='template_board'><i onclick='templateBoard("${value['board_uuid']}");' class='material-icons' title='Copy Template'>folder_copy</i></div>`;
                    html += `           <div class='delete_board'><i onclick='deleteBoard("${value['board_uuid']}");' class='material-icons' title='Delete board'>folder_delete</i></div>`;
                    html += `           <div class='open_board'><i onclick='openBoard("${value['path']}");' class='material-icons' title='Open board'>`;
                    if (value['board_version'] != value['current_version']) {
                        html += `sync_problem`;
                    } else {
                        html += `web`;
                    }
                    html += `       </i></div>`;
                    html += '       </li>';
                    html += '   </ul>';
                    html += `   <div class='board_last_edit'>last edit: ${value['last_edit']}</div>`;
                    html += `</div>`;
                    $('#board').append(html);
                });
            }
        });

        ws.onopen = () => {
            $('nav').removeClass('nav_disconnected');
            ws.send(JSON.stringify({
                type: 'board_list',
                username: localStorage.getItem('username')
            }));
        };

        ws.onclose = () => {
            $('nav').addClass('nav_disconnected');
            setTimeout(connect, reconnectInterval);
            reconnectInterval *= 2;
        };
    }
    connect();
    $(document).ready(function(){
        setTimeout(() => {
            $('#loader').hide('fade', 300);    
        }, 300);
    });
}
