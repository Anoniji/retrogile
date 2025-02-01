/**
 * GNU GENERAL PUBLIC LICENSE
 * Version 3, 29 June 2007
 *
 * @author Anoniji <contact@anoniji.dev>
 *
 */

function removeNonAlphanumeric(str) {
    if (!str) return false;
    return str.replace(/[^a-zA-Z0-9]/g, '');
}

function removeNonNumeric(str) {
    if (!str) return false;
    return str.replace(/[^0-9]/g, '');
}

function generateColumnBoundaries(numColumns, sectionWidth) {
    const boundaries = [];
    for (let i = 0; i < numColumns; i++) {
        boundaries.push(Math.round(sectionWidth * i));
    }
    return boundaries;
}

function rgbToHex(rgbValue) {
    const match = rgbValue.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    if (!match) {
        throw new Error('Format RGB invalide');
    }
    let r = parseInt(match[1], 10);
    let g = parseInt(match[2], 10);
    let b = parseInt(match[3], 10);

    r = r.toString(16);
    g = g.toString(16);
    b = b.toString(16);

    r = r.length === 1 ? '0' + r : r;
    g = g.length === 1 ? '0' + g : g;
    b = b.length === 1 ? '0' + b : b;

    return '#' + r + g + b;
}

var username = localStorage.getItem('username');
if (username === null) {
    const pathname = window.location.pathname;
    const lastpart = pathname.split('/').pop();
    location.href = `../#${lastpart}`;
}

$(function () { $('#console').accordion({ collapsible: true, active: false, heightStyle: 'content' }); });

function showNotification(user, message) {
    var notification = $('<div class="notification">');
    notification.append(`<b>${user}</b> ${message}`);
    $('body #notifications').append(notification);
    notification.slideDown(300).delay(2000).slideUp(300, function() {
        $(this).remove();
    });
}

function cardTextSize(className, action, save = false) {
    const elements = document.querySelectorAll(`.${className}`);
    elements.forEach(element => {
        const currentSize = parseInt(window.getComputedStyle(element).fontSize);
        let newSize = currentSize + action;

        newSize = Math.max(8, Math.min(newSize, 32));
        element.style.fontSize = `${newSize}px`;
        if (save) {
            localStorage.setItem(`${className}-fontSize`, newSize);
        }
    });
}

function applySavedSize(className) {
    const savedSize = localStorage.getItem(`${className}-fontSize`);
    if (savedSize) {
        const elements = document.querySelectorAll(`.${className}`);
        elements.forEach(element => {
            element.style.fontSize = `${savedSize}px`;
        });
    }
}

