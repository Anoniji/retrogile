#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import uuid
import hashlib
import asyncio
import datetime
import websockets


users = {}
clients = set()
pos = 0


def generate_color(_key):
    hash_object = hashlib.sha256(_key.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    color_hex = f"#{hex_dig[:6]}"
    return color_hex


def get_board_list_by_author(author):
    directory = './board/'
    author_files = []
    for file in os.listdir(directory):
        if file.endswith(".json"):
            file_path = os.path.join(directory, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data['author'] == author:
                    author_files.append([data['board_name'], file_path])
    return author_files


def get_board_info_by_id(board_id, username_filter=False):
    if board_id:
        board_path = f'./board/{board_id}.json'
        if os.path.isfile(board_path):
            with open(board_path, encoding='utf-8') as f:
                _tmps = json.load(f)
                if not username_filter:
                    return _tmps

                for col_name in _tmps['data']:
                    for card_uuid, card_data in _tmps['data'][col_name].items():
                        if card_data["author"] != username_filter and card_data['hidden']:
                            _tmps['data'][col_name][card_uuid]['content'] = '~~~'

                return _tmps

    return False


def get_board_info_by_id(board_id, new_timer_value):
    board_info = get_board_info_by_id(board_id)
    if board_info:
        board_info['timer'] = int(new_timer_value.timestamp() * 1000)
        board_path = f'./board/{board_id}.json'
        with open(board_path, 'w', encoding='utf-8') as f:
            json.dump(board_info, f, indent=4)
        return True

    return False


def reset_votes_in_nested_dict(my_dict):
    for key, value in my_dict.items():
        if isinstance(value, dict):
            reset_votes_in_nested_dict(value)
        elif key == "votes":
            my_dict[key] = 0

    return my_dict


def board_votes_reset_by_id(board_id):
    board_info = get_board_info_by_id(board_id)
    if not board_info:
        return False

    for key, value in board_info['data'].items():
        if isinstance(value, dict):
            reset_votes_in_nested_dict(value)
        elif key == "votes":
            board_info['data'][key] = 0

    board_path = f'./board/{board_id}.json'
    with open(board_path, 'w', encoding='utf-8') as f:
        json.dump(board_info, f, indent=4)


def board_manager_by_id(board_id, mode, data):
    board_info = get_board_info_by_id(board_id)
    if not board_info:
        return False

    card_uuid = uuid.uuid4().hex
    card_votes = 0
    if mode == 'card_add':
        board_info['data'][data.get('col_id')][card_uuid] = {
            'pos': data.get('pos'),
            'author': data.get('author'),
            'author_id': data.get('user_id'),
            'content': data.get('cardContent'),
            'hidden': True,
            'votes': 0
        }

    elif mode == 'card_edit':
        if(data.get('col_id') in board_info['data'] and data.get('card_uuid') in board_info['data'][data.get('col_id')]):
            board_info['data'][data.get('col_id')][data.get('card_uuid')]['content'] = data.get('cardContent')

    elif mode == 'card_view':
        for col_name in board_info["data"]:
            for card_uuid, card_data in board_info["data"][col_name].items():
                if card_data["author"] == data.get('author'):
                    board_info["data"][col_name][card_uuid]["hidden"] = False

    elif mode == 'card_vote':
        if(data.get('col_id') in board_info['data'] and data.get('card_uuid') in board_info['data'][data.get('col_id')]):
            board_info['data'][data.get('col_id')][data.get('card_uuid')]['votes'] += 1
            card_votes = board_info['data'][data.get('col_id')][data.get('card_uuid')]['votes']

    elif mode == 'card_delete':
        if(data.get('col_id') in board_info['data'] and data.get('card_uuid') in board_info['data'][data.get('col_id')]):
            del board_info['data'][data.get('col_id')][data.get('card_uuid')]

    board_path = f'./board/{board_id}.json'
    with open(board_path, 'w', encoding='utf-8') as f:
        json.dump(board_info, f, indent=4)
    return card_uuid, card_votes


def col_manager_by_board_id(board_id, mode, data):
    board_info = get_board_info_by_id(board_id)
    if not board_info:
        return False

    if mode == 'col_add':
        if data.get('colName') in board_info['data']:
            return False

        board_info['data'][data.get('colName')] = {}

    elif mode == 'col_order':
        try:
            cnt = 0
            for uuid in data.get('uuidList'):
                uuid = uuid[5:]
                if uuid in board_info['data'][data.get('colName')]:
                    board_info['data'][data.get('colName')][uuid]["pos"] = cnt
                    cnt += 1

                else:
                    for col_name, col_data in board_info["data"].items():
                        if uuid in col_data:
                            board_info["tmps"][uuid] = board_info["data"][col_name][
                                uuid
                            ]
                            del board_info["data"][col_name][uuid]

                if uuid in board_info["tmps"]:
                    board_info["data"][data.get("colName")][uuid] = board_info["tmps"][
                        uuid
                    ]
                    del board_info["tmps"][uuid]
                    board_info["data"][data.get("colName")][uuid]["pos"] = cnt
                    cnt += 1
        
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(e, exc_type, fname, exc_tb.tb_lineno)

    elif mode == 'col_delete':
        if data.get('colName') not in board_info['data']:
            return False

        del board_info['data'][data.get('colName')]

    board_path = f'./board/{board_id}.json'
    with open(board_path, 'w', encoding='utf-8') as f:
        json.dump(board_info, f, indent=4)
    return True

async def board_timer(clients, msg):
    timer_in_seconds = int(msg.get('timerInSeconds'))
    while timer_in_seconds:
        for ws in clients:
            await ws.send(json.dumps({
                'type': 'timer',
                'timer': timer_in_seconds,
                'board_id': msg.get('board_id')
            }))

        timer_in_seconds -= 1
        time.sleep(1)


async def handler(websocket):
    global users, clients, pos

    print('new_client>')
    clients.add(websocket)
    client_id = pos
    pos += 1

    try:
        while True:
            msg = await websocket.recv()
            # print(f'From Client: {msg}')

            data = json.loads(msg)
            message_type = data.get('type')
            board_id = data.get('board_id')

            if message_type == 'board_list':
                board_author = data.get('username')
                await websocket.send(json.dumps({
                    'type': 'board_list',
                    'board_list': get_board_list_by_author(board_author)
                }))

            elif message_type == 'connect':
                message_username = data.get('username')
                users[client_id] = {
                    'username': message_username,
                    'color': generate_color(message_username),
                    'board_id': board_id
                }

                await websocket.send(json.dumps({
                    'type': 'connect_status',
                    'user_id': client_id,
                    'error': False,
                    'board_id': board_id
                }))

                await websocket.send(json.dumps({
                    'type': 'users_list',
                    'users_list': users,
                    'board_id': board_id
                }))

                for ws in clients:
                    await ws.send(json.dumps({
                        'type': 'user_add',
                        'user_id': client_id,
                        'username': message_username,
                        'board_id': board_id,
                        'color': generate_color(message_username)
                    }))

            elif message_type == 'cursor_user':
                message_content = data.get('content')
                pos_x = data.get('pos_x')
                pos_y = data.get('pos_y')
                for ws in clients:
                    await ws.send(json.dumps({
                        'type': 'cursor_user',
                        'user_id': client_id,
                        'pos_x': pos_x,
                        'pos_y': pos_y,
                        'board_id': board_id
                    }))

            elif message_type == 'board_info':
                await websocket.send(json.dumps({
                    'type': 'board_info',
                    'board_info': get_board_info_by_id(board_id, data.get('username', False)),
                    'board_id': board_id
                }))

            elif message_type == 'start_timer':
                timer_in_seconds = data.get('timer_in_seconds')
                utc_now = datetime.datetime.now()
                delta = datetime.timedelta(seconds=int(timer_in_seconds))
                future_time_utc = utc_now + delta
                users[client_id]['timer'] = int(future_time_utc.timestamp() * 1000)
                get_board_info_by_id(board_id, future_time_utc)
                for ws in clients:
                    await ws.send(json.dumps({
                        'type': 'start_timer',
                        'board_id': board_id,
                        'timer_in_seconds': timer_in_seconds
                    }))

            elif message_type == 'start_vote':
                board_votes_reset_by_id(board_id)
                for ws in clients:
                    await ws.send(json.dumps(data))

            elif message_type == 'start_confetti':
                for ws in clients:
                    await ws.send(json.dumps(data))

            elif message_type in ('card_add', 'card_edit', 'card_view', 'card_vote', 'card_delete'):
                card_uuid, card_votes = board_manager_by_id(board_id, message_type, data)
                for ws in clients:
                    message_data = data.copy()
                    if message_type in ('card_add', 'card_edit'):
                        message_data['cardContent'] = data['cardContent']
                        if websocket != ws:
                            message_data['cardContent'] = '~~~'

                    to_send = json.dumps({
                        'type': message_type,
                        'board_id': board_id,
                        'card_uuid': card_uuid,
                        'card_votes': card_votes,
                        message_type: message_data
                    })
                    await ws.send(to_send)

            elif message_type in ('col_add', 'col_order', 'col_delete'):
                col_manager_by_board_id(board_id, message_type, data)
                for ws in clients:
                    await ws.send(json.dumps({
                        'type': message_type,
                        'board_id': board_id,
                        message_type: data
                    }))

            elif message_type == 'message':
                message_content = data.get('content')
                if "/see_all_cards" in message_content:
                    board_info = get_board_info_by_id(board_id)
                    if not board_info:
                        return False

                    for col_name in board_info["data"]:
                        for card_uuid, _ in board_info["data"][col_name].items():
                            board_info["data"][col_name][card_uuid]["hidden"] = False

                    board_path = f'./board/{board_id}.json'
                    with open(board_path, 'w', encoding='utf-8') as f:
                        json.dump(board_info, f, indent=4)

                    for ws in clients:
                        await ws.send(json.dumps({
                            'type': 'force_reload',
                            'user_id': client_id,
                            'username': users[client_id]['username'],
                            'board_id': board_id
                        }))

                else:
                    for ws in clients:
                        await ws.send(json.dumps({
                            'type': 'message',
                            'user_id': client_id,
                            'username': users[client_id]['username'],
                            'content': message_content,
                            'board_id': board_id
                        }))

            else:
                print('unknow_type:', message_type, msg)

    except websockets.exceptions.ConnectionClosedOK:
        print('close_client>')

    except Exception as e:
        exc_type, _, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)

    finally:
        clients.remove(websocket)

        for ws in clients:
            if client_id in users:
                await ws.send(json.dumps({
                    'type': 'user_remove',
                    'user_id': client_id,
                    'username': users[client_id]['username'],
                    'board_id': board_id
                }))

        if client_id in users:
            del users[client_id]

async def main():
    async with websockets.serve(handler, '0.0.0.0', 8009):
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    asyncio.run(main())
