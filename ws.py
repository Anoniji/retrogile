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
from collections import OrderedDict
import websockets


BOARD_VERSION = 3
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
    hash_object = hashlib.sha256(_key.encode("utf-8"))
    hex_dig = hash_object.hexdigest()
    color_hex = f"#{hex_dig[:6]}"
    return color_hex


def update_board(board_data_old):
    """
    Updates the given board data.

    This function checks the current version of the board data.
    If the version is 1, it updates the version to 2 and
    clears the users_list.

    Args:
        board_data_old: A dictionary containing the old board data.

    Returns:
        The updated board data.
    """
    if board_data_old["version"] <= 1:
        board_data_old["version"] = 2
        board_data_old["users_list"] = []

    if board_data_old["version"] <= 2:
        board_data_old["version"] = 3
        for category in board_data_old["data"]:
            for _, child_data in board_data_old["data"][category].items():
                child_data["children"] = []

        board_data_old["users_list"] = []

    return board_data_old


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
    directory = "./board/"
    author_files = []
    for file in os.listdir(directory):
        if file.endswith(".json"):
            file_path = os.path.join(directory, file)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data["author"] == author:
                    curr_version = data.get("version", False)
                    if curr_version:
                        temps_modification = os.path.getmtime(file_path)
                        date_modification = datetime.datetime.fromtimestamp(temps_modification)
                        date_format = "%Y-%m-%d %H:%M:%S"
                        date_format = date_modification.strftime(date_format)

                        author_files.append(
                            {
                                'board_name': data["board_name"],
                                'board_version': BOARD_VERSION,
                                'current_version': curr_version,
                                'path': file_path,
                                'last_edit': date_format,
                            }
                        )
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
        board_path = f"./board/{board_id}.json"
        if os.path.isfile(board_path):
            with open(board_path, encoding="utf-8") as f:
                _tmps = json.load(f)

                if "version" not in _tmps:
                    return False

                if _tmps["version"] != BOARD_VERSION:
                    _tmps = update_board(_tmps)
                    with open(board_path, "w", encoding="utf-8") as f:
                        json.dump(_tmps, f, indent=4)

                if not username_filter:
                    return _tmps

                for col_name in _tmps["data"]:
                    for card_uuid, card_data in _tmps["data"][col_name].items():
                        if (
                            card_data["author"] != username_filter
                            and card_data["hidden"]
                        ):
                            _tmps["data"][
                                col_name][
                                card_uuid][
                                "content"] = "<div class='hide_content'></div>"

                return OrderedDict(_tmps.items())

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
        board_info["timer"] = int(new_timer_value.timestamp() * 1000)
        board_path = f"./board/{board_id}.json"
        with open(board_path, "w", encoding="utf-8") as f:
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


def board_votes_reset_by_id(board_id, max_vote):
    """
    Resets the vote count for a specific board.

    Args:
        board_id (int): The ID of the board to reset.
        max_vote (int): Board max Votes.

    Returns:
        bool: True if the reset was successful, False otherwise.
    """
    board_info = get_board_info_by_id(board_id)
    if not board_info:
        return False

    board_info["votes"] = int(max_vote)
    board_info["votes_list"] = {}
    for key, value in board_info["data"].items():
        if isinstance(value, dict):
            reset_votes_in_nested_dict(value)
        elif key == "votes":
            board_info["data"][key] = 0

    board_path = f"./board/{board_id}.json"
    with open(board_path, "w", encoding="utf-8") as f:
        json.dump(board_info, f, indent=4)

    return True


def board_votes_init(board_id, max_vote):
    """
    Initializes the votes for all users in a given board.

    Args:
        board_id (str): The ID of the board.
        max_vote (int): The maximum number of votes allowed per user.

    Returns:
        bool: True if the initialization was successful, False otherwise.
    """
    board_info = get_board_info_by_id(board_id)
    if not board_info:
        return False

    for user in board_info["users_list"]:
        board_info["votes_list"][user] = int(max_vote)

    board_path = f"./board/{board_id}.json"
    with open(board_path, "w", encoding="utf-8") as f:
        json.dump(board_info, f, indent=4)

    return True