function play_confetti(duration = 800) {
    $('#board_confetti').prop('disabled', true);
    const canvas = document.createElement('canvas');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    document.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');

    const confettiCount = 500;
    const confetti = [];
    for (let i = 0; i < confettiCount; i++) {
        confetti.push({
            x: Math.random() * canvas.width,
            y: canvas.height,
            width: Math.random() * 4 + 5,
            height: Math.random() * 4 + 5,
            angle: Math.random() * 2 * Math.PI,
            speed: Math.random() * 8 + 1,
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

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function customPrompt(col_id, message, defaultValue) {
    $('.custom-prompt').remove();
    const dialog = document.createElement('li');
    dialog.classList.add('custom-prompt');
    dialog.classList.add('unsortable');

    const input = document.createElement('textarea');
    input.type = 'text';
    input.value = defaultValue || '';
    input.placeholder = message;
    dialog.appendChild(input);

    const button = document.createElement('button');
    button.textContent = 'OK';
    dialog.appendChild(button);

    const el = document.querySelector(`#col_${col_id} ul`);
    el.prepend(dialog);

    $(`#col_${col_id} ul`).scrollTop(0);
    $('.custom-prompt textarea').focus();

    if (defaultValue) {
        input.style.height = 'auto';
        input.style.height = (input.scrollHeight - 20) + 'px';
    }

    return new Promise((resolve) => {
        button.addEventListener('click', () => {
            const value = escapeHtml(input.value);
            dialog.remove();
            resolve(value);
        });

        input.addEventListener('input', () => {
            input.style.height = 'auto';
            input.style.height = (input.scrollHeight - 20) + 'px';
        });

        input.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') {
                const value = escapeHtml(input.value);
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
    const now = new Date();
    const hour = now.getHours();
    const minute = now.getMinutes();
    const second = now.getSeconds();
    var board_log = $('#board_log');
    board_log.append(`[${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}.${second.toString().padStart(2, '0')}] <span style='color: ${color}'>${text}</span><br>`);
    var log_height = board_log[0].scrollHeight;
    board_log.animate({ scrollTop: log_height }, 200);
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

function board_timer(seconds) {
    const $countdownElement = $('#board_timer .title');
    clearInterval($countdownElement.data('intervalId'));
    const countDownDate = new Date().getTime() + seconds * 1000;
    const updateCount = () => {
        const now = new Date().getTime();
        const distance = countDownDate - now;
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        $countdownElement.text(`${minutes}m ${seconds}s`);
        if (distance < 0) {
            clearInterval($countdownElement.data('intervalId'));
            $countdownElement.text('Timer');
            $('#wallpaper2').effect('highlight');
        }
    };
    const intervalId = setInterval(updateCount, 1000);
    $countdownElement.data('intervalId', intervalId);
    updateCount();
}

function board_vote(maxVote) {
    $('#board_vote .title').html(maxVote);
}

function board_vote_order() {
    $('.sortable').each(function () {
        const $sortableList = $(this);
        $sortableList.find('li').sort(function (a, b) {
            const aVotes = parseInt($(a).find('.votes').text());
            const bVotes = parseInt($(b).find('.votes').text());
            return bVotes - aVotes;
        }).appendTo($sortableList);
    });
}

var stockList = {};
let timeout;
var colLst;

function scrollFix() {
    $board = $('#board');
    clearTimeout(timeout);
    timeout = setTimeout(function() {
        let scrollPosition = $board.scrollLeft();
        if (!colLst.includes(scrollPosition)) {
            adjustScrollbar(scrollPosition);
        }
    }, 200);

    function adjustScrollbar(position) {
        let closestPosition = colLst[0];
        let minDifference = Math.abs(position - closestPosition);

        for (let i = 1; i < colLst.length; i++) {
            let difference = Math.abs(position - colLst[i]);
            if (difference < minDifference) {
                minDifference = difference;
                closestPosition = colLst[i];
            }
        }

        $board.animate({
            scrollLeft: closestPosition
        }, 500);
    }
}

if (username !== null) {
    let ws;
    let reconnectInterval = 1000;
    let board_author;
    let user_id = false;
    var pos_x;
    var pos_y;
    var curr_highlightUser;
    var maxVoteTotal;

    $('#board').scroll(function() {
        scrollFix();
    });

    function board_copy_link() {
        try {
            navigator.permissions.query({ name: 'clipboard-write' }).then((result) => {
                if (result.state == 'granted' || result.state == 'prompt') {
                    showNotification('(!)', 'Board url copied');
                    navigator.clipboard.writeText(window.location.href);
                }
            });
        } catch (err) {
            console.error('Error_copy:', err);
        }
    };

    function startTimer() {
        if (board_author != username) return;
        let timerInSeconds = prompt('Timer in secondes');

        timerInSeconds = removeNonNumeric(timerInSeconds);
        if (timerInSeconds && timerInSeconds != '') {
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
        if (maxVote && maxVote != '') {
            ws.send(JSON.stringify({
                type: 'start_vote',
                board_id: board_id,
                maxVote: maxVote,
            }));
        }
    }

    $("#custom_color").change(function() {
        ws.send(JSON.stringify({
            type: 'user_color',
            board_id: board_id,
            username: username,
            custom_color: $('#custom_color').val(),
        }));
        $(this).attr("type", "hidden");
    });
 
    function setColor() {
        const $input = $("#custom_color");
        const currentType = $input.attr("type");
        if (currentType === "hidden") {
            current_custom_color = $(`#users div[data-username=${username}]`).children().css('color');
            $input.val(rgbToHex(current_custom_color)).attr("type", "color");
        } else {
            $input.attr("type", "hidden");
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
        customPrompt(col_id, 'Add new Card', '').then(cardContent => {
            if (cardContent) {
                ws.send(JSON.stringify({
                    type: 'card_add',
                    pos: $(`#col_${col_id} ul`).children('li').length,
                    author: username,
                    board_id: board_id,
                    user_id: user_id,
                    col_id: col_id,
                    votes: 0,
                    cardContent: cardContent.trim(),
                }));
            }
        });
    }

    function mergeCard() {
        if (board_author != username) return;
        if ($('#board_merge_bloc i').text() == 'call_merge') {
            $('#board_merge_bloc i').text('merge')
            $('.child_drop').show();
        } else {
            $('#board_merge_bloc i').text('call_merge')
            $('.child_drop').hide();
        }        
    }

    function unmergeCard(col_id, parent, cardPos) {
        if (board_author != username) return;
        if ($('#board_merge_bloc i').text() == 'call_merge') return;
        ws.send(JSON.stringify({
            type: 'card_unmerge',
            author: username,
            board_id: board_id,
            user_id: user_id,
            col_id: col_id,
            card_uuid: parent,
            cardContent: cardPos,
        }));      
    }

    function editCard(card_uuid) {
        col_id = $(`.uuid_${card_uuid}`).parent().parent().attr('data-col');
        customPrompt(col_id, 'Editing Card content', $(`.uuid_${card_uuid} .info_content`).text()).then(cardContent => {
            if (cardContent) {
                ws.send(JSON.stringify({
                    type: 'card_edit',
                    author: username,
                    board_id: board_id,
                    user_id: user_id,
                    col_id: col_id,
                    card_uuid: card_uuid,
                    cardContent: cardContent.trim(),
                }));
            }
        });
    }

    function voteCard(card_uuid) {
        col_id = $(`.uuid_${card_uuid}`).parent().parent().attr('data-col');
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
                    card_uuid: card_uuid,
                }));
            }
        }
    }

    function deleteCard(card_uuid) {
        col_id = $(`.uuid_${card_uuid}`).parent().parent().attr('data-col').toString();
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
        colName = removeNonAlphanumeric(colName);
        if (colName) {
            ws.send(JSON.stringify({
                type: 'col_add',
                author: username,
                board_id: board_id,
                user_id: user_id,
                colName: colName,
            }));
        }
    }

    function moveCol(move, col_index) {
        if (board_author != username) return;
        const elements = $('[data-col]');
        const valeursDataCol = [];
        elements.each(function () {
            valeursDataCol.push($(this).data('col').toString());
        });

        const index = valeursDataCol.indexOf(col_index);
        const newOrder = [...valeursDataCol];

        if (move == "left") {
            if (index > 0) {
                [newOrder[index], newOrder[index - 1]] = [newOrder[index - 1], newOrder[index]];
            }
        } else {
            if (index < newOrder.length - 1) {
                [newOrder[index], newOrder[index + 1]] = [newOrder[index + 1], newOrder[index]];
            }
        }
        ws.send(JSON.stringify({
            type: 'col_reorder',
            author: username,
            board_id: board_id,
            user_id: user_id,
            colName: newOrder,
            uuidList: false,
        }));
    }

    function viewCardToggle() {
        ws.send(JSON.stringify({
            type: 'card_view',
            author: username,
            board_id: board_id,
            user_id: user_id,
        }));
    }

    function moveToChild(parentId, childId) {
        ws.send(JSON.stringify({
            type: 'card_parent',
            author: username,
            board_id: board_id,
            user_id: user_id,
            col_id: false,
            card_uuid: parentId,
            cardContent: childId,
        }));
    }

    function orderCol(name, data) {
        uuid_list = []

        $.each(data, function (_, element) {
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
            uuidList: uuid_list,
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
        if (curr_highlightUser != Husername) {
            $('#users div').each(function () {
                const $user = $(this);
                if ($user.attr('data-username') == Husername) {
                    $user.animate({ 'opacity': 1 }, 300);
                } else {
                    $user.animate({ 'opacity': .2 }, 300);
                }
            });

            $('.col li').each(function () {
                const $li = $(this);
                if ($li.attr('data-username') == Husername) {
                    $li.css('display', 'block');
                } else {
                    $li.css('display', 'none');
                }
            });
            curr_highlightUser = Husername;
        } else {
            $('#users div').each(function () {
                $(this).animate({ 'opacity': 1 }, 300);
            });

            $('.col li').each(function () {
                $(this).css('display', 'block');
            });
            curr_highlightUser = false;
        }
    }

    function connect() {
        ws_path = `ws://${location.hostname}:8009`;
        if (window.location.protocol === 'https:') {
            ws_path = `wss://wss-${location.hostname}`;
        }
        ws = new WebSocket(ws_path);

        $(document).on('mousemove', function (event) {
            pos_x = event.pageX;
            pos_y = event.pageY;
        });

        function mouse_position() {
            ws.send(JSON.stringify({
                type: 'cursor_user',
                board_id: board_id,
                pos_x: pos_x,
                pos_y: pos_y,
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
                $.each(ws_data.users_list, function (index, value) {
                    if (user_id && user_id != index && value.board_id == board_id) {
                        $('#cursors').append(`<div id='cursor_${index}' class='cursor'><div class='username'>${value.username}</div></div>`)
                    }
                    if (value.board_id == board_id) {
                        var $div_username = $(`#users div[data-username=${value.username}]`);
                        if ($($div_username).length > 0) {
                            var currentCount = parseInt($div_username.attr('data-count'));
                            $div_username.attr('data-count', currentCount + 1);
                        } else {
                            $('#users').append(`<div id='user_${index}' class='user' title='${value.username}' data-username='${value.username}' data-count='1' onclick='highlightUser("${value.username}");'><i class='material-icons' style='color: ${value.color}'>face</i></div>`)
                            $(document).tooltip({ position: { my: 'center top', at: 'center bottom' } });
                        }
                    }
                });
            } else if (ws_data.type == 'user_add') {
                if (user_id != ws_data.user_id && ws_data.board_id == board_id) {
                    log(`< ${ws_data.username} > connected`, 'yellow');
                    $('#cursors').append(`<div id='cursor_${ws_data.user_id}' class='cursor'><div class='username'>${ws_data.username}</div></div>`);

                    var $div_username = $(`#users div[data-username=${ws_data.username}]`);
                    if ($($div_username).length > 0) {
                        var currentCount = parseInt($div_username.attr('data-count'));
                        $div_username.attr('data-count', currentCount + 1);
                    } else {
                        $('#users').append(`<div id='user_${ws_data.user_id}' class='user' title='${ws_data.username}' data-username='${ws_data.username}' data-count='1' onclick='highlightUser("${ws_data.username}");'><i class='material-icons' style='color: ${ws_data.color}'>face</i></div>`)
                        $(document).tooltip({ position: { my: 'center top', at: 'center bottom' } });
                    }
                }
            } else if (ws_data.type == 'user_remove') {
                log(`< ${ws_data.username} > disconnected`, 'red');
                $(`#cursor_${ws_data.user_id}`).hide('fade', 300).remove();

                var $div_username = $(`#users div[data-username=${ws_data.username}]`);
                var currentCount = parseInt($div_username.attr('data-count'));
                if (currentCount == 1) {
                    $(`#user_${ws_data.user_id}`).hide('fade', 300).remove();
                } else {
                    $div_username.attr('data-count', currentCount - 1);
                }
            } else if (ws_data.type == 'cursor_user') {
                if (user_id != ws_data.user_id) {
                    if (ws_data.pos_y && ws_data.pos_x) {
                        $(`#cursor_${ws_data.user_id}`).animate({ top: `${ws_data.pos_y}px`, left: `${ws_data.pos_x}px` }, 300);
                    }
                }
            } else if (ws_data.type == 'user_color') {
                var $div_username = $(`#users div[data-username=${ws_data.username}]`);
                $div_username.children().css('color', ws_data.custom_color);
            } else if (ws_data.type == 'board_info') {
                board_author = ws_data.board_info.author;
                board_data = ws_data.board_info.data;
                check_timer = ws_data.board_info.timer;
                check_votes = ws_data.board_info.votes;
                list_votes = ws_data.board_info.votes_list;
                list_users = ws_data.board_info.users_list;

                if (check_timer) {
                    const now = new Date();
                    difSecs = parseInt((check_timer - now.getTime()) / 1000);
                    if (difSecs > 0) {
                        board_timer(difSecs);
                    }
                }

                if (check_votes) {
                    if (username in list_votes) {
                        $('#board_vote .title').html(list_votes[username]);
                    }
                }

                const url = window.location.href;
                if (!url.startsWith("https://") && !url.includes("localhost") && !url.includes("127.0.0.1")) {
                    $('#board_copy_link').remove();
                }

                $('#board').html('');
                if (!board_data) {
                    $('#board_name').html('This board does not exist, <a href="../">return to home page</a>');
                    $('#board_timer, #board_vote, #r_menu').remove();
                    return;
                }

                if (board_author != username) {
                    $('#board_add_bloc, #board_merge_bloc').remove();
                    $('#board_timer, #board_vote').prop('disabled', true);
                } else {
                    $('#board_add_bloc, #board_merge_bloc').show();
                }

                if (list_users.hasOwnProperty(username)) {
                    if (list_users[username]['card_visibility']) {
                        $('#board_cards_visibility .material-icons').html('visibility_off');
                        $('#board_cards_visibility .title').html('Hide my cards');
                    }
                }

                $.each(board_data, function (index, value) {
                    html = `<div id='col_${index}' data-col='${index}' class='col'><h1>${index}<i onclick='addCard("${index}");' class='add_icon material-icons'>add</i>`;
                    if (board_author == username) {
                        html += `<i onclick='deleteCol("${index}");' class='drop_icon material-icons'>delete</i>`;
                        html += `<i onclick='moveCol("left", "${index}");' class='left_icon material-icons'>keyboard_double_arrow_left</i>`;
                        html += `<i onclick='moveCol("right", "${index}");' class='right_icon material-icons'>keyboard_double_arrow_right</i>`;
                    }
                    html += `</h1><ul class='sortable'></ul></div>`;
                    $('#board').append(html);

                    const entries = Object.entries(value);
                    entries.sort((a, b) => a[1].pos - b[1].pos);
                    const sortedData = Object.fromEntries(entries);

                    $.each(sortedData, function (uuid, value) {
                        html = `<li class='ui-state-default uuid_${uuid} pos_${value.pos}' data-username="${value.author}" data-uuid="${uuid}">`;
                        html += `<div class='card_icon'>`;
                        html += `<div class='info_author'>by ${value.author}</div>`;
                        if (value.author == username) {
                            html += `<div class='edit_icon' onclick='editCard("${uuid}");'>
                                <i class='material-icons'>edit</i>
                                <div class='type'>Edit</div>
                            </div>`;
                            html += `<div class='delete_icon' onclick='deleteCard("${uuid}");'>
                                <i class='material-icons'>delete</i>
                                <div class='type'>Delete</div>
                            </div>`;
                        }
                        html += `</div>`;
                        html += `<div class='votes' onclick='voteCard("${uuid}");'>${value.votes}</div>
                            <div class='info_content'>${value.content}</div>`

                        child_cnt = 0;
                        $.each(value.children, function (_, child) {
                            html += `<div class="card_child"><i class='material-icons' onclick='unmergeCard("${index}", "${uuid}", "${child_cnt}");'>radio_button_checked</i> ${child.author}: ${child.content}</div>`;
                            child_cnt += 1;
                        });

                        html += `    <div class='child_drop' data-parentId='${uuid}'>
                                    </div>
                            </div>`;
                        html += `</li>`;
                        $(`#col_${index} .sortable`).append(html);
                    });
                    $(`#col_${index} .sortable`).sortable({ items: 'li:not(.unsortable)', placeholder: 'ui-state-highlight', connectWith: '.sortable, .child_drop', update: function (e, u) { var l = []; $(this).children().each(function (i, e) { l.push($(e).attr('class')) }); orderCol($(this).parent().attr('id'), l) } });
                    $(`#col_${index} .child_drop`).sortable({ 
                        items: 'li:not(.unsortable)',
                        placeholder: 'ui-state-highlight',
                        connectWith: '.sortable, .child_drop',
                        update: function (e, u) { $('.child_drop').each(function (_, e) { if($(e).children().length) { $(e).children().each(function (_, c) { moveToChild($(e).attr('data-parentId'), $(c).attr('data-uuid')); return; }) } }) }
                    });
                });

                colLst = generateColumnBoundaries(Object.keys(board_data).length, $('.col').width() + 32);
                $('#board_name').html(ws_data.board_info.board_name);
                if (curr_highlightUser) {
                    let tmps_highlightUser = curr_highlightUser;
                    curr_highlightUser = false;
                    highlightUser(tmps_highlightUser);
                }

                if (board_author == username && $('#board_merge_bloc i').text() == 'merge') {
                    $('.child_drop').show();
                }

                applySavedSize("info_content");
            } else if (ws_data.type == 'start_timer') {
                board_timer(ws_data.timerInSeconds);
            } else if (ws_data.type == 'start_confetti') {
                play_confetti();
            } else if (ws_data.type == 'start_vote') {
                maxVoteTotal = $('#users .user').length * ws_data.maxVote;
                $('.votes').text('0');
                log(`< Vote Session > started`, 'red');
                board_vote(ws_data.maxVote);
            } else if (ws_data.type == 'card_add') {
                html = `<li class='ui-state-default uuid_${ws_data.card_uuid} pos_${ws_data.card_add.pos}' data-username="${ws_data.card_add.author}" data-uuid="${ws_data.card_uuid}">`;
                html += `<div class='card_icon'>`;
                html += `<div class='info_author'>by ${ws_data.card_add.author}</div>`;
                if (ws_data.card_add.author == username) {
                    html += `<div class='edit_icon' onclick='editCard("${ws_data.card_uuid}");'>
                        <i class='material-icons'>edit</i>
                        <div class='type'>Edit</div>
                    </div>`;
                    html += `<div class='delete_icon' onclick='deleteCard("${ws_data.card_uuid}");'>
                        <i class='material-icons'>delete</i>
                        <div class='type'>Delete</div>
                    </div>`;
                }
                html += `</div>`;
                html += `<div class='votes' onclick='voteCard("${ws_data.card_uuid}");'>${parseInt(ws_data.card_add.votes)}</div>
                    <div class='info_content'>${ws_data.card_add.cardContent}</div>
                    <div class='child_drop' data-parentId='${ws_data.card_uuid}'></div>
                    </div>`;
                html += `</li>`;
                $(`#col_${ws_data.card_add.col_id} .sortable`).append(html);
                $(`#col_${ws_data.card_add.col_id} .sortable`).sortable({ items: 'li:not(.unsortable)', placeholder: 'ui-state-highlight', connectWith: '.sortable, .child_drop', update: function (e, u) { var l = []; $(this).children().each(function (i, e) { l.push($(e).attr('class')) }); orderCol($(this).parent().attr('id'), l) } });
                $(`#col_${ws_data.card_add.col_id} .child_drop`).sortable({ 
                        items: 'li:not(.unsortable)',
                        placeholder: 'ui-state-highlight',
                        connectWith: '.sortable, .child_drop',
                        update: function (e, u) { $('.child_drop').each(function (_, e) { if($(e).children().length) { $(e).children().each(function (_, c) { moveToChild($(e).attr('data-parentId'), $(c).attr('data-uuid')); return; }) } }) }
                });

                if (curr_highlightUser) {
                    let tmps_highlightUser = curr_highlightUser;
                    curr_highlightUser = false;
                    highlightUser(tmps_highlightUser);
                }
                applySavedSize("info_content");
            } else if (ws_data.type == 'card_edit') {
                $(`#col_${ws_data.card_edit.col_id} ul .uuid_${ws_data.card_edit.card_uuid} .info_content`).html(ws_data.card_edit.cardContent);
            } else if (ws_data.type == 'card_view') {

                notif_txt = 'hide these cards';
                if(ws_data.card_view.visibility) {
                    notif_txt = 'show these cards';
                }

                if (ws_data.card_view.author != username) {
                    showNotification(ws_data.card_view.author, notif_txt);
                } else {
                    showNotification('You', notif_txt.replace('these', 'your'));
                    if (ws_data.card_view.hidden) {
                        $('#board_cards_visibility .material-icons').html('visibility_off');
                        $('#board_cards_visibility .title').html('Hide my cards');
                    } else {
                        $('#board_cards_visibility .material-icons').html('visibility');
                        $('#board_cards_visibility .title').html('Show my cards');
                    }
                }

                ws.send(JSON.stringify({
                    type: 'board_info',
                    board_id: board_id,
                    username: username,
                }));
            } else if (ws_data.type == 'card_vote') {
                $(`#col_${ws_data.card_vote.col_id} ul .uuid_${ws_data.card_vote.card_uuid} .votes`).html(ws_data.card_votes);
                if (board_author == username) {
                    var elementsVotes = $('.votes');
                    var totalVotes = 0;
                    elementsVotes.each(function () {
                        var valeurVote = parseInt($(this).text());
                        if (!isNaN(valeurVote)) {
                            totalVotes += valeurVote;
                        }
                    });
                    log(`< Vote Session > Total: ${totalVotes} / ${maxVoteTotal}`, 'cyan');
                }
            } else if (ws_data.type == 'card_delete') {
                $(`#col_${ws_data.card_delete.col_id} ul .uuid_${ws_data.card_delete.card_uuid}`).remove();
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
                            board_id: board_id,
                            username: username,
                        }));
                    }
                });

                sortableList.innerHTML = '';
                sortableList.appendChild(fragment);
            } else if (ws_data.type == 'col_delete') {
                $(`#col_${ws_data.col_delete.colName}`).remove();
            } else if (['force_reload', 'col_reorder', 'card_parent', 'card_unmerge', 'col_add'].includes(ws_data.type)) {
                ws.send(JSON.stringify({
                    type: 'board_info',
                    board_id: board_id,
                    username: username,
                }));
            } else {
                log(`< ${ws_data.username} > ${ws_data.content}`, 'white');
            }
        });

        document.getElementById('form').onsubmit = ev => {
            ev.preventDefault();
            const textField = document.getElementById('chat_msg');
            ws.send(JSON.stringify({
                type: 'message',
                board_id: board_id,
                content: escapeHtml(textField.value),
            }));
            textField.value = '';
        };

        ws.onopen = () => {
            $('nav').removeClass('nav_disconnected');
            ws.send(JSON.stringify({
                type: 'connect',
                board_id: board_id,
                username: localStorage.getItem('username'),
            }));

            ws.send(JSON.stringify({
                type: 'board_info',
                board_id: board_id,
                username: username,
            }));

            setInterval(function () { mouse_position() }, 2000);
        };

        ws.onclose = () => {
            showNotification('Please Wait,', 'your are disconnected!');
            $('nav').addClass('nav_disconnected');
            setTimeout(connect, reconnectInterval);
            reconnectInterval *= 2;
        };
    }
    connect();
    $(document).ready(function () {
        setTimeout(() => {
            $('#loader').hide('fade', 300);
        }, 300);
    });
}

window.onload = () => {
    applySavedSize("info_content");
};

window.onresize = function(event) {
    colLst = generateColumnBoundaries($('.col').length, $('.col').width() + 32);
    scrollFix();
};
