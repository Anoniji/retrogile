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

document.addEventListener("contextmenu",function(e){e.preventDefault()});
function detectDevTool(e) { isNaN(+e) && (e = 100); var t = +new Date; debugger; var n = +new Date; (isNaN(t) || isNaN(n) || n - t > e) && (window.fetch = window.WebSocket = console.error) }
function generateColumnBoundaries(e, n) { let r = []; for (let u = 0; u < e; u++)r.push(Math.round(n * u)); return r }
function getFirstLetters(t) { return "string" != typeof t || 0 === t.length ? "<i class='material-icons'>face</i>" : "<span>" + t.charAt(0).toUpperCase() + "</span>" }
function rgbToHex(t) { t.includes("none") && (t = t.split(" none", 1)[0]); let n = t.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/); if (!n) throw Error("Format RGB invalide"); let e = parseInt(n[1], 10), _ = parseInt(n[2], 10), i = parseInt(n[3], 10); return e = e.toString(16), _ = _.toString(16), i = i.toString(16), e = 1 === e.length ? "0" + e : e, _ = 1 === _.length ? "0" + _ : _, i = 1 === i.length ? "0" + i : i, "#" + e + _ + i }
function hexToRgb(r) { hex = r.replace("#", ""); let n = parseInt(hex.substring(0, 2), 16), s = parseInt(hex.substring(2, 4), 16), t = parseInt(hex.substring(4, 6), 16); return { r: n, g: s, b: t } }
function isLightColor(r) { let t = hexToRgb(r), _ = (299 * t.r + 587 * t.g + 114 * t.b) / 1e3; return _ > 128 }

var username = localStorage.getItem('username');
if (username === null) {
    const pathname = window.location.pathname;
    const lastpart = pathname.split('/').pop();
    location.href = `../#speed-${lastpart}`;
}

function storeWsMessages(message) {
    const storedMessages = localStorage.getItem('unsentMessages');
    let messagesArray = storedMessages ? JSON.parse(storedMessages) : [];
    messagesArray.push(message);
    localStorage.setItem('unsentMessages', JSON.stringify(messagesArray));
}

function sendWsMessage(websocket, message) {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        try {
            websocket.send(message);
        } catch (error) {
            storeWsMessages(message);
        }
    } else {
        storeWsMessages(message);
    }
}

function resendWsMessages(websocket) {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        const storedMessages = localStorage.getItem('unsentMessages');
        if (storedMessages) {
            let messagesArray = JSON.parse(storedMessages);
            messagesArray.forEach(message => {
                try {
                    websocket.send(message);
                } catch (error) {
                    console.error("Not resend:", error);
                }
            });
            localStorage.removeItem('unsentMessages');
        }
    }
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function customPrompt(col_id, message) {
    const dialog = document.createElement('div');
    dialog.classList.add('custom-prompt');

    const input = document.createElement('textarea');
    input.type = 'text';
    input.value = '';
    input.placeholder = message;
    dialog.appendChild(input);

    const el = document.querySelector(`#${col_id}`);
    el.append(dialog);
}

function board_timer(seconds) {
    const $countdownElement = $('#board_timer');
    clearInterval($countdownElement.data('intervalId'));
    const countDownDate = new Date().getTime() + seconds * 1000;
    const updateCount = () => {
        const now = new Date().getTime();
        const distance = countDownDate - now;
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        if(minutes != 0) {
            $countdownElement.html(`${minutes}m ${seconds}s <i class="material-icons">timer</i>`);
        } else {
            $countdownElement.html(`${seconds}s <i class="material-icons">timer</i>`);
        }

        if (distance < 0) {
            clearInterval($countdownElement.data('intervalId'));
            $countdownElement.text('');
            const config = [
                { id: 'good_input', label: 'good' },
                { id: 'bad_input', label: 'bad' },
                { id: 'stape_input', label: 'start_stop' }
            ];

            config.forEach(({ id, label }) => {
                const cardContent = escapeHtml($(`#${id} textarea`).val());
                $(`#${id} textarea`).prop('disabled', true);
                if(cardContent != '') {
                    addCard(label, cardContent);
                }
            });

            goto_page('loop_speed');
        }
    };
    const intervalId = setInterval(updateCount, 1000);
    $countdownElement.data('intervalId', intervalId);
    updateCount();
}

