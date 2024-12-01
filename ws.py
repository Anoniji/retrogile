import asyncio
import datetime
import websockets
import os
import sys
import json
import time
import uuid

users = {}
clients = set()
pos = 0


def getBoardInfoById(board_id):
    if board_id:
        board_path = f'./board/{board_id}.json'
        if os.path.isfile(board_path):
            with open(board_path) as f:
                return json.load(f)

    return False


def updateTimerInBoard(board_id, new_timer_value):
    board_info = getBoardInfoById(board_id)
    if board_info:
        board_info['timer'] = int(new_timer_value.timestamp() * 1000)
        board_path = f'./board/{board_id}.json'
        with open(board_path, 'w') as f:
            json.dump(board_info, f, indent=4)
        return True
    else:
        return False


def boardManagerById(board_id, mode, data):
    board_info = getBoardInfoById(board_id)
    if not board_info:
        return False

    card_uuid = uuid.uuid4().hex
    if mode == 'card_add':
        board_info['data'][data.get('col_id')][card_uuid] = {
            'pos': data.get('pos'),
            'author': data.get('author'),
            'author_id': data.get('user_id'),
            'content': data.get('cardContent'),
            'votes': 0
        }

    elif mode == 'card_edit':
        if(data.get('col_id') in board_info['data'] and data.get('card_uuid') in board_info['data'][data.get('col_id')]):
            board_info['data'][data.get('col_id')][data.get('card_uuid')]['content'] = data.get('cardContent')

    elif mode == 'card_delete':
        if(data.get('col_id') in board_info['data'] and data.get('card_uuid') in board_info['data'][data.get('col_id')]):
            del board_info['data'][data.get('col_id')][data.get('card_uuid')]

    board_path = f'./board/{board_id}.json'
    with open(board_path, 'w') as f:
        json.dump(board_info, f, indent=4)
    return card_uuid


def colManagerByBoardId(board_id, mode, data):
    board_info = getBoardInfoById(board_id)
    if not board_info:
        return False

    if mode == 'col_add':
        if data.get('colName') in board_info['data']:
            return False

        board_info['data'][data.get('colName')] = {}

    elif mode == 'col_delete':
        if data.get('colName') not in board_info['data']:
            return False

        del board_info['data'][data.get('colName')]

    board_path = f'./board/{board_id}.json'
    with open(board_path, 'w') as f:
        json.dump(board_info, f, indent=4)
    return True

async def board_timer(clients, msg):
    print(msg, type(msg))
    timerInSeconds = int(msg.get('timerInSeconds'))
    while timerInSeconds:
        print(timerInSeconds)
        for ws in clients:
            await ws.send(json.dumps({
                'type': 'timer',
                'timer': timerInSeconds,
                'board_id': msg.get('board_id')
            }))

        timerInSeconds -= 1
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

            if message_type == 'connect':
                message_username = data.get('username')
                users[client_id] = {
                    'username': message_username,
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
                        'board_id': board_id
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
                    'board_info': getBoardInfoById(board_id),
                    'board_id': board_id
                }))

            elif message_type == 'start_timer':
                timerInSeconds = data.get('timerInSeconds')
                utc_now = datetime.datetime.now()
                delta = datetime.timedelta(seconds=int(timerInSeconds))
                future_time_utc = utc_now + delta
                users[client_id]['timer'] = future_time_utc
                updateTimerInBoard(board_id, future_time_utc)
                for ws in clients:
                    await ws.send(json.dumps({
                        'type': 'start_timer',
                        'board_id': board_id,
                        'timerInSeconds': timerInSeconds
                    }))

            elif message_type in ('card_add', 'card_edit', 'card_delete'):
                card_uuid = boardManagerById(board_id, message_type, data)
                for ws in clients:
                    await ws.send(json.dumps({
                        'type': message_type,
                        'board_id': board_id,
                        'card_uuid': card_uuid,
                        message_type: data
                    }))

            elif message_type in ('col_add', 'col_edit', 'col_delete'):
                colManagerByBoardId(board_id, message_type, data)
                for ws in clients:
                    await ws.send(json.dumps({
                        'type': message_type,
                        'board_id': board_id,
                        message_type: data
                    }))

            elif message_type == 'message':
                message_content = data.get('content')
                # websocket.send(message_content)

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

    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    finally:
        clients.remove(websocket)

        for ws in clients:
            await ws.send(json.dumps({
                'type': 'user_remove',
                'user_id': client_id,
                'username': users[client_id]['username'],
                'board_id': board_id
            }))

        if client_id in users:
            del users[client_id]

async def main():
    async with websockets.serve(handler, 'localhost', 8009):
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    asyncio.run(main())
