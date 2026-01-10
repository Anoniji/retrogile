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
function removeNonAlphanumeric(e){return!!e&&e.replace(/[^a-zA-Z0-9]/g,"")}
function removeNonNumeric(e){return!!e&&e.replace(/[^0-9]/g,"")}
function isNumeric(i) { return !isNaN(parseFloat(i)) && isFinite(i) }
function generateColumnBoundaries(e, n) { let r = []; for (let u = 0; u < e; u++)r.push(Math.round(n * u)); return r }
function getFirstLetters(t) { return "string" != typeof t || 0 === t.length ? "<i class='material-icons'>face</i>" : "<span>" + t.charAt(0).toUpperCase() + "</span>" }
function rgbToHex(t) { t.includes("none") && (t = t.split(" none", 1)[0]); let n = t.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/); if (!n) throw Error("Format RGB invalide"); let e = parseInt(n[1], 10), _ = parseInt(n[2], 10), i = parseInt(n[3], 10); return e = e.toString(16), _ = _.toString(16), i = i.toString(16), e = 1 === e.length ? "0" + e : e, _ = 1 === _.length ? "0" + _ : _, i = 1 === i.length ? "0" + i : i, "#" + e + _ + i }
function hexToRgb(r) { hex = r.replace("#", ""); let n = parseInt(hex.substring(0, 2), 16), s = parseInt(hex.substring(2, 4), 16), t = parseInt(hex.substring(4, 6), 16); return { r: n, g: s, b: t } }
function isLightColor(r) { let t = hexToRgb(r), _ = (299 * t.r + 587 * t.g + 114 * t.b) / 1e3; return _ > 128 }
const ipv4Regex = /^(\d{1,3}\.){3}\d{1,3}$/;
const ipv6Regex = /^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$/;
function getRootDomain() { const hostname = window.location.hostname; if (ipv4Regex.test(hostname)) { const parts = hostname.split('.'); if (parts.every(part => { const num = parseInt(part, 10); return num >= 0 && num <= 255; })) { return hostname; } } if (ipv6Regex.test(hostname)) { return hostname; } const parts = hostname.split('.'); if (parts.length <= 2) return hostname; return parts.slice(-2).join('.'); }

var username = localStorage.getItem('username');
if (username === null) {
    const pathname = window.location.pathname;
    const lastpart = pathname.split('/').pop();
    location.href = `../#${lastpart}`;
}

$(function () {
    $('#toggle_chat').click(function () {
        $('#console').toggle();
        $('#console_dot').hide('fade');
    });
});


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