var user_pos = 0
function user_timer(seconds, lst) {
    const $countdownElement = $('#board_timer');
    clearInterval($countdownElement.data('intervalId'));
    const countDownDate = new Date().getTime() + seconds * 1000;
    if(lst[user_pos]) {
        $('#board_curr_user').html(`<i class="material-icons">person</i> ${lst[user_pos]}`);
        const config = [
            { id: 'col_good', cnt_id: 'good_input' },
            { id: 'col_bad', cnt_id: 'bad_input' },
            { id: 'col_start_stop', cnt_id: 'stape_input' }
        ];

        config.forEach(({ id, cnt_id }) => {
            const element = $(`#${id} [data-username="${lst[user_pos]}"] .info_content`).first();
            if(element){
                $(`#${cnt_id} div`).text(element.text());
            } else {
                $(`#${cnt_id} div`).text('{{ translates.speed_js_3 }}');
            }
        });


        const updateCount = () => {
            const now = new Date().getTime();
            const distance = countDownDate - now;
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            if(minutes != 0) {
                $countdownElement.html(`${minutes}m ${seconds}s <i class="material-icons">timer</i>`);
            } else {
                $countdownElement.html(`${seconds}s <i class="material-icons">timer</i>`);
            }

            if (distance < 0) {
                if (user_pos < lst.length) {
                    user_pos += 1;
                    user_timer(60, lst);
                } else {
                    clearInterval($countdownElement.data('intervalId'));
                    $countdownElement.text('');
                    goto_page('votes');
                }
            }
        };

        const intervalId = setInterval(updateCount, 1000);
        $countdownElement.data('intervalId', intervalId);
        updateCount();
    } else {
        $('#board_curr_user').html('');
        clearInterval($countdownElement.data('intervalId'));
        $countdownElement.text('');
        goto_page('votes');
    }
}

function board_vote(maxVote) {
    if (maxVote == 0) {
        $('#speed_board_vote').text('');
        $('nav #vote_progress, #board-votes-menu, .vote_actions').fadeOut(300);
    } else {
        $('#speed_board_vote').text(maxVote);
        $('nav #vote_progress, #board-votes-menu, .vote_actions').fadeIn(300);
    }
}

var stockList = {};
let timeout;
var colLst;

