#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Retrogile WS
"""

import os
import json
import uuid
import hashlib
import asyncio
import datetime
import websockets


users = {}
clients = set()
POS = 0


def generate_color(_key):
    """
    Generates a unique hexadecimal color code based on the given key.

    Args:
        key (str): The input key string.

    Returns:
        str: The generated hexadecimal color code in the format "#XXXXXX".
    """
    hash_object = hashlib.sha256(_key.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    color_hex = f"#{hex_dig[:6]}"
    return color_hex


def get_board_list_by_author(author):
    """
    Retrieves a list of board files authored by a specific user.

    Args:
        author (str): The name of the author to search for.

    Returns:
        List[List[str]]: A list of lists, where each inner list contains:
            - The name of the board.
            - The path to the board's JSON file.
    """
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
    """
    Retrieves information about a specific board.

    Args:
        board_id (str): The ID of the board to retrieve.
        username_filter (bool, optional): Whether to filter the board data
                                            based on the specified username.
                                            Defaults to False.

    Returns:
        Union[dict, bool]:
            - If the board is found and the username filter is not applied,
                returns a dictionary containing the board data.
            - If the board is found and the username filter is applied,
                returns a dictionary with filtered card content.
            - If the board is not found, returns False.
    """
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


def update_timer_in_board(board_id, new_timer_value):
    """
    Updates the timer value in a specified board.

    Args:
        board_id (int): The unique identifier of the board to update.
        new_timer_value (datetime.datetime): The new timer value.

    Returns:
        bool: True if the update was successful, False otherwise.

    This function retrieves the board information based on the provided.
    If the board exists, it updates the `timer` field with the timestamp
    of the `new_timer_value` in milliseconds.
    The updated board information is then written to a JSON file.
    """
    board_info = get_board_info_by_id(board_id)
    if board_info:
        board_info['timer'] = int(new_timer_value.timestamp() * 1000)
        board_path = f'./board/{board_id}.json'
        with open(board_path, 'w', encoding='utf-8') as f:
            json.dump(board_info, f, indent=4)
        return True

    return False


def reset_votes_in_nested_dict(my_dict):
    """
    Recursively resets the "votes" value to 0 in a nested dictionary.

    This function iterates through a nested dictionary and sets the value of
    the "votes" key to 0 for all occurrences. 
    It recursively traverses nested dictionaries to ensure that all "votes"
    values are reset.

    Args:
        my_dict (dict): The nested dictionary to be processed.

    Returns:
        dict: The modified nested dictionary with all "votes" values reset.
    """
    for key, value in my_dict.items():
        if isinstance(value, dict):
            reset_votes_in_nested_dict(value)
        elif key == "votes":
            my_dict[key] = 0

    return my_dict


def board_votes_reset_by_id(board_id):
    """
    Resets the vote count for a specific board.

    Args:
        board_id (int): The ID of the board to reset.

    Returns:
        bool: True if the reset was successful, False otherwise.
    """
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

    return True


def board_manager_by_id(board_id, mode, data):
    """
    Manages board operations based on the specified mode.

    Args:
        board_id (str): The unique identifier of the board.
        mode (str): The operation mode, one of:
            - 'card_add': Add a new card to the board.
            - 'card_edit': Edit an existing card.
            - 'card_view': Mark a card as visible to the author.
            - 'card_vote': Increment the vote count of a card.
            - 'card_delete': Delete a card from the board.
        data (dict): A dictionary containing additional data for the specific
            operation, including:
            - 'col_id': The ID of the column.
            - 'card_uuid': The UUID of the card
                (for edit, view, vote, and delete).
            - 'author': The author of the card.
            - 'user_id': The user ID of the author.
            - 'cardContent': The content of the card.
            - 'pos': The position of the card within the column.

    Returns:
        tuple[str, int]: A tuple containing the card UUID and the number of
                            votes, or (None, 0) if the operation fails.
    """
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
        if (
            data.get('col_id') in board_info['data']
            and data.get('card_uuid') in board_info['data'][data.get('col_id')]
        ):
            board_info['data'][
                data.get('col_id')][
                data.get('card_uuid')]['content'] = data.get('cardContent')

    elif mode == 'card_view':
        for col_name in board_info["data"]:
            for card_uuid, card_data in board_info["data"][col_name].items():
                if card_data["author"] == data.get('author'):
                    board_info["data"][col_name][card_uuid]["hidden"] = False

    elif mode == 'card_vote':
        if(
            data.get('col_id') in board_info['data']
            and data.get('card_uuid') in board_info['data'][data.get('col_id')]
        ):
            board_info['data'][
                data.get('col_id')][
                data.get('card_uuid')]['votes'] += 1
            card_votes = board_info['data'][
                data.get('col_id')][
                data.get('card_uuid')]['votes']

    elif mode == 'card_delete':
        if(
            data.get('col_id') in board_info['data']
            and data.get('card_uuid') in board_info['data'][data.get('col_id')]
        ):
            del board_info['data'][data.get('col_id')][data.get('card_uuid')]

    board_path = f'./board/{board_id}.json'
    with open(board_path, 'w', encoding='utf-8') as f:
        json.dump(board_info, f, indent=4)
    return card_uuid, card_votes


def col_manager_by_board_id(board_id, mode, data):
    """
    Manages column operations for a specific board.

    Args:
        board_id (str): The unique identifier of the board.
        mode (str): The operation mode, one of 'col_add', 'col_order',
                    or 'col_delete'.
        data (dict): A dictionary containing additional data for
                    the specific operation.

    Returns:
        bool: True if the operation was successful, False otherwise.

    Raises:
        Exception: If an error occurs during the operation.
    """
    board_info = get_board_info_by_id(board_id)
    if not board_info:
        return False

    if mode == 'col_add':
        if data.get('colName') in board_info['data']:
            return False

        board_info['data'][data.get('colName')] = {}

    elif mode == 'col_order':
        cnt = 0
        for uuidl in data.get('uuidList'):
            uuidl = uuidl[5:]
            if uuidl in board_info['data'][data.get('colName')]:
                board_info['data'][data.get('colName')][uuidl]["pos"] = cnt
                cnt += 1

            else:
                for col_name, col_data in board_info["data"].items():
                    if uuidl in col_data:
                        board_info["tmps"][uuidl] = board_info["data"][col_name][
                            uuidl
                        ]
                        del board_info["data"][col_name][uuidl]

            if uuidl in board_info["tmps"]:
                board_info["data"][data.get("colName")][uuidl] = board_info["tmps"][
                    uuidl
                ]
                del board_info["tmps"][uuidl]
                board_info["data"][data.get("colName")][uuidl]["pos"] = cnt
                cnt += 1

    elif mode == 'col_delete':
        if data.get('colName') not in board_info['data']:
            return False

        del board_info['data'][data.get('colName')]

    board_path = f'./board/{board_id}.json'
    with open(board_path, 'w', encoding='utf-8') as f:
        json.dump(board_info, f, indent=4)
    return True


def send_list_multi(send_list, clients_lst, msg_data):
    """
    Appends a tuple of clients and message data to a send list.

    Args:
        send_list: A list to store tuples of clients and message data.
        clients_lst: A list of clients to send the message to.
        msg_data: The message data to be sent.

    Returns:
        list: send_list
    """
    for client in clients_lst:
        send_list.append([client, msg_data])
    return send_list


def message_responce(send_list, websocket, board_id, client_id, data):
    """
    Processes a received message and builds a list of messages to send.

    This function takes a message received from a websocket client,
    analyzes its type, and creates appropriate responses.
    The responses are added to a `send_list` which is a list of tuples
    containing the target websocket and the message data to be sent.

    Args:
        send_list: A list to store tuples of target websockets and message.
        websocket: The websocket that sent the original message.
        board_id: The ID of the board the message is related to.
        client_id: The ID of the client who sent the message.
        data: The data payload of the received message.

    Returns:
        The updated `send_list` containing messages to be sent to clients.
    """

    message_type = data.get('type')
    if message_type == 'board_list':
        board_author = data.get('username')
        send_list.append([websocket, {
            'type': 'board_list',
            'board_list': get_board_list_by_author(board_author)
        }])

    elif message_type == 'connect':
        message_username = data.get('username')
        users[client_id] = {
            'username': message_username,
            'color': generate_color(message_username),
            'board_id': board_id
        }

        send_list.append([websocket, {
            'type': 'connect_status',
            'user_id': client_id,
            'error': False,
            'board_id': board_id
        }])

        send_list.append([websocket, {
            'type': 'users_list',
            'users_list': users,
            'board_id': board_id
        }])

        send_list = send_list_multi(send_list, clients, {
            'type': 'user_add',
            'user_id': client_id,
            'username': message_username,
            'board_id': board_id,
            'color': generate_color(message_username)
        })

    elif message_type == 'cursor_user':
        message_content = data.get('content')
        pos_x = data.get('pos_x')
        pos_y = data.get('pos_y')

        send_list = send_list_multi(send_list, clients, {
            'type': 'cursor_user',
            'user_id': client_id,
            'pos_x': pos_x,
            'pos_y': pos_y,
            'board_id': board_id
        })

    elif message_type == 'board_info':
        send_list.append([websocket, {
            'type': 'board_info',
            'board_info': get_board_info_by_id(board_id, data.get('username', False)),
            'board_id': board_id
        }])

    elif message_type == 'start_timer':
        timer_in_seconds = data.get('timerInSeconds')
        utc_now = datetime.datetime.now()
        delta = datetime.timedelta(seconds=int(timer_in_seconds))
        future_time_utc = utc_now + delta
        users[client_id]['timer'] = int(future_time_utc.timestamp() * 1000)
        update_timer_in_board(board_id, future_time_utc)
        send_list = send_list_multi(send_list, clients, {
            'type': 'start_timer',
            'board_id': board_id,
            'timerInSeconds': timer_in_seconds
        })

    elif message_type == 'start_vote':
        board_votes_reset_by_id(board_id)
        send_list = send_list_multi(send_list, clients, data)

    elif message_type == 'start_confetti':
        send_list = send_list_multi(send_list, clients, data)

    elif message_type in ('card_add', 'card_edit', 'card_view', 'card_vote', 'card_delete'):
        card_uuid, card_votes = board_manager_by_id(board_id, message_type, data)
        for ws in clients:
            message_data = data.copy()
            if message_type in ('card_add', 'card_edit'):
                message_data['cardContent'] = data['cardContent']
                if websocket != ws:
                    message_data['cardContent'] = '~~~'

            send_list.append([ws, {
                'type': message_type,
                'board_id': board_id,
                'card_uuid': card_uuid,
                'card_votes': card_votes,
                message_type: message_data
            }])

    elif message_type in ('col_add', 'col_order', 'col_delete'):
        col_manager_by_board_id(board_id, message_type, data)
        send_list = send_list_multi(send_list, clients, {
            'type': message_type,
            'board_id': board_id,
            message_type: data
        })

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

            send_list = send_list_multi(send_list, clients, {
                'type': 'force_reload',
                'user_id': client_id,
                'username': users[client_id]['username'],
                'board_id': board_id
            })

        else:
            send_list = send_list_multi(send_list, clients, {
                'type': 'message',
                'user_id': client_id,
                'username': users[client_id]['username'],
                'content': message_content,
                'board_id': board_id
            })

    return send_list


async def handler(websocket):
    """
    Handles incoming WebSocket messages and dispatches them to appropriate
    functions based on message type.

    This function manages the connection with a single websocket client.
    It receives messages, parses them as JSON, and
    then calls the appropriate functions based on the message type.

    Args:
        websocket: A websocket object representing the connection
                    to the client.

    Raises:
        websockets.exceptions.ConnectionClosedOK:
            Raised when the client closes the connection gracefully.
        Exception: Raised for any other unexpected errors during communication.
    """
    # pylint: disable=W0602
    global users, clients, POS

    print('new_client>')
    clients.add(websocket)
    client_id = POS
    send_list = []
    POS += 1

    try:
        while True:
            data = json.loads(await websocket.recv())
            board_id = data.get('board_id')
            send_list = message_responce(
                send_list, websocket,
                client_id, data)
            if len(send_list) > 0:
                for ws_client, message in send_list:
                    await ws_client.send(json.dumps(message))

            send_list = []

    except websockets.exceptions.ConnectionClosedOK:
        print('close_client>')

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
    """
    Starts a WebSocket server on port 8009, listening on all interfaces.

    This function initiates an asynchronous WebSocket server
    The `handler` function (not shown) is responsible for handling incoming
    The server runs indefinitely until it's manually stopped.
    """
    async with websockets.serve(handler, '0.0.0.0', 8009):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
