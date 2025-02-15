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
from pathlib import Path
from collections import OrderedDict
import websockets

from libs import licence, tools, boards
boards = boards.Board()


BOARD_VERSION = 4
users = {}
clients = set()
POS = 0


def username_color(board_id, username):
    """
    Generates a unique hexadecimal color code for a username.

    First, it checks if a custom color is defined for the user in the specified board's JSON file.
    If a custom color is found, it returns that color. Otherwise, it generates a dark color 
    based on the username using a SHA256 hash.

    Args:
        board_id (str): The ID of the board.
        username (str): The username.

    Returns:
        str: The hexadecimal color code in the format "#RRGGBB".
    """

    if board_id:
        _tmps, _ = boards.get_board(board_id)
        if "users_list" in _tmps and isinstance(_tmps["users_list"], dict):
            user_param = _tmps["users_list"].get(username)
            if user_param:
                custom_color = user_param.get("custom_color")
                if custom_color:
                    return custom_color

    # If no custom color is found, generate a dark color based on the username.
    hash_object = hashlib.sha256(username.encode("utf-8"))
    hex_dig = hash_object.hexdigest()

    # Convert the first 6 hex characters to integers (representing R, G, and B).
    r = int(hex_dig[:2], 16)
    g = int(hex_dig[2:4], 16)
    b = int(hex_dig[4:6], 16)

    # Adjust the RGB values to ensure a dark color (maximum of 50% brightness).
    max_value = 128  # 50% of 256

    r = min(r, max_value)
    g = min(g, max_value)
    b = min(b, max_value)

    # Format back to hex with padding.
    color_hex = f"#{r:02x}{g:02x}{b:02x}"
    return color_hex