if (username !== null) {
    let ws;
    let reconnectInterval = 1000;
    let needReload = false;
    let board_author;
    let user_id = false;
    var user_list = [];
    var goto_page_state = false;

    var maxVoteTotal;

    function startVote() {
        if (board_author != username) return;
        sendWsMessage(ws, JSON.stringify({
            type: 'start_vote',
            maxVote: 3,
        }));
    }

    $("#custom_color").change(function () {
        custom_color = $('#custom_color').val();
        sendWsMessage(ws, JSON.stringify({
            type: 'user_color',
            custom_color: custom_color,
        }));
        $(this).attr("type", "hidden");
    });

    function setColor() {
        const $input = $("#custom_color");
        const currentType = $input.attr("type");
        if (currentType === "hidden") {
            current_custom_color = $(`#users div[data-username=${username}]`).css('background');
            $input.val(rgbToHex(current_custom_color)).attr("type", "color");
        } else {
            $input.attr("type", "hidden");
        }
    }

    function start_timer() {
        sendWsMessage(ws, JSON.stringify({
            type: 'start_timer',
            timerInSeconds: timerInSeconds,
        }));
    }

    function addCard(col_id, cardContent) {
        sendWsMessage(ws, JSON.stringify({
            type: 'card_add',
            pos: 1,
            user_id: user_id,
            col_id: col_id,
            votes: 0,
            cardContent: cardContent.trim(),
        }));
    }

    function end_speed() {
        const cardContent = escapeHtml($(`#actions_input textarea`).val());
        $(`#actions_input textarea, #end_speed`).prop('disabled', true);
        if(cardContent != '') {
            addCard('actions', cardContent);
        }
        goto_page('end_speed');
    }

    function voteCard(card_uuid, act) {
        const now = Date.now();
        const lastExecution = voteCard.lastExecution || 0;
        if (now - lastExecution < 1000) {
            return;
        }
        voteCard.lastExecution = now;

        var col_id = $(`.uuid_${card_uuid}`).parent().parent().attr('data-col');
        var maxVote = $('#speed_board_vote').text();

        if (maxVote == "0") return;

        if (!isNaN(maxVote)) {
            maxVote = parseInt(maxVote);
            maxVote -= 1
            $('#speed_board_vote').text(maxVote);
            sendWsMessage(ws, JSON.stringify({
                type: 'card_vote',
                user_id: user_id,
                col_id: col_id,
                card_uuid: card_uuid,
            }));
            $(`.uuid_${card_uuid} .votes`).effect('highlight', { color: "#f2f2f2" }, 700);
        }
    }

    function goto_page(speed_type='start_speed') {
        goto_page_state = speed_type
        if (board_author == username) {
            sendWsMessage(ws, JSON.stringify({type: 'message', content: speed_type}));
        }
    }

    function connect() {
        ws_path = `ws://${location.hostname}:8009`;
        if (window.location.protocol === 'https:') {
            ws_path = `wss://wss-${location.hostname}`;
        }
        ws = new WebSocket(`${ws_path}/?token={{ ws_session }}`);
        ws.addEventListener('message', ev => {
            ws_data = JSON.parse(ev.data);
            detectDevTool();
            if (ws_data.type == 'connect_status') {
                if (!ws_data.error) {
                    user_id = ws_data.user_id;
                    user_color = ws_data.user_color;
                    $('.board-color, nav #vote_progress').animate({ backgroundColor: user_color }, 300);
                }
            } else if (ws_data.type == 'users_list') {
                $('#users').html('');
                $.each(ws_data.users_list, function (index, value) {
                    var $div_username = $(`#users div[data-username=${value.username}]`);
                    if ($($div_username).length > 0) {
                        var currentCount = parseInt($div_username.attr('data-count'));
                        $div_username.attr('data-count', currentCount + 1);
                    } else {
                        if (isLightColor(value.color)) {
                            txt_color = 'color: #333;';
                        } else {
                            txt_color = 'color: #f2f2f2;';
                        }

                        $('#users').append(`<div id='user_${index}' class='user' title='${value.username}' data-username='${value.username}' data-count='1' style='${txt_color}background: ${value.color}'>${getFirstLetters(value.username)}<div class='user_notif_status'></div></div>`);
                        $(document).tooltip({ position: { my: 'center top', at: 'center bottom' } });
                    }
                });
            } else if (ws_data.type == 'user_add') {
                if (user_id != ws_data.user_id) {
                    var $div_username = $(`#users div[data-username=${ws_data.username}]`);
                    if ($($div_username).length > 0) {
                        var currentCount = parseInt($div_username.attr('data-count'));
                        $div_username.attr('data-count', currentCount + 1);
                    } else {
                        if (isLightColor(ws_data.color)) {
                            txt_color = 'color: #333;';
                        } else {
                            txt_color = 'color: #f2f2f2;';
                        }
                        $('#users').append(`<div id='user_${ws_data.user_id}' class='user' title='${ws_data.username}' data-username='${ws_data.username}' data-count='1' style='${txt_color}background: ${ws_data.color}'></div>`);
                        $(`#user_${ws_data.user_id}`).hide().html(getFirstLetters(ws_data.username)).slideDown(300, function () {
                        });
                        $(document).tooltip({ position: { my: 'center top', at: 'center bottom' } });
                    }
                }
            } else if (ws_data.type == 'user_color') {
                var $div_username = $(`#users div[data-username=${ws_data.username}]`);
                if (isLightColor(ws_data.custom_color)) {
                    $div_username.css('color', '#333');
                } else {
                    $div_username.css('color', '#f2f2f2');
                }
                $div_username.css('background', ws_data.custom_color);
                if (username == ws_data.username) {
                    $('.board-color, #vote_progress').animate({ backgroundColor: ws_data.custom_color }, 300);
                }

                ws.send(JSON.stringify({ type: 'board_info' }));
            } else if (ws_data.type == 'board_info') {
                board_author = ws_data.board_info.author;
                board_data = ws_data.board_info.data;
                check_timer = ws_data.board_info.timer;
                check_votes = ws_data.board_info.votes;
                list_votes = ws_data.board_info.votes_list;
                list_users = ws_data.board_info.users_list;

                if (board_author == username && user_list.length == 0 && !goto_page_state) {
                    $('#speed_list').html('<button id="goto_page" onclick="goto_page();">{{ translates.speed_js_2 }}</button>')
                }

                if (check_votes) {
                    if (username in list_votes) {
                        $('#board_vote .title').html(list_votes[username]);
                        sendWsMessage(ws, JSON.stringify({
                            type: 'stats_vote',
                        }));
                    }
                }

                $('#board').html('');
                if (!board_data) {
                    $('#speed_board_name').html("{{ translates.board_js_12 }}<a href='../'>{{ translates.board_js_13 }}</a>");
                    $('#board_vote, #r_menu').remove();
                    return;
                }

                col_class = 'col';
                if (board_author != username) {
                    $('#board_add_bloc, #board_merge_bloc').remove();
                    $('#board_vote').prop('disabled', true);
                } else {
                    $('#board_merge_bloc').show();
                    if (Object.keys(board_data).length < 5) {
                        $('#board_add_bloc').show();
                    }
                }

                if (Object.keys(board_data).length == 5) {
                    col_class += ' col_5';
                }

                user_card_visibility = false;
                if (list_users.hasOwnProperty(username)) {
                    if (list_users[username]['card_visibility']) {
                        user_card_visibility = true;
                        $('#board_cards_visibility .material-icons').html('visibility_off');
                        $('#board_cards_visibility .title').html('{{ translates.board_js_19 }}');
                    }
                }

                $.each(board_data, function (index, value) {
                    html = `<div id='col_${index}' data-col='${index}' class='${col_class}'><h1>${index}</h1><ul></ul></div>`;
                    $('#board').append(html);

                    const entries = Object.entries(value);
                    entries.sort((a, b) => a[1].pos - b[1].pos);
                    const sortedData = Object.fromEntries(entries);

                    $.each(sortedData, function (uuid, value) {
                        html = `<li class='ui-state-default uuid_${uuid} pos_${value.pos}`

                        html += `' data-username="${value.author}" data-uuid="${uuid}" style="background-color: ${value.username_color}; border-color: ${value.username_color}">`;
                        html += `<div class='card_icon' style='`;
                        if (isLightColor(value.username_color)) {
                            html += 'color: #333';
                        } else {
                            html += 'color: #f2f2f2';
                        }
                        html += `'>`;
                        html += `<div class='info_author'><i class="material-icons">person</i><b>${value.author}</b></div>`;
                        html += `</div>`;

                        html += `<div class="card_content`;

                        if (value.author == username && !user_card_visibility) {
                            html += ' card_not_visible';
                        }

                        html += `">`;

                        html += `<div class='votes' style='background-color: ${value.username_color}`;
                        if (isLightColor(value.username_color)) {
                            html += '; color: #333';
                        } else {
                            html += '; border-color: #d3d3d3';
                        }
                        html += `'><span>${value.votes}</span>
                                <div class='vote_actions'>
                                    <div onclick='voteCard("${uuid}");'>{{ translates.board_3 }}</div>
                                </div>
                            </div>
                            <div class='info_content' `

                        html += `>${value.content}</div>`
                        html += `</div></div>`;
                        html += `</div></li>`;
                        $(`#col_${index} ul`).append(html);
                    });
                });

                colLst = generateColumnBoundaries(Object.keys(board_data).length, $('.col').width() + 32);
                $('#speed_board_name').text(ws_data.board_info.board_name);
            } else if (ws_data.type == 'start_vote') {
                if (ws_data.maxVote != 0) {
                    ws.send(JSON.stringify({ type: 'stats_vote' }));
                }
                maxVoteTotal = $('#users .user').length * ws_data.maxVote;
                board_vote(ws_data.maxVote);
            } else if (ws_data.type == 'stats_vote') {
                votes_set = ws_data.votes;
                votes_total = ws_data.votes_total;
                console.log(goto_page_state);
                if (votes_total == 0 && votes_set != 0 && goto_page_state == 'votes') {
                    $('.vote_actions').hide();
                    goto_page('votes_end')
                }
            } else if (ws_data.type == 'card_add') {
                html = `<li class='ui-state-default uuid_${ws_data.card_uuid} pos_${ws_data.card_add.pos}' data-username="${ws_data.card_add.username}" data-uuid="${ws_data.card_uuid}" style="background-color: ${ws_data.card_add.username_color}; border-color: ${ws_data.card_add.username_color}">`;
                html += `<div class='card_icon' style='`;
                if (isLightColor(ws_data.card_add.username_color)) {
                    html += 'color: #333';
                } else {
                    html += 'border-color: #d3d3d3';
                }
                html += `'>`;
                html += `<div class='info_author'><i class="material-icons">person</i><b>${ws_data.card_add.username}</b></div>`;
                html += `</div>`;

                html += `<div class="card_content`;

                if (ws_data.card_add.username == username && !user_card_visibility) {
                    html += ' card_not_visible';
                }

                html += `">`;

                html += `<div class='votes' style='background-color: ${ws_data.card_add.username_color}`;
                if (isLightColor(ws_data.card_add.username_color)) {
                    html += '; color: #333';
                } else {
                    html += '; border-color: #d3d3d3';
                }
                html += `'><span>${parseInt(ws_data.card_add.votes)}</span>
                        <div class='vote_actions'>
                            <div onclick='voteCard("${ws_data.card_uuid}");'>{{ translates.board_3 }}</div>
                        </div>
                    </div>
                    <div class='info_content'>${ws_data.card_add.cardContent}</div>
                    </div>`;
                html += `</li>`;
                $(`#col_${ws_data.card_add.col_id} ul`).append(html);

            } else if (ws_data.type == 'card_vote') {
                $(`#col_${ws_data.card_vote.col_id} ul .uuid_${ws_data.card_vote.card_uuid} .votes span`).html(ws_data.card_votes);
                ws.send(JSON.stringify({ type: 'stats_vote' }));
            } else {
                if (ws_data.content == 'start_speed') {
                    $('#board_access').addClass('speed_step_1');
                    $('#speed_list').empty().animate({ height: '310px' }, 300, function() {
                        $(this).append(`<li id="board_timer"></li>`);
                        const config = [
                            { id: 'good_input', label: 'Good' },
                            { id: 'bad_input', label: 'Bad' },
                            { id: 'stape_input', label: 'Start / Stop' }
                        ];

                        config.forEach(({ id, label }) => {
                            $(this).append(`<li id="${id}"></li>`);
                            customPrompt(id, label);
                        });

                        board_timer(120);
                    }).css('background-color', 'transparent');
                } else if (ws_data.content == 'loop_speed') {
                    $('#board_timer').html('');
                    $('#board_access').addClass('speed_step_2').removeClass('speed_step_1');
                    $('#speed_list').empty().animate({ height: '170px' }, 300, function() {
                        $(this).append(`<li><i class="material-icons timer hourglass">hourglass_bottom</i></li>`);
                    }).css('background-color', '#dce8f7');

                    $('#users div').each(function () {
                        var data_username = $(this).attr('data-username');
                        if(data_username) {
                            user_list.push($(this).attr('data-username'));
                        }
                    });

                    ws.send(JSON.stringify({type: 'card_view', user_id: user_id}));
                    setTimeout(() => {
                        ws.send(JSON.stringify({ type: 'board_info' }));
                        $('#board_access').addClass('speed_step_1').removeClass('speed_step_2');
                        $('#speed_list').empty().animate({ height: '310px' }, 300, function() {
                            $(this).append(`<li id="board_timer"></li>`);
                            $(this).append(`<li id="board_curr_user"></li>`);
                            const config = [
                                { id: 'good_input', label: 'Good' },
                                { id: 'bad_input', label: 'Bad' },
                                { id: 'stape_input', label: 'Start / Stop' }
                            ];

                            config.forEach(({ id, label }) => {
                                $(this).append(`<li id="${id}"><h3>${label}</h3><div></div></li>`);
                            });

                            user_timer(60, user_list);
                        });
                    }, 5000);
                } else if (ws_data.content == 'votes') {
                    $('#board_timer').html('');
                    $('#board_access').addClass('speed_step_2').removeClass('speed_step_1');
                    $('.votes span').text('0');
                    $('#speed_list').empty().animate({ height: '170px' }, 300, function() {
                        $(this).append(`<li><i class="material-icons timer hourglass">hourglass_bottom</i></li>`);
                    }).css('background-color', '#dce8f7');

                    $('#col_bad h1').text('Bad');
                    $('#col_start_stop h1').text('Start / Stop');
                    $('#col_good, #col_actions, #loader').css('display', 'none');
                    $('#loader').hide('fade', 300);
                    $('#board').show('fade', 300);
                    startVote()
                } else if (ws_data.content == 'votes_end') {
                    ws.send(JSON.stringify({type: 'col_add', user_id: user_id, colName: 'actions' }));
                    $('#board').hide('fade', 300);
                    $('#loader').show('fade', 300);

                    setTimeout(() => {
                        ws.send(JSON.stringify({ type: 'board_info' }));
                        $('#board_access').addClass('speed_step_1').removeClass('speed_step_2');
                        $('#speed_list').empty().animate({ height: '310px' }, 300, function() {
                            $('.col ul').each(function () {
                                const $sortableList = $(this);
                                $sortableList.find('li').each(function () {
                                    const votes = parseInt($(this).find('.votes span').text());
                                    if (votes === 0) {
                                        $(this).remove();
                                    }
                                });

                                $sortableList.find('li').sort(function (a, b) {
                                    const aVotes = parseInt($(a).find('.votes span').text());
                                    const bVotes = parseInt($(b).find('.votes span').text());
                                    return bVotes - aVotes;
                                }).appendTo($sortableList);

                                $sortableList.find('li').each(function (index) {
                                    if (index >= 3) {
                                        $(this).remove();
                                        limitedCount++;
                                    }
                                });
                            });

                            const config = [
                                { id: 'bad_lst', label: 'Bad' },
                                { id: 'stape_lst', label: 'Start / Stop' },
                                { id: 'actions_input', label: 'Actions' }
                            ];
                            config.forEach(({ id, label }) => {
                                $(this).append(`<li id="${id}"><h3>${label}</h3><ul></ul></li>`);
                            });

                            const config2 = [
                                { id: 'bad', lst: 'bad_lst' },
                                { id: 'start_stop', lst: 'stape_lst' }
                            ];
                            config2.forEach(({ id, lst }) => {
                                const elements = $(`#col_${id} .info_content`);
                                if(elements.length > 0){
                                    elements.each(function() {
                                        $(`#${lst} ul`).append(`<li>● ${$(this).text()}</li>`);
                                    });
                                } else {
                                    $(`#${lst} ul`).html('<li>● {{ translates.speed_js_4 }}</li>');
                                }
                            });

                            if (board_author == username) {
                                $('#actions_input').html('');
                                customPrompt('actions_input', 'Actions');
                                $('#board_access_bloc').append('<button id="end_speed" onclick="end_speed();">{{ translates.speed_js_5 }}</button>');
                            } else {
                                $('#actions_input').remove();
                            }

                        }).css('background-color', 'transparent');
                    }, 5000);
                } else if (ws_data.content == 'end_speed') {
                    if (board_author == username) {
                        ws.send(JSON.stringify({
                            type: 'board_type',
                            username: localStorage.getItem('username'),
                            board_uuid: '{{ board_id }}',
                            board_name: $('#speed_board_name').val()
                        }));
                    }
                    setTimeout(() => {
                        window.location.href = window.location.href.replace('/speed/', '/board/');
                    }, 2000);
                }
            }
        });

        ws.onopen = () => {
            reconnectInterval = 1000;
            if (needReload) {
                window.location.reload();
            } else {
                $('#nav_logo').removeClass('nav_disconnected');
                $('.notif_ws').slideUp(300, function() {
                    $(this).remove();
                })

                ws.send(JSON.stringify({
                    type: 'connect',
                    board_id: '{{ board_id }}',
                    username: localStorage.getItem('username'),
                }));

                ws.send(JSON.stringify({ type: 'board_info' }));
                resendWsMessages(ws);
            }
        };

        ws.onclose = () => {
            $('#nav_logo').addClass('nav_disconnected');
            if (window.WebSocket) {
                setTimeout(connect, reconnectInterval);
                reconnectInterval *= 2;
                if(reconnectInterval > 8000) { needReload = true; reconnectInterval = 8000; }
            }
        };
    }
    connect();
    $(document).ready(function () {
        setTimeout(() => {
            $('#board_access').css('z-index', 11);
        }, 1200);
    })
}

$('#board').on('heightChange', '.col', function () {
    if ($(this).hasScrollBar()) {
        $(this).css('padding-right', '8px');
    } else {
        $(this).css('padding-right', '0');
    }
});
