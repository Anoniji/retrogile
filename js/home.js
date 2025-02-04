/**
 * GNU GENERAL PUBLIC LICENSE
 * Version 3, 29 June 2007
 *
 * @author Anoniji <contact@anoniji.dev>
 *
 */

var username = localStorage.getItem('username');
if (username === null) {
	location.href = '../';
} else {
    $( "#board_name" ).html(`List of "${username}" boards`);

    let ws;
    let reconnectInterval = 1000;


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
        let isDisconnected = false;

        ws.addEventListener('message', ev => {
            ws_data = JSON.parse(ev.data);
            if (ws_data.type == 'board_list') {
                $('#board').html('');
                board_list = ws_data.board_list;
                $.each(board_list,function(index,value){
                    html = `<div id='col_${index}' class='col'>`;
                    html += `   <h1 class="board_list">${value['board_name']}`;
                    html += `       <i onclick='openBoard("${value['path']}");' class='open_icon material-icons' title='Open board'>`;

                    if (value['board_version'] != value['current_version']) {
                        html += `sync_problem`;
                    } else {
                        html += `open_in_new`;
                    }

                    html += `       </i>`;
                    html += `   </h1>`;
                    html += `   <div class='board_last_edit'>last edit: ${value['last_edit']}</div>`;
                    html += `</div>`;
                    $('#board').append(html);
                });
                if (!isDisconnected) {
                    ws.close();
                    isDisconnected = true;
                }
            }
        });

        ws.onopen = () => {
            ws.send(JSON.stringify({
                type: 'board_list',
                username: localStorage.getItem('username')
            }));
        };

        ws.onclose = () => {
            if (!isDisconnected) {
                setTimeout(connect, reconnectInterval);
                reconnectInterval *= 2;
            }
        };
    }
    connect();
    $(document).ready(function(){
        setTimeout(() => {
            $('#loader').hide('fade', 300);    
        }, 300);
    });
}