function showNotification(type, icon, user, message) {
    var notification = $(`<div class="notification notif_${type}">`);
    $(`.notif_${type}`).hide();
    notification.append(`<i class="material-icons">${icon}</i> <span><b>${user}</b> ${message}</span>`);
    $('body #notifications').append(notification);
    notification.slideDown(300).delay(5000).slideUp(300, function () {
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

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

var freeze_board = false;
var waiting_unfreeze = false;
function customPrompt(col_id, message, defaultValue) {
    freeze_board = true;
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
        input.style.height = (input.scrollHeight - 18) + 'px';
    }

    return new Promise((resolve) => {
        button.addEventListener('click', () => {
            const value = escapeHtml(input.value);
            dialog.remove();
            freeze_board = false;
            resolve(value);
        });

        input.addEventListener('input', () => {
            input.style.height = 'auto';
            input.style.height = (input.scrollHeight - 18) + 'px';
        });

        input.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') {
                const value = escapeHtml(input.value);
                dialog.remove();
                freeze_board = false;
                resolve(value);
            }
        });

        document.addEventListener('keyup', (event) => {
            if (event.key === 'Escape') {
                dialog.remove();
                freeze_board = false;
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
            $countdownElement.text('{{ translates.board_js_1 }}');
            $('#wallpaper2').effect('highlight');
        }
    };
    const intervalId = setInterval(updateCount, 1000);
    $countdownElement.data('intervalId', intervalId);
    updateCount();
}

function board_vote(maxVote) {
    if (maxVote == 0) {
        $('#board_vote .title').html('Vote');
        $('nav #vote_progress, #board-votes-menu, .vote_actions').fadeOut(300);
        $('#cursors').fadeIn(300);
    } else {
        $('#board_vote .title, #votes_remaining').html(maxVote);
        $('nav #vote_progress, #board-votes-menu, .vote_actions').fadeIn(300);
        $('#cursors').fadeOut(300);
    }
}

function randomBetweenZeroAndScreenWidth() {
    return Math.floor(Math.random() * (window.innerWidth - 32));
}

function randomBetweenZeroAndScreenHeight() {
    return Math.floor(Math.random() * (window.innerHeight - 32));
}

function createConfetti(options) {
    const canvas = document.createElement('canvas');
    canvas.className = 'confetti_animate';
    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const {
        particleCount = 100,
        startVelocity = 10,
        angle = 90,
        origin = { x: 0.5, y: 0.5 },
        colors = ['#FF6B6B']
    } = options;

    const colorPalette = generateColorPalette(colors[0]);
    const particles = [];

    for (let i = 0; i < particleCount; i++) {
        const particleVelocity = startVelocity * (0.6 + Math.random() * 0.4);
        const spreadAngle = (Math.random() - 0.5) * 30;
        const finalAngle = (angle + spreadAngle) * (Math.PI / 180);

        particles.push({
            x: origin.x * canvas.width,
            y: origin.y * canvas.height,
            vx: Math.cos(finalAngle) * particleVelocity,
            vy: -Math.sin(finalAngle) * particleVelocity,
            distanceTraveled: 0,
            maxDistance: particleVelocity * 100,
            color: colorPalette[Math.floor(Math.random() * colorPalette.length)],
            size: 8 + Math.random() * 4,
            rotation: Math.random() * Math.PI * 2,
            rotationSpeed: (Math.random() - 0.5) * 0.2
        });
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let hasParticles = false;

        for (const p of particles) {
            p.x += p.vx;
            p.y += p.vy;
            p.distanceTraveled += Math.sqrt(p.vx * p.vx + p.vy * p.vy);
            const opacity = Math.max(0, 1 - (p.distanceTraveled / p.maxDistance));
            p.rotation += p.rotationSpeed;

            if (opacity > 0) {
                ctx.save();
                ctx.globalAlpha = opacity;
                ctx.fillStyle = p.color;
                ctx.translate(p.x, p.y);
                ctx.rotate(p.rotation);
                ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size);
                ctx.restore();
                hasParticles = true;
            }
        }

        if (hasParticles) {
            requestAnimationFrame(animate);
        } else {
            canvas.remove();
        }
    }
    animate();
}

function generateColorPalette(hexColor) {
    const rgb = hexToRgb(hexColor);
    const darkerRgb = `rgb(${Math.max(0, rgb.r - 50)}, ${Math.max(0, rgb.g - 50)}, ${Math.max(0, rgb.b - 50)})`;
    const darker = rgbToHex(darkerRgb);
    const normal = hexColor;
    const lighterRgb = `rgb(${Math.min(255, rgb.r + 50)}, ${Math.min(255, rgb.g + 50)}, ${Math.min(255, rgb.b + 50)})`;
    const lighter = rgbToHex(lighterRgb);
    return [darker, normal, lighter];
}

var cnt_clk = 0
function cursor_clicked(elem) {
    $(`#${elem}`).css(
        'opacity', '0').css(
            'top', `${randomBetweenZeroAndScreenHeight()}px`).css(
                'left', `${randomBetweenZeroAndScreenWidth()}px`).css(
                    'opacity', '.4');

    cnt_clk += 1;
    $('#click_cnt').html(`${cnt_clk} {{ translates.board_js_2 }}`);
    if (cnt_clk % 20 == 0) {
        createConfetti({
            particleCount: 512,
            startVelocity: 10,
            angle: 60,
            origin: {
                x: 0,
                y: 1
            },
            colors: ['#333333']
        });
        createConfetti({
            particleCount: 512,
            startVelocity: 10,
            angle: 120,
            origin: {
                x: 1,
                y: 1
            },
            colors: ['#333333']
        });
    }
}

var stockList = {};
let timeout;
var colLst;

function scrollFix() {
    $board = $('#board');
    clearTimeout(timeout);
    timeout = setTimeout(function () {
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
    let needReload = false;
    let board_author;
    let user_id = false;

    let confettiActive = false;
    let confettiSpread = false;
    let confettiTimer = false;
    let isDrawing = false;
    let line;
    let startX, startY;

    var pos_x;
    var pos_y;
    var curr_highlightUser;
    var maxVoteTotal;
    var mergeEnable = false;

    $('#board').scroll(function () {
        scrollFix();
    });

    function board_copy_link() {
        try {
            navigator.permissions.query({ name: 'clipboard-write' }).then((result) => {
                if (result.state == 'granted' || result.state == 'prompt') {
                    showNotification('link', 'circle_notifications', '(!)', '{{ translates.board_js_3 }}');
                    navigator.clipboard.writeText(window.location.href);
                }
            });
        } catch (err) {
            console.error('Error_copy:', err);
        }
    };

    function startTimer() {
        if (board_author != username) return;
        let timerInMinutes = prompt('{{ translates.board_js_4 }}');

        timerInMinutes = removeNonNumeric(timerInMinutes);
        if (timerInMinutes && timerInMinutes != '') {
            sendWsMessage(ws, JSON.stringify({
                type: 'start_timer',
                timerInMinutes: timerInMinutes,
            }));
        }
    }

    function startVote() {
        if (board_author != username) return;
        let maxVote = prompt('{{ translates.board_js_5 }}');

        maxVote = removeNonNumeric(maxVote);
        if (maxVote && maxVote != '') {
            sendWsMessage(ws, JSON.stringify({
                type: 'start_vote',
                maxVote: maxVote,
            }));
        }
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

    function startConfetti() {
        confettiActive = true;
        $('#board_confetti').prop('disabled', true);
        $('#confetti').css('z-index', 100);
    }

    $('#confetti').on('mousedown touchstart', function (e) {
        if (!confettiActive) return;
        e.preventDefault();
        isDrawing = true;
        startX = e.pageX - $(this).offset().left;
        startY = e.pageY - $(this).offset().top;

        circle = $('<div>').addClass('circle').css({
            left: startX - 11,
            top: startY - 11
        }).appendTo('#confetti');
    });

    $('#confetti').on('mousemove touchmove', function (e) {
        if (!isDrawing) return;
        e.preventDefault();

        let mouseX = e.pageX - $(this).offset().left;
        let mouseY = e.pageY - $(this).offset().top;

        if (line) line.remove();

        line = $('<div>').addClass('line').appendTo('#confetti');
        updateLine(startX, startY, mouseX, mouseY, line);
    });

    $('#confetti').on('mouseup touchend touchcancel', function (e) {
        if (!isDrawing && !confettiSpread) return;
        e.preventDefault();
        isDrawing = false;

        let endX = e.pageX - $(this).offset().left;
        let endY = e.pageY - $(this).offset().top;

        let distance = Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2));
        let angle = Math.atan2(endY - startY, endX - startX) * 180 / Math.PI;

        ws.send(JSON.stringify({
            type: 'start_confetti',
            startX: parseInt(startX),
            startY: startY + parseInt($('#confetti').css('top')),
            angle: parseInt(angle),
            distance: parseInt(distance),
        }));
        $('.circle, .line').remove();
        $('#confetti').css('z-index', -1);
        confettiActive = false;
    });

    function updateLine(x1, y1, x2, y2, line) {
        let distance = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
        let angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;

        line.css({
            width: distance,
            left: x1,
            top: y1,
            transform: `rotate(${angle}deg)`
        });
    }

    function start_timer() {
        sendWsMessage(ws, JSON.stringify({
            type: 'start_timer',
            timerInSeconds: timerInSeconds,
        }));
    }

    function addCard(col_id) {
        sendWsMessage(ws, JSON.stringify({ type: 'card_write_start' }));
        customPrompt(col_id, '{{ translates.board_js_6 }}', '').then(cardContent => {
            if (cardContent) {
                sendWsMessage(ws, JSON.stringify({
                    type: 'card_add',
                    pos: $(`#col_${col_id} ul`).children('li').length,
                    user_id: user_id,
                    col_id: col_id,
                    votes: 0,
                    cardContent: cardContent.trim(),
                }));
            }
            if (waiting_unfreeze) {
                waiting_unfreeze = false;
            }
            sendWsMessage(ws, JSON.stringify({ type: 'card_write_stop' }));
        });
    }

    function mergeCard() {
        if (board_author != username) return;
        if (!mergeEnable) {
            $('#board_merge_bloc i').text('merge')
            $('.child_drop').show();
            $('.card_child i').addClass('cursor_pointer');
            mergeEnable = true;
        } else {
            $('#board_merge_bloc i').text('call_merge')
            $('.child_drop').hide();
            $('.card_child i').removeClass('cursor_pointer');
            mergeEnable = false;
        }
    }

    function unmergeCard(col_id, parent, cardPos) {
        if (board_author != username) return;
        if ($('#board_merge_bloc i').text() == 'call_merge') return;
        sendWsMessage(ws, JSON.stringify({
            type: 'card_unmerge',
            user_id: user_id,
            col_id: col_id,
            card_uuid: parent,
            cardContent: cardPos,
        }));
    }

    function editCard(card_uuid) {
        col_id = $(`.uuid_${card_uuid}`).parent().parent().attr('data-col');
        sendWsMessage(ws, JSON.stringify({ type: 'card_write_start' }));
        customPrompt(col_id, '{{ translates.board_js_7 }}', $(`.uuid_${card_uuid} .info_content`).text()).then(cardContent => {
            if (cardContent) {
                sendWsMessage(ws, JSON.stringify({
                    type: 'card_edit',
                    user_id: user_id,
                    col_id: col_id,
                    card_uuid: card_uuid,
                    cardContent: cardContent.trim(),
                }));
            }
            if (waiting_unfreeze) {
                waiting_unfreeze = false;
                ws.send(JSON.stringify({ type: 'board_info' }));
            }
            sendWsMessage(ws, JSON.stringify({ type: 'card_write_stop' }));
        });
    }

    function voteCard(card_uuid, act) {
        const now = Date.now();
        const lastExecution = voteCard.lastExecution || 0;
        if (now - lastExecution < 1000) {
            return;
        }
        voteCard.lastExecution = now;

        var col_id = $(`.uuid_${card_uuid}`).parent().parent().attr('data-col');
        var cur_vote = $(`.uuid_${card_uuid} .votes span`).text();
        var maxVote = $('#board_vote .title').text();

        if (act == "remove" && cur_vote == "0") return;
        if (act == "add" && maxVote == "0") return;

        if (!isNaN(maxVote)) {
            maxVote = parseInt(maxVote);
            maxVote -= 1
            $('#board_vote .title').text(maxVote);

            if (act == "add") {
                sendWsMessage(ws, JSON.stringify({
                    type: 'card_vote',
                    user_id: user_id,
                    col_id: col_id,
                    card_uuid: card_uuid,
                }));
            } else {
                sendWsMessage(ws, JSON.stringify({
                    type: 'card_vote',
                    user_id: user_id,
                    col_id: col_id,
                    card_uuid: card_uuid,
                    unvote: true,
                }));
            }

            $(`.uuid_${card_uuid} .votes`).effect('highlight', { color: "#f2f2f2" }, 700);
        }
    }

    function deleteCard(card_uuid) {
        col_id = $(`.uuid_${card_uuid}`).parent().parent().attr('data-col').toString();
        sendWsMessage(ws, JSON.stringify({
            type: 'card_delete',
            user_id: user_id,
            col_id: col_id,
            card_uuid: card_uuid,
        }));
    }

    function addCol() {
        if (board_author != username) return;
        let colName = prompt('{{ translates.board_js_8 }}');
        colName = removeNonAlphanumeric(colName);
        if (isNumeric(colName)) return;
        if (colName) {
            sendWsMessage(ws, JSON.stringify({
                type: 'col_add',
                user_id: user_id,
                colName: colName,
            }));

            if ($('.col').length == 4) {
                $('.col').addClass('col_5');
                $('#board_add_bloc').hide();
            }
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
        sendWsMessage(ws, JSON.stringify({
            type: 'col_reorder',
            user_id: user_id,
            colName: newOrder,
            uuidList: false,
        }));
    }

    function viewCardToggle() {
        $('#board_cards_visibility').prop('disabled', true);
        sendWsMessage(ws, JSON.stringify({
            type: 'card_view',
            user_id: user_id,
        }));
        setTimeout(() => {
            $('#board_cards_visibility').prop('disabled', false);
        }, 3600)
    }

    function moveToChild(parentId, childId) {
        sendWsMessage(ws, JSON.stringify({
            type: 'card_parent',
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

        sendWsMessage(ws, JSON.stringify({
            type: 'col_order',
            user_id: user_id,
            colName: name.slice(4),
            uuidList: uuid_list,
        }));
    }

    function deleteCol(col_id) {
        if (board_author != username) return;
        if (window.confirm('{{ translates.board_js_9 }}')) {
            if ($('.col').length == 5) {
                $('.col').removeClass('col_5');
                $('#board_add_bloc').show();
            }
            sendWsMessage(ws, JSON.stringify({
                type: 'col_delete',
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

    var vote_order = false;
    function board_vote_order(force = false) {
        if (!vote_order || force) {
            $('.sortable').each(function () {
                const $sortableList = $(this);
                $sortableList.find('li').sort(function (a, b) {
                    const aVotes = parseInt($(a).find('.votes span').text());
                    const bVotes = parseInt($(b).find('.votes span').text());
                    return bVotes - aVotes;
                }).appendTo($sortableList);
            });
            vote_order = true;
        } else {
            vote_order = false;
            ws.send(JSON.stringify({ type: 'board_info' }));
        }
    }

    function userMood(val) {
        if(val) {
            sendWsMessage(ws, JSON.stringify({
                type: 'user_mood',
                user_id: user_id,
                mood: val,
            }));
            $('#users_custom_mood').hide();
        }
    }

    function connect() {
        ws_path = 'ws://';
        if (window.location.protocol === 'https:') {
            ws_path = 'wss://';
        }

        if ("{{ ws_subdomain }}" != "") {
            ws_path = `${ws_path}{{ ws_subdomain }}${getRootDomain()}`;
        } else {
            ws_path = `${ws_path}${getRootDomain()}:8009`;
        }
        ws = new WebSocket(`${ws_path}/?token={{ ws_session }}`);

        $(document).on('mousemove', function (event) {
            pos_x = (event.pageX / $(window).width()) * 100;
            pos_y = (event.pageY / $(window).height()) * 100;
        });

        function mouse_position() {
            sendWsMessage(ws, JSON.stringify({
                type: 'cursor_user',
                pos_x: pos_x,
                pos_y: pos_y,
            }));
        }

        ws.addEventListener('message', ev => {
            ws_data = JSON.parse(ev.data);
            detectDevTool();
            if (ws_data.type == 'connect_status') {
                if (!ws_data.error) {
                    user_id = ws_data.user_id;
                    user_color = ws_data.user_color;
                    if (!isLightColor(user_color)) {
                        $('#board_name').animate({ color: "#f2f2f2" }, 300);
                    }
                    $('.board-color, nav #vote_progress').animate({ backgroundColor: user_color }, 300);
                }
            } else if (ws_data.type == 'users_list') {
                $('#users, #cursors').html('');
                $.each(ws_data.users_list, function (index, value) {
                    if (user_id && user_id != index) {
                        $('#cursors').append(`<div id='cursor_${index}' class='cursor' ondblclick='cursor_clicked(this.id);'><div class='username'>${value.username}</div></div>`)
                    }
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

                        $('#users').append(`<div id='user_${index}' class='user' title='${value.username}' data-username='${value.username}' data-count='1' onclick='highlightUser("${value.username}");' style='${txt_color}background: ${value.color}'>${getFirstLetters(value.username)}<div class='user_notif_status'></div></div>`);
                        $(document).tooltip({ position: { my: 'center top', at: 'center bottom' } });
                    }
                });
            } else if (ws_data.type == 'user_add') {
                if (user_id != ws_data.user_id) {
                    $('#cursors').append(`<div id='cursor_${ws_data.user_id}' class='cursor' ondblclick='cursor_clicked(this.id);'><div class='username'>${ws_data.username}</div></div>`);

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
                        $('#users').append(`<div id='user_${ws_data.user_id}' class='user' title='${ws_data.username}' data-username='${ws_data.username}' data-count='1' onclick='highlightUser("${ws_data.username}");' style='${txt_color}background: ${ws_data.color}'></div>`);
                        $(`#user_${ws_data.user_id}`).hide().html(getFirstLetters(ws_data.username) + "<div class='user_notif_status'></div>").slideDown(300, function () {
                            if (curr_highlightUser) {
                                let tmps_highlightUser = curr_highlightUser;
                                curr_highlightUser = false;
                                highlightUser(tmps_highlightUser);
                            }
                        });
                        $(document).tooltip({ position: { my: 'center top', at: 'center bottom' } });
                    }
                }
            } else if (ws_data.type == 'user_remove') {
                log(`< ${ws_data.username} > {{ translates.board_js_11 }}`, 'red');
                $(`#cursor_${ws_data.user_id}`).remove();

                var $div_username = $(`#users div[data-username=${ws_data.username}]`);
                var currentCount = parseInt($div_username.attr('data-count'));
                if (currentCount == 1) {
                    $(`#user_${ws_data.user_id}`).remove();
                } else {
                    $div_username.attr('data-count', currentCount - 1);
                }
            } else if (ws_data.type == 'cursor_user') {
                if (user_id != ws_data.user_id) {
                    if (ws_data.pos_y && ws_data.pos_x) {
                        $(`#cursor_${ws_data.user_id}`).animate({ top: `${ws_data.pos_y}vh`, left: `${ws_data.pos_x}vw` }, 2800);
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
                    if (isLightColor(ws_data.custom_color)) {
                        $('#board_name').animate({ color: "#333" }, 300);
                    } else {
                        $('#board_name').animate({ color: "#f2f2f2" }, 300);
                    }
                    $('.board-color, #vote_progress').animate({ backgroundColor: ws_data.custom_color }, 300);
                }

                ws.send(JSON.stringify({ type: 'board_info' }));
            } else if (ws_data.type == 'board_info') {
                if (freeze_board) {
                    waiting_unfreeze = true;
                    return;
                }
                board_author = ws_data.board_info.author;
                board_data = ws_data.board_info.data;
                check_timer = ws_data.board_info.timer;
                check_votes = ws_data.board_info.votes;
                list_votes = ws_data.board_info.votes_list;
                list_users = ws_data.board_info.users_list;

                if (board_author == username) {
                    $('#nav_main_logo, #nav_main_logo_mini').attr('onclick', "location.href = './';");
                }

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
                        sendWsMessage(ws, JSON.stringify({
                            type: 'stats_vote',
                        }));
                    }
                }

                const url = window.location.href;
                if (!url.startsWith("https://") && !url.includes("localhost") && !url.includes("127.0.0.1")) {
                    $('#board_copy_link').remove();
                }

                $('#board').html('');
                if (!board_data) {
                    $('#board_name').html("{{ translates.board_js_12 }}<a href='../'>{{ translates.board_js_13 }}</a>");
                    $('#board_timer, #board_vote, #r_menu').remove();
                    return;
                }

                col_class = 'col';
                if (board_author != username) {
                    $('#board_add_bloc, #board_merge_bloc').remove();
                    $('#board_timer, #board_vote').prop('disabled', true);
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

                var board_col_idx = 0;
                var board_total_idx = Object.keys(board_data).length - 1;
                $.each(board_data, function (index, value) {
                    var h1_name = index;
                    if (h1_name.length > 14) {
                        h1_name = h1_name.substring(0, 14) + '...';
                    }

                    html = `<div id='col_${index}' data-col='${index}' class='${col_class}'><h1>${h1_name}<i onclick='addCard("${index}");' class='add_icon material-icons'>add</i>`;
                    if (board_author == username) {
                        html += `<i onclick='deleteCol("${index}");' class='drop_icon material-icons'>delete</i>`;
                        if (board_col_idx != 0) {
                            html += `<i onclick='moveCol("left", "${index}");' class='left_icon material-icons'>keyboard_double_arrow_left</i>`;
                        }
                        if (board_col_idx != board_total_idx) {
                            html += `<i onclick='moveCol("right", "${index}");' class='right_icon material-icons'>keyboard_double_arrow_right</i>`;
                        }
                    }
                    html += `</h1><ul class='sortable'></ul></div>`;
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
                        if (value.author == username) {
                            html += `<div class='edit_icon' onclick='editCard("${uuid}");' title='{{ translates.board_js_15 }}'>
                                <i class="material-icons">edit</i>
                            </div>
                            <div class='delete_icon' onclick='deleteCard("${uuid}");' title='{{ translates.board_js_16 }}'>
                                <i class="material-icons">delete</i>
                            </div>`;
                        }
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
                                    <div onclick='voteCard("${uuid}", "remove");'>-</div>
                                    <div onclick='voteCard("${uuid}", "add");'>+</div>
                                </div>
                            </div>
                            <div class='info_content' `

                        html += `>${value.content}</div>`
                        html += `</div></div>`;

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
                        update: function (e, u) { $('.child_drop').each(function (_, e) { if ($(e).children().length) { $(e).children().each(function (_, c) { moveToChild($(e).attr('data-parentId'), $(c).attr('data-uuid')); return; }) } }) }
                    });
                    board_col_idx += 1;
                });

                colLst = generateColumnBoundaries(Object.keys(board_data).length, $('.col').width() + 32);
                $('#board_name').html(ws_data.board_info.board_name);
                if (curr_highlightUser) {
                    let tmps_highlightUser = curr_highlightUser;
                    curr_highlightUser = false;
                    highlightUser(tmps_highlightUser);
                }

                if (vote_order) {
                    board_vote_order(true);
                }

                if (board_author == username && $('#board_merge_bloc i').text() == 'merge') {
                    $('.child_drop').show();
                }

                applySavedSize("info_content");
            } else if (ws_data.type == 'start_timer') {
                board_timer(ws_data.timerInSeconds);
            } else if (ws_data.type == 'start_confetti') {
                if (!confettiSpread) {
                    confettiSpread = true;
                    createConfetti({
                        particleCount: 512,
                        startVelocity: parseInt(Math.min(ws_data.distance / 15, 100)),
                        angle: 180 - ws_data.angle,
                        origin: {
                            x: ws_data.startX / $('#confetti').width(),
                            y: ws_data.startY / $('#confetti').height()
                        },
                        colors: ['#' + ws_data.color.replace('#', '')]
                    });

                    if (confettiTimer) {
                        clearTimeout(confettiTimer);
                    }

                    confettiTimer = setTimeout(function () {
                        confettiSpread = false;
                        $('#board_confetti').prop('disabled', false);
                    }, 2000);
                }
            } else if (ws_data.type == 'start_vote') {
                if (ws_data.maxVote != 0) {
                    $('.votes span').html(0);
                    ws.send(JSON.stringify({ type: 'stats_vote' }));
                    $('#wallpaper2').effect('highlight');
                }
                maxVoteTotal = $('#users .user').length * ws_data.maxVote;
                board_vote(ws_data.maxVote);
            } else if (ws_data.type == 'stats_vote') {
                votes_set = ws_data.votes;
                votes_remaining = ws_data.votes_remaining;
                votes_total = ws_data.votes_total;
                votes_percentage = ws_data.votes_percentage;
                $('nav #vote_progress').css('width', `${votes_percentage}%`);
                $('#board_vote .title').html(votes_remaining);
                $('#votes_remaining').html(votes_total);

                if (votes_total == 0 && votes_set != 0) {
                    $('nav #vote_progress').hide().css('width', '100%');
                    $('#board-votes-menu, .vote_actions').fadeOut(300);
                    $('#cursors').fadeIn(300);
                    $('#wallpaper2').effect('highlight');
                } else {
                    $('nav #vote_progress, #board-votes-menu, .vote_actions').fadeIn(300);
                    $('#cursors').fadeOut(300);
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
                if (ws_data.card_add.username == username) {
                    html += `<div class='edit_icon' onclick='editCard("${ws_data.card_uuid}");' title='{{ translates.board_js_15 }}'>
                        <i class='material-icons'>edit</i>
                    </div>
                    <div class='delete_icon' onclick='deleteCard("${ws_data.card_uuid}");' title='{{ translates.board_js_16 }}'>
                        <i class='material-icons'>delete</i>
                    </div>`;
                }
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
                            <div onclick='voteCard("${ws_data.card_uuid}", "remove");'>-</div>
                            <div onclick='voteCard("${ws_data.card_uuid}", "add");'>+</div>
                        </div>
                    </div>
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
                    update: function (e, u) { $('.child_drop').each(function (_, e) { if ($(e).children().length) { $(e).children().each(function (_, c) { moveToChild($(e).attr('data-parentId'), $(c).attr('data-uuid')); return; }) } }) }
                });

                if (curr_highlightUser) {
                    let tmps_highlightUser = curr_highlightUser;
                    curr_highlightUser = false;
                    highlightUser(tmps_highlightUser);
                }

                if (vote_order) {
                    board_vote_order(true);
                }

                applySavedSize("info_content");
            } else if (ws_data.type == 'card_edit') {
                $(`#col_${ws_data.card_edit.col_id} ul .uuid_${ws_data.card_edit.card_uuid} .info_content`).html(ws_data.card_edit.cardContent);
            } else if (ws_data.type == 'card_view') {
                notif_type = 'hide';
                notif_ico = 'visibility_off';
                notif_txt = '{{ translates.board_js_17 }}';
                if (ws_data.card_view.visibility) {
                    notif_type = 'show';
                    notif_ico = 'visibility';
                    notif_txt = '{{ translates.board_js_18 }}';
                }

                card_view_username = ws_data.card_view.username;
                $(`#users div[data-username=${card_view_username}] .user_notif_status`)
                    .stop(true, false)
                    .html(`<i class="material-icons">${notif_ico}</i>`)
                    .show('slide', { direction: 'down' }, 300, function () {
                        setTimeout(() => {
                            $(`#users div[data-username=${card_view_username}] .user_notif_status`).hide('slide', { direction: 'down' }, 300);
                        }, 3000);
                    });

                if (ws_data.card_view.username == username) {
                    if (ws_data.card_view.hidden) {
                        $('#board_cards_visibility .material-icons').html('visibility_off');
                        $('#board_cards_visibility .title').html('{{ translates.board_js_19 }}');
                    } else {
                        $('#board_cards_visibility .material-icons').html('visibility');
                        $('#board_cards_visibility .title').html('{{ translates.board_js_20 }}');
                    }
                }

                ws.send(JSON.stringify({ type: 'board_info' }));
            } else if (ws_data.type == 'card_vote') {
                $(`#col_${ws_data.card_vote.col_id} ul .uuid_${ws_data.card_vote.card_uuid} .votes span`).html(ws_data.card_votes);
                ws.send(JSON.stringify({ type: 'stats_vote' }));
            } else if (ws_data.type == 'card_delete') {
                $(`#col_${ws_data.card_delete.col_id} ul .uuid_${ws_data.card_delete.card_uuid}`).remove();
            } else if (ws_data.type == 'card_write_start') {
                if (ws_data.card_write_start.username != username) {
                    $(`#users div[data-username=${ws_data.card_write_start.username}]`).addClass('writing');
                }
            } else if (ws_data.type == 'card_write_stop') {
                if (ws_data.card_write_stop.username != username) {
                    $(`#users div[data-username=${ws_data.card_write_stop.username}]`).removeClass('writing');
                }
            } else if (ws_data.type == 'col_order') {
                const sortableList = document.querySelector(`#col_${ws_data.col_order.colName} .sortable`);
                const fragment = document.createDocumentFragment();
                ws_data.col_order.uuidList.forEach(uuid => {
                    const li = sortableList.querySelector(`li[class*="${uuid}"]`);
                    if (li) {
                        fragment.appendChild(li);
                    } else {
                        ws.send(JSON.stringify({ type: 'board_info' }));
                    }
                });

                sortableList.innerHTML = '';
                sortableList.appendChild(fragment);
            } else if (['force_reload', 'col_reorder', 'card_parent', 'card_unmerge', 'col_add', 'col_delete'].includes(ws_data.type)) {
                ws.send(JSON.stringify({ type: 'board_info' }));
            } else if (ws_data.type == 'user_mood') {
                if(ws_data.user_mood.mood == 2) {
                    mgs_icon = 'sentiment_satisfied';
                    mgs_text = '{{ translates.board_js_29 }}';
                } else if(ws_data.user_mood.mood == 3) {
                    mgs_icon = 'sentiment_very_satisfied';
                    mgs_text = '{{ translates.board_js_30 }}';
                } else {
                    mgs_icon = 'sentiment_dissatisfied';
                    mgs_text = '{{ translates.board_js_28 }}';
                }

                showNotification('mood', mgs_icon, ws_data.user_mood.username, mgs_text);
            } else {
                if ($("#console").css("display") !== "block" && ws_data.username != username) {
                    $('#console_dot').show('fade');
                }
                log(`< ${ws_data.username} > ${ws_data.content}`, 'white');
            }
        });

        const antispam = {
            maxMessages: 3,
            timeWindow: 3000,
            messages: [],
        };

        document.getElementById('form').onsubmit = ev => {
            ev.preventDefault();

            const now = Date.now();
            antispam.messages = antispam.messages.filter(timestamp => now - timestamp < antispam.timeWindow);
            antispam.messages.push(now);

            if (antispam.messages.length > antispam.maxMessages) {
                const $form = $('#form');
                const $newDiv = $('<div>').attr('id', 'form');
                $form.attr('class') && $newDiv.addClass($form.attr('class'));
                $newDiv.append($form.contents());
                $form.replaceWith($newDiv);
                return;
            }

            const textField = document.getElementById('chat_msg');
            sendWsMessage(ws, JSON.stringify({
                type: 'message',
                content: escapeHtml(textField.value),
            }));
            textField.value = '';
        };

        ws.onopen = () => {
            reconnectInterval = 1000;
            if (needReload && !freeze_board) {
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

                setInterval(function () { mouse_position() }, 3000);
            }
        };

        ws.onclose = () => {
            showNotification('ws', 'circle_notifications', '{{ translates.ws_1 }}', '{{ translates.ws_2 }}');
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
            $('#loader').hide('fade', 300, function () {
                $(this).remove();
            });
        }, 1200);
    }).keydown(function (event) {
        if (event.ctrlKey) {
            startConfetti();
        }
    });
}

$('#toggle_mood').click(function () {
    $('#users_custom_mood').toggle();
});

$('#board').on('heightChange', '.col', function () {
    if ($(this).hasScrollBar()) {
        $(this).css('padding-right', '8px');
    } else {
        $(this).css('padding-right', '0');
    }
});

window.onload = () => {
    applySavedSize("info_content");
};

window.onresize = function (_) {
    colLst = generateColumnBoundaries($('.col').length, $('.col').width() + 32);
    scrollFix();
};

