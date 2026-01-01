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

document.addEventListener("contextmenu", function (e) { e.preventDefault() });
function detectDevTool(e) { isNaN(+e) && (e = 100); var t = +new Date; debugger; var n = +new Date; (isNaN(t) || isNaN(n) || n - t > e) && (window.fetch = window.WebSocket = console.error) }

function removeNonAlphanumericSpace(str) {
    if (!str) return false;
    return str.replace(/[^a-zA-Z0-9 ]/g, '');
}

function showNotification(type, user, message) {
    if(!$('.notification').length) {
        var notification = $(`<div class="notification notif_${type}">`);
        $(`.notif_${type}`).hide();
        notification.append(`<i class="material-icons">circle_notifications</i> <span><b>${user}</b> ${message}</span>`);
        $('body #notifications').append(notification);
        notification.slideDown(300);
    }
}

var username = localStorage.getItem('username');
if (username === null) {
    location.href = '../';
} else {
    $("#board_name").html(`{{ translates.home_js_1 }}"${username}"{{ translates.home_js_2 }}`);

    let ws;
    let reconnectInterval = 1000;
    let needReload = false;

    function renameBoard(board_uuid) {
        if (!board_uuid) return;
        let board_name = prompt('{{ translates.home_js_3 }}');
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
        let new_name = prompt('{{ translates.home_js_4 }}');
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
        let check_confirm = confirm('{{ translates.home_js_5 }}');
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
        const hostname = location.hostname.replace(/^www\./, '');
        ws_path = 'ws://';
        if (window.location.protocol === 'https:') {
            ws_path = 'wss://';
        }

        if ("{{ ws_subdomain }}" != "") {
            ws_path = `${ws_path}{{ ws_subdomain }}${hostname}`;
        } else {
            ws_path = `${ws_path}${hostname}:8009`;
        }
        ws = new WebSocket(`${ws_path}/?token={{ ws_session }}`);
        ws.addEventListener('message', ev => {
            ws_data = JSON.parse(ev.data);
            detectDevTool();
            if (ws_data.type == 'board_list') {
                $('#board_access_bloc .content').html('<ul></ul>');
                board_list = ws_data.board_list;
                if (board_list.length == 0) {
                    $('#board_access_bloc .content ul').append("<li>{{ translates.home_js_11 }}</li>");
                    return;
                }
                $.each(board_list, function (_, value) {
                    html = `<li id='col_${value['board_uuid']}' class='col col_board'>`;
                    html += `   <h1 onclick='openBoard("${value['path']}");' title='{{ translates.home_js_9 }}'>${value['board_name']} <i class="material-icons">`;

                    if (value['board_version'] != value['current_version']) {
                        html += `sync_problem`;
                    }

                    html += `</i></h1>`;
                    html += `   <div class='edit_board'><i onclick='renameBoard("${value['board_uuid']}");' class='material-icons' title='{{ translates.home_js_6 }}'>edit_note</i></div>`;
                    html += `   <div class='delete_board'><i onclick='deleteBoard("${value['board_uuid']}");' class='material-icons' title='{{ translates.home_js_8 }}'>delete_sweep</i></div>`;
                    html += `   <div class='template_board'><i onclick='templateBoard("${value['board_uuid']}");' class='material-icons' title='{{ translates.home_js_7 }}'>library_add</i></div>`;
                    html += `   <div class='board_last_edit'>{{ translates.home_js_10 }}${value['last_edit']}</div>`;
                    html += `</li>`;
                    $('#board_access_bloc .content ul').append(html);
                });
                $('#search').show();
            }
        });

        ws.onopen = () => {
            reconnectInterval = 1000;
            if (needReload) {
                window.location.reload();
            } else {
                $('.notif_ws').slideUp(300, function() {
                    $(this).remove();
                })
                ws.send(JSON.stringify({
                    type: 'board_list',
                    username: localStorage.getItem('username')
                }));
            }
        };

        ws.onclose = () => {
            showNotification('ws', '{{ translates.ws_1 }}', '{{ translates.ws_2 }}');
            if (window.WebSocket) {
                setTimeout(connect, reconnectInterval);
                reconnectInterval *= 2;
                if(reconnectInterval > 8000) { needReload = true; reconnectInterval = 8000; }
            }
        };
    }
    connect();
}

$('#search').on('input', function() {
    var searchTerm = $(this).val().toLowerCase();
    $('#board_access_bloc .content ul li').each(function() {
        var nom = $(this).find('h1').text().toLowerCase();
        if (nom.indexOf(searchTerm) > -1) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
}).on('keydown', function(e) {
    if (e.key === 'Escape') {
        $(this).val('');
        $('#board_access_bloc .content ul li').show();
    }
});