def find_content_by_id(data, id_to_find, parent=False):
    """
    Searches for the given ID within the nested dictionary structure and
    returns its associated content and the path to the ID.

    Args:
        data: The dictionary to search.
        id_to_find: The ID to search for.
        parent: The name of the parent key (optional, default: False).
             Used for tracking the path to the ID.

    Returns:
        A tuple containing:
          - The content associated with the given ID if found, otherwise None.
          - A list representing the path to the ID, starting from the root.
            If the ID is not found, the list is empty.
    """
    if not data or not id_to_find:
        return None, []

    result = False
    for key, value in data.items():
        if key == id_to_find:
            return value, parent
        elif isinstance(value, dict):
            result, path = find_content_by_id(value, id_to_find, key)
        if result:
            return result, path if parent else path

    return None, []


def board_manager_by_id(send_list, board_id, mode, websocket, data):
    """
    Manages board operations based on the specified mode.

    Args:
        send_list: A list to store messages for sending to clients.
        board_id: The unique identifier of the board.
        mode: The operation mode:
            - 'card_add': Add a new card to the board.
            - 'card_edit': Edit an existing card.
            - 'card_view': Mark a card as visible to the author.
            - 'card_vote': Increment the vote count of a card.
            - 'card_delete': Delete a card from the board.
        websocket: The WebSocket connection of the current user.
        data: A dictionary containing additional data for the specific operation.

    Returns:
        The updated send_list with messages for each client.
    """
    board_info = get_board_info_by_id(board_id)
    if not board_info:
        return False

    card_uuid = uuid.uuid4().hex
    card_votes = 0
    if mode == "card_add":
        board_info["data"][data.get("col_id")][card_uuid] = {
            "pos": data.get("pos"),
            "author": data.get("author"),
            "author_id": data.get("user_id"),
            "content": data.get("cardContent"),
            "hidden": True,
            "votes": 0,
            "children": [],
        }

    elif mode == "card_edit":
        if (
            data.get("col_id") in board_info["data"]
            and data.get("card_uuid") in board_info["data"][data.get("col_id")]
        ):
            board_info["data"][data.get("col_id")][data.get("card_uuid")]["content"] = (
                data.get("cardContent")
            )

    elif mode == "card_parent":
        parentId = data.get("card_uuid")
        childId = data.get("cardContent")

        parentCard, parentCol = find_content_by_id(
            board_info["data"], parentId)
        childCard, childCol = find_content_by_id(
            board_info["data"], childId)

        if parentCard and childCard:
            del childCard['pos']
            del childCard['votes']
            del childCard['hidden']
            del childCard['children']
            board_info["data"][parentCol][parentId]["children"].append(
                childCard)
            del board_info["data"][childCol][childId]

    elif mode == "card_view":
        for col_name in board_info["data"]:
            for card_uuid, card_data in board_info["data"][col_name].items():
                if card_data["author"] == data.get("author"):
                    board_info["data"][col_name][card_uuid]["hidden"] = False

    elif mode == "card_vote":
        if (
            data.get("col_id") in board_info["data"]
            and data.get("card_uuid") in board_info["data"][data.get("col_id")]
        ):
            if data.get("author") not in board_info["votes_list"]:
                board_info["votes_list"][data.get("author")] = board_info["votes"] - 1
            elif not board_info["votes_list"][data.get("author")]:
                return False
            else:
                board_info["votes_list"][data.get("author")] -= 1

            board_info["data"][data.get("col_id")][data.get("card_uuid")]["votes"] += 1
            card_votes = board_info["data"][data.get("col_id")][data.get("card_uuid")][
                "votes"
            ]

    elif mode == "card_delete":
        if (
            data.get("col_id") in board_info["data"]
            and data.get("card_uuid") in board_info["data"][data.get("col_id")]
        ):
            del board_info["data"][data.get("col_id")][data.get("card_uuid")]

    board_path = f"./board/{board_id}.json"
    with open(board_path, "w", encoding="utf-8") as f:
        json.dump(board_info, f, indent=4)

    for ws in clients:
        message_data = data.copy()
        if mode in ("card_add", "card_edit"):
            message_data["cardContent"] = data["cardContent"]
            if websocket != ws:
                message_data["cardContent"] = "<div class='hide_content'></div>"

        send_list.append(
            [
                ws,
                {
                    "type": mode,
                    "board_id": board_id,
                    "card_uuid": card_uuid,
                    "card_votes": card_votes,
                    mode: message_data,
                },
            ]
        )

    return send_list


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

    if mode == "col_add":
        if data.get("colName") in board_info["data"]:
            return False

        board_info["data"][data.get("colName")] = {}

    elif mode == "col_order":
        cnt = 0
        for uuidl in data.get("uuidList"):
            uuidl = uuidl[5:]
            if uuidl in board_info["data"][data.get("colName")]:
                board_info["data"][data.get("colName")][uuidl]["pos"] = cnt
                cnt += 1

            else:
                for col_name, col_data in board_info["data"].items():
                    if uuidl in col_data:
                        board_info["tmps"][uuidl] = board_info["data"][col_name][uuidl]
                        del board_info["data"][col_name][uuidl]

            if uuidl in board_info["tmps"]:
                board_info["data"][data.get("colName")][uuidl] = board_info["tmps"][
                    uuidl
                ]
                del board_info["tmps"][uuidl]
                board_info["data"][data.get("colName")][uuidl]["pos"] = cnt
                cnt += 1

    elif mode == "col_reorder":
        board_info["data"] = OrderedDict(
            (k, board_info["data"][k]) for k in data.get("colName")
        )

    elif mode == "col_delete":
        if data.get("colName") not in board_info["data"]:
            return False

        del board_info["data"][data.get("colName")]

    board_path = f"./board/{board_id}.json"
    with open(board_path, "w", encoding="utf-8") as f:
        json.dump(board_info, f, indent=4)
    return True