def user_set_color(board_id, data):
    """
    Sets a custom color for a user on a specific board.

    Reads the board's JSON file, updates the user's custom color if the user exists,
    and then writes the updated data back to the file.

    Args:
        board_id (str): The ID of the board.
        data (dict): A dictionary containing the username and the desired custom color.
    """

    if board_id:
        _tmps, _ = boards.get_board(board_id)

        username = data.get("username")
        if username:
            user_param = _tmps["users_list"].get(username)
            if user_param:
                # Update the user's custom color.
                _tmps["users_list"][username]["custom_color"] = data.get("custom_color")

        # Write the updated data back to the JSON file.
        boards.update_board(board_id, _tmps)


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
                        temps_modif = os.path.getmtime(file_path)
                        date_modif = datetime.datetime.fromtimestamp(
                            temps_modif)
                        date_format = "%Y-%m-%d %H:%M:%S"
                        date_format = date_modif.strftime(date_format)

                        author_files.append(
                            {
                                "board_uuid": Path(file_path).stem,
                                "board_name": data["board_name"],
                                "board_version": BOARD_VERSION,
                                "current_version": curr_version,
                                "path": file_path,
                                "last_edit": date_format,
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
        _tmps, _ = boards.get_board(board_id)

        if "version" not in _tmps:
            return False

        if _tmps["version"] != BOARD_VERSION:
            _tmps = tools.update_board(_tmps)
            boards.update_board(board_id, _tmps)

        if not username_filter:
            return _tmps

        for col_name in _tmps["data"]:
            for card_uuid, card_data in _tmps["data"][col_name].items():
                card_visibility = False
                user_param = _tmps["users_list"].get(card_data["author"])
                if user_param:
                    card_visibility = user_param["card_visibility"]

                if card_data["author"] != username_filter and not card_visibility:
                    _tmps["data"][
                        col_name][
                        card_uuid][
                        "content"] = "<div class='hide_content'></div>"

                _tmps["data"][
                    col_name][
                    card_uuid][
                    "username_color"] = username_color(board_id, card_data["author"])

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
    _tmps = get_board_info_by_id(board_id)
    if _tmps:
        _tmps["timer"] = int(new_timer_value.timestamp() * 1000)
        boards.update_board(board_id, _tmps)
        return True

    return False


def board_votes_reset_by_id(board_id, max_vote):
    """
    Resets the vote count for a specific board.

    Args:
        board_id (int): The ID of the board to reset.
        max_vote (int): Board max Votes.

    Returns:
        bool: True if the reset was successful, False otherwise.
    """
    _tmps = get_board_info_by_id(board_id)
    if not _tmps:
        return False

    if not max_vote:
        _tmps["votes"] = False
    else:
        _tmps["votes"] = int(max_vote)

    _tmps["votes_list"] = {}
    for key, value in _tmps["data"].items():
        if isinstance(value, dict):
            tools.reset_votes_in_nested_dict(value)
        elif key == "votes":
            _tmps["data"][key] = 0

    boards.update_board(board_id, _tmps)
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
    _tmps = get_board_info_by_id(board_id)
    if not _tmps:
        return False

    if not max_vote:
        _tmps["users_list"] = {}
    else:
        for user in _tmps["users_list"].keys():
            _tmps["votes_list"][user] = int(max_vote)

    boards.update_board(board_id, _tmps)
    return True


def board_manager_response(ws_lst, data, board_info, card_data):
    """
    Constructs and returns a message to be sent to clients regarding board updates.

    Args:
        ws_lst: A list containing the websocket and a secondary websocket (likely for comparison).
        data: A dictionary containing the original data received from the client.
        board_info: A dictionary containing information about the board, including user details.
        card_data: A tuple containing the mode of the update, board ID, card UUID, and card votes.

    Returns:
        A list containing the websocket to send the message to and the message itself.
        The message is a dictionary with the update type, board ID, card UUID, card votes,
        and the updated card data.
    """
    websocket, ws = ws_lst
    mode, board_id, card_uuid, card_votes = card_data
    message_data = data.copy()
    if mode in ("card_add", "card_edit"):
        message_data["cardContent"] = data["cardContent"]
        if (
            websocket != ws
            and not board_info["users_list"].get(message_data["author"])["card_visibility"]
        ):
            message_data["cardContent"] = "<div class='hide_content'></div>"
        message_data["username_color"] = username_color(board_id, message_data["author"])

    return [
        ws,
        {
            "type": mode,
            "board_id": board_id,
            "card_uuid": card_uuid,
            "card_votes": card_votes,
            mode: message_data,
        },
    ]


def children_manager_by_id(board_info, mode, card_uuid, data):
    """
    Manages children cards within a board's data structure.

    Args:
        board_info (dict): A dictionary containing the board's data.
        mode (str): The mode of operation ("card_parent" or other).
        card_uuid (str): A UUID (used only if mode is not "card_parent").
        data (dict): A dictionary containing data relevant to the operation.

    Returns:
        dict: The modified board_info dictionary.
    """
    if mode == "card_parent":
        parent_id = data.get("card_uuid")
        child_id = data.get("cardContent")

        parent_card, parent_col = tools.find_content_by_id(
            board_info["data"], parent_id)
        child_card, child_col = tools.find_content_by_id(
            board_info["data"], child_id)

        if parent_card and child_card:
            del child_card["pos"]
            del child_card["votes"]

            board_info["data"][parent_col][parent_id]["children"].append(
                child_card)

            if len(child_card["children"]) > 0:
                board_info["data"][parent_col][parent_id]["children"].extend(
                    child_card["children"])

            del child_card["children"]
            del board_info["data"][child_col][child_id]

        return board_info

    card_uuid = uuid.uuid4().hex
    col_id = data.get("col_id")
    parent_id = data.get("card_uuid")
    child_id = data.get("cardContent")

    if parent_id not in board_info["data"][col_id]:
        return board_info

    if int(child_id) >= len(board_info["data"][col_id][parent_id]["children"]):
        return board_info

    board_info["data"][col_id][card_uuid] = board_info["data"][
        col_id][parent_id]["children"][int(child_id)].copy()
    board_info["data"][col_id][card_uuid]["pos"] = len(
        board_info["data"][col_id].keys()) + 1
    board_info["data"][col_id][card_uuid]["votes"] = 0
    board_info["data"][col_id][card_uuid]["children"] = []

    del board_info["data"][col_id][parent_id]["children"][int(child_id)]
    return board_info


def board_manager_by_id(send_list, board_id, mode, websocket, data):
    """
    Manages board operations based on the specified mode.

    Args:
        send_list (list): A list to which messages to be sent are appended. Each item
                         in the list should be a list containing the websocket and
                         the message payload (dictionary).
        board_id (int or str): The ID of the board to operate on (if applicable).
        mode (str): The operation mode.
        websocket: The websocket connection object.
        data (dict):  A dictionary containing request data, potentially including
                      the "username" key.

    Returns:
        list: The updated send_list.
    """
    if mode == "board_info":
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

    elif mode == "board_list":
        send_list.append(
            [
                websocket,
                {
                    "type": "board_list",
                    "board_list": get_board_list_by_author(data.get("username")),
                },
            ]
        )

    elif mode in ("board_template", "board_delete", "board_rename"):
        board_info = get_board_info_by_id(data.get("board_uuid"))
        board_info_author = board_info.get("author")
        if board_info_author == data.get("username"):
            if mode == "board_template":
                new_board_uuid = uuid.uuid4().hex
                new_board_path = f"./board/{new_board_uuid}.json"

                board_info["board_name"] = data.get("new_name")
                for category in board_info["data"]:
                    board_info["data"][category] = {}
                with open(new_board_path, "w", encoding="utf-8") as f:
                    json.dump(board_info, f, indent=4)

                send_list.append(
                    [
                        websocket,
                        {
                            "type": "board_list",
                            "board_list": get_board_list_by_author(data.get("username")),
                        },
                    ]
                )

            else:
                board_uuid = data.get("board_uuid")
                board_path = f"./board/{board_uuid}.json"
                if os.path.isfile(board_path):

                    if mode == "board_delete":
                        os.remove(board_path)
                    else:
                        board_info["board_name"] = data.get("board_name")
                        boards.update_board(board_id, board_info)

                    send_list.append(
                        [
                            websocket,
                            {
                                "type": "board_list",
                                "board_list": get_board_list_by_author(data.get("username")),
                            },
                        ]
                    )

    return send_list


def card_manager_by_id(send_list, board_id, mode, websocket, data):
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

    elif mode in ["card_parent", "card_unmerge"]:
        board_info = children_manager_by_id(board_info, mode, card_uuid, data)

    elif mode == "card_view":
        if data.get("author") in board_info["users_list"].keys():
            if board_info["users_list"][data.get("author")]["card_visibility"]:
                data["visibility"] = False
            else:
                data["visibility"] = True

            board_info["users_list"][data.get("author")]["card_visibility"] = data["visibility"]

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

    boards.update_board(board_id, board_info)
    for ws in clients:
        send_list.append(
            board_manager_response(
                (websocket, ws),
                data, board_info,
                (mode, board_id, card_uuid, card_votes))
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

    boards.update_board(board_id, board_info)
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
    if username not in board_users_list.keys():
        board_info["users_list"][username] = {
            "custom_color": False,
            "card_visibility": False,
        }

    boards.update_board(board_id, board_info)
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
    if message_type == "connect":
        boards.add_client(board_id)
        message_username = data.get("username")
        color_username = username_color(board_id, message_username)
        users[client_id] = {
            "username": message_username,
            "color": color_username,
            "board_id": board_id,
        }

        send_list.append(
            [
                websocket,
                {
                    "type": "connect_status",
                    "user_id": client_id,
                    "user_color": color_username,
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
                "color": username_color(board_id, message_username),
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

    elif message_type in (
        "board_list",
        "board_info",
        "board_rename",
        "board_template",
        "board_delete",
    ):
        send_list = board_manager_by_id(
            send_list, board_id, message_type, websocket, data
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
        "card_unmerge",
        "card_view",
        "card_vote",
        "card_delete",
    ):
        send_list = card_manager_by_id(
            send_list, board_id, message_type, websocket, data
        )

    elif message_type in ("col_add", "col_order", "col_reorder", "col_delete"):
        col_manager_by_board_id(board_id, message_type, data)
        send_list = send_list_multi(
            send_list,
            clients,
            {"type": message_type, "board_id": board_id, message_type: data},
        )

    elif message_type == "user_color":
        user_set_color(board_id, data)
        send_list = send_list_multi(send_list, clients, data)

    elif message_type == "message":
        message_content = data.get("content")
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


def ws_stats():
    """
    Prints statistics about users, clients, and the current position.
    """

    print("-"*25)

    num_boards = len(boards.boards)
    print(f"> Boards loaded: {num_boards}")

    num_users = len(users)
    print(f"> Total users  : {num_users}")

    num_clients = len(clients)
    print(f"> Total clients: {num_clients}")

    print(f"> Next position: {POS}")


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

    clients.add(websocket)
    client_id = POS
    board_id = False
    send_list = []
    POS += 1
    ws_stats()

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
        ws_stats()

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
            boards.remove_client(board_id)
            del users[client_id]


async def main():
    """
    Starts a WebSocket server on port 8009, listening on all interfaces.

    This function initiates an asynchronous WebSocket server
    The `handler` function (not shown) is responsible for handling incoming
    The server runs indefinitely until it's manually stopped.
    """
    async with websockets.serve(handler, "0.0.0.0", 8009):
        print("Websocket Started")
        await asyncio.Future()


if __name__ == "__main__":
    licence_manager = licence.LicenceManager()
    licence_manager.validate_licence()
    asyncio.run(main())