def add_user_to_board(board_id, username):
    """
    Adds a user to the specified board.

    Args:
        board_id (str): The ID of the board.
        username (str): The username of the user to add.

    Returns:
        bool: True if the user was successfully added, False otherwise.
    """
    board_info = get_board_info_by_id(board_id)
    if not board_info:
        return False

    board_users_list = board_info.get("users_list")
    if username not in board_users_list:
        board_info["users_list"].append(username)

    board_path = f"./board/{board_id}.json"
    with open(board_path, "w", encoding="utf-8") as f:
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

    message_type = data.get("type")
    if message_type == "board_list":
        send_list.append(
            [
                websocket,
                {
                    "type": "board_list",
                    "board_list": get_board_list_by_author(data.get("username")),
                },
            ]
        )

    elif message_type == "connect":
        message_username = data.get("username")
        users[client_id] = {
            "username": message_username,
            "color": generate_color(message_username),
            "board_id": board_id,
        }

        send_list.append(
            [
                websocket,
                {
                    "type": "connect_status",
                    "user_id": client_id,
                    "error": False,
                    "board_id": board_id,
                },
            ]
        )

        send_list.append(
            [
                websocket,
                {"type": "users_list", "users_list": users, "board_id": board_id},
            ]
        )

        send_list = send_list_multi(
            send_list,
            clients,
            {
                "type": "user_add",
                "user_id": client_id,
                "username": message_username,
                "board_id": board_id,
                "color": generate_color(message_username),
            },
        )

        add_user_to_board(board_id, message_username)

    elif message_type == "cursor_user":
        send_list = send_list_multi(
            send_list,
            clients,
            {
                "type": "cursor_user",
                "user_id": client_id,
                "pos_x": data.get("pos_x"),
                "pos_y": data.get("pos_y"),
                "board_id": board_id,
            },
        )

    elif message_type == "board_info":
        send_list.append(
            [
                websocket,
                {
                    "type": "board_info",
                    "board_info": get_board_info_by_id(
                        board_id, data.get("username", False)
                    ),
                    "board_id": board_id,
                },
            ]
        )

    elif message_type == "start_timer":
        timer_in_seconds = data.get("timerInSeconds")
        delta = datetime.timedelta(seconds=int(timer_in_seconds))
        future_time_utc = datetime.datetime.now() + delta
        users[client_id]["timer"] = int(future_time_utc.timestamp() * 1000)
        update_timer_in_board(board_id, future_time_utc)
        send_list = send_list_multi(
            send_list,
            clients,
            {
                "type": "start_timer",
                "board_id": board_id,
                "timerInSeconds": timer_in_seconds,
            },
        )

    elif message_type == "start_vote":
        board_votes_reset_by_id(board_id, data.get("maxVote"))
        board_votes_init(board_id, data.get("maxVote"))
        send_list = send_list_multi(send_list, clients, data)

    elif message_type == "start_confetti":
        send_list = send_list_multi(send_list, clients, data)

    elif message_type in (
        "card_add",
        "card_edit",
        "card_parent",
        "card_view",
        "card_vote",
        "card_delete",
    ):
        send_list = board_manager_by_id(
            send_list, board_id, message_type, websocket, data
        )

    elif message_type in ("col_add", "col_order", "col_reorder", "col_delete"):
        col_manager_by_board_id(board_id, message_type, data)
        send_list = send_list_multi(
            send_list,
            clients,
            {"type": message_type, "board_id": board_id, message_type: data},
        )

    elif message_type == "message":
        message_content = data.get("content")
        if "/see_all_cards" in message_content:
            board_info = get_board_info_by_id(board_id)
            if not board_info:
                return False

            for col_name in board_info["data"]:
                for card_uuid, _ in board_info["data"][col_name].items():
                    board_info["data"][col_name][card_uuid]["hidden"] = False

            with open(f"./board/{board_id}.json", "w", encoding="utf-8") as f:
                json.dump(board_info, f, indent=4)

            return send_list_multi(
                send_list,
                clients,
                {
                    "type": "force_reload",
                    "user_id": client_id,
                    "username": users[client_id]["username"],
                    "board_id": board_id,
                },
            )

        send_list = send_list_multi(
            send_list,
            clients,
            {
                "type": "message",
                "user_id": client_id,
                "username": users[client_id]["username"],
                "content": message_content,
                "board_id": board_id,
            },
        )

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

    print("new_client>")
    clients.add(websocket)
    client_id = POS
    board_id = False
    send_list = []
    POS += 1

    try:
        while True:
            data = json.loads(await websocket.recv())
            board_id = data.get("board_id")
            send_list = message_responce(
                send_list, websocket, board_id, client_id, data
            )
            if len(send_list) > 0:
                for ws_client, message in send_list:
                    await ws_client.send(json.dumps(message))

            send_list = []

    except websockets.exceptions.ConnectionClosedOK:
        print("close_client>")

    finally:
        clients.remove(websocket)

        for ws in clients:
            if client_id in users:
                await ws.send(
                    json.dumps(
                        {
                            "type": "user_remove",
                            "user_id": client_id,
                            "username": users[client_id]["username"],
                            "board_id": board_id,
                        }
                    )
                )

        if client_id in users:
            del users[client_id]


async def main():
    """
    Starts a WebSocket server on port 8009, listening on all interfaces.

    This function initiates an asynchronous WebSocket server
    The `handler` function (not shown) is responsible for handling incoming
    The server runs indefinitely until it's manually stopped.
    """
    async with websockets.serve(handler, "0.0.0.0", 8009):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
