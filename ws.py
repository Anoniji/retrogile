#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Script Name: Retrogile WS
Author: Niji Ano
Date: 2026-01-06

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
"""

import os
import argparse
import json
import uuid
import asyncio
import time
import datetime
from pathlib import Path
from collections import OrderedDict
from urllib.parse import urlparse, parse_qs
import logging
import websockets

from libs import lic, tools, sessions, boards, users


logging.basicConfig(
    filename="retrogile_ws.log", level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# ///////////////////////////////////////////////////////////////////////

boards, usersdb, sesssdb = [boards.Board(), users.Users(), sessions.Sessions()]
BOARD_VERSION, clients = (8, {})

# ///////////////////////////////////////////////////////////////////////


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
    directory, author_files = ("./board/", [])
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

                        if data.get("type", "board") == "speed":
                            file_path = file_path.replace("board", "speed")

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

        if not _tmps or "version" not in _tmps:
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
                    "username_color"] = usersdb.get_user_color(card_data["author"])

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


def board_votes_reset_by_id(board_id, data):
    """
    Resets the vote count and vote list for a specific board.

    Args:
        board_id (int): The ID of the board to reset.
        data (dict): A dictionary containing board data, including 'maxVote'.

    Returns:
        dict: The updated 'data' dictionary if the reset was successful,
              False otherwise.

    """
    max_vote = data.get("maxVote")
    _tmps = get_board_info_by_id(board_id)
    if not _tmps:
        return False

    if max_vote == "0":
        _tmps["votes"] = False
    elif int(max_vote) > 20:
        max_vote = 20
        _tmps["votes"] = max_vote
        data["maxVote"] = max_vote
    else:
        _tmps["votes"] = int(max_vote)

    _tmps["votes_list"] = {}
    for key, value in _tmps["data"].items():
        if isinstance(value, dict):
            tools.reset_votes_in_nested_dict(value)
        elif key == "votes":
            _tmps["data"][key] = 0

    boards.update_board(board_id, _tmps)
    return data


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
            _tmps["votes_list"][user] = {
                "remaining": int(max_vote),
                "votes": {}
            }

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
        message_data["cardContent"] = tools.remove_symbols(data["cardContent"])
        if (
            websocket != ws
            and not board_info["users_list"].get(message_data["username"])["card_visibility"]
        ):
            message_data["cardContent"] = "<div class='hide_content'></div>"
        message_data["username_color"] = usersdb.get_user_color(message_data["username"])

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
    parent_id, child_id = (data.get("card_uuid"), data.get("cardContent"))

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

    elif mode in ("board_template", "board_delete", "board_rename", "board_type"):
        board_info = get_board_info_by_id(data.get("board_uuid"))
        board_info_author = board_info.get("author")
        if board_info_author == data.get("username"):
            if mode == "board_template":
                new_board_uuid = uuid.uuid4().hex
                new_board_path = f"./board/{new_board_uuid}.json"

                board_info["board_name"] = tools.remove_symbols(data.get("new_name"))
                board_info["users_list"] = {}
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
                    elif mode == "board_type":
                        board_info["type"] = "board"
                        boards.update_board(board_uuid, board_info)
                    else:
                        board_info["board_name"] = tools.remove_symbols(
                            data.get("board_name"))
                        boards.update_board(board_uuid, board_info)

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

    card_uuid, card_votes = (uuid.uuid4().hex, 0)
    if mode == "card_add":
        board_info["data"][data.get("col_id")][card_uuid] = {
            "pos": data.get("pos"),
            "author": data.get("username"),
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

    elif mode in ("card_parent", "card_unmerge"):
        board_info = children_manager_by_id(board_info, mode, card_uuid, data)

    elif mode == "card_view":
        if data.get("username") in board_info["users_list"].keys():
            data["visibility"] = True
            if (
                board_info["users_list"][data.get("username")]["card_visibility"]
                and board_info["type"] != "speed"
            ):
                data["visibility"] = False

            board_info["users_list"][data.get("username")]["card_visibility"] = data["visibility"]

    elif mode == "card_vote":
        if (
            data.get("username")
            and data.get("col_id") in board_info["data"]
            and data.get("card_uuid") in board_info["data"][data.get("col_id")]
        ):

            cur_user, cur_uuid = (data.get("username"), data.get("card_uuid"))
            cur_unvote, udv = (data.get("unvote"), 1)
            if cur_unvote:
                udv = -1

            if not board_info["votes_list"][cur_user]:
                return False

            if "remaining" not in board_info["votes_list"][cur_user]:
                return False

            if cur_unvote and (
                cur_uuid not in board_info["votes_list"][cur_user]["votes"]
                or board_info["votes_list"][cur_user]["votes"][cur_uuid] == 0
            ):
                return False

            if cur_user not in board_info["votes_list"]:
                board_info["votes_list"][cur_user]["remaining"] = board_info["votes"] - udv
            else:
                board_info["votes_list"][cur_user]["remaining"] -= udv

            if cur_uuid not in board_info["votes_list"][cur_user]["votes"]:
                board_info["votes_list"][cur_user]["votes"][cur_uuid] = 0

            board_info["votes_list"][cur_user]["votes"][cur_uuid] += udv
            board_info["data"][data.get("col_id")][cur_uuid]["votes"] += udv
            card_votes = board_info["data"][data.get("col_id")][cur_uuid][
                "votes"
            ]

    elif mode == "card_delete":
        if (
            data.get("col_id") in board_info["data"]
            and data.get("card_uuid") in board_info["data"][data.get("col_id")]
        ):
            del board_info["data"][data.get("col_id")][data.get("card_uuid")]

    elif mode == "user_mood" and data.get("username"):
        board_info["users_list"][data.get("username")]["mood"] = data.get("mood", False)

    elif mode == "get_mood" and data.get("username"):
        data["user_selected_color"] = usersdb.get_user_color(data.get('username'))
        data["user_selected_mood"] = board_info["users_list"][data.get("username")]["mood"]

    boards.update_board(board_id, board_info)
    for tk, ws in clients.items():
        if (
            sesssdb.get(tk) and
            board_id == sesssdb.get(tk)['board_id']
        ):
            send_list.append(
                board_manager_response(
                    (websocket, ws),
                    data, board_info,
                    (mode, board_id, card_uuid, card_votes))
            )

    return send_list


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
    for tk, client in clients_lst.items():
        if (
            sesssdb.get(tk) and
            msg_data['board_id'] == sesssdb.get(tk)['board_id']
        ):
            send_list.append([client, msg_data])

    return send_list


def votes_manager_by_id(send_list, board_id, mode, websocket, data):
    """
    Manages votes for a specific board.

    Args:
        send_list (list): List of messages to be sent.
        board_id (int/str): ID of the board.
        mode (str): Vote management mode ("start_vote" or other).
        websocket: Websocket object for communication.
        data (dict): Additional data (may contain "maxVote").

    Returns:
        list: The updated send_list. Returns False if the board doesn't exist.
    """
    if mode == "start_vote":
        data = board_votes_reset_by_id(board_id, data)
        board_votes_init(board_id, data.get("maxVote"))
        send_list = send_list_multi(send_list, clients, data)

    elif mode == "stats_vote":
        board_info = get_board_info_by_id(board_id)
        if not board_info:
            return send_list

        votes_remaining = board_info["votes_list"][data.get("username")]["remaining"]
        votes_total = sum(entry["remaining"] for entry in board_info["votes_list"].values())
        votes_percentage = 0
        if votes_total != 0:
            votes_total_remaining = len(board_info["votes_list"].keys()) * board_info["votes"]
            votes_percentage = int((votes_total * 100) / votes_total_remaining)

        send_list.append(
            [
                websocket,
                {
                    "type": "stats_vote",
                    "board_id": board_id,
                    "votes": board_info["votes"],
                    "votes_remaining": votes_remaining,
                    "votes_total": votes_total,
                    "votes_percentage": votes_percentage,
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

    if mode == "col_order":
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

    elif board_info['author'] != data.get('username', False):
        return False

    if mode == "col_add":
        if data.get("colName") in board_info["data"]:
            return False

        board_info["data"][tools.remove_symbols(data.get("colName"))] = {}

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
            "card_visibility": False,
        }

    boards.update_board(board_id, board_info)
    return True


def set_confetti_color(data):
    """
    Retrieves the user's confetti color from the database
    and adds it to the data.

    Args:
        data (dict): A dictionary containing user information,
                     including a 'username' key.

    Returns:
        dict: The modified 'data' dictionary with the 'color' key added
              and the 'username' key removed.

    """
    confetti_color = usersdb.get_user_color(data.get('username'))
    data['color'] = confetti_color
    del data['username']

    return data


def message_responce(send_list, websocket, token, data):
    """
    Processes a received message and builds a list of messages to send.

    This function takes a message received from a websocket client,
    analyzes its type, and creates appropriate responses.
    The responses are added to a `send_list` which is a list of tuples
    containing the target websocket and the message data to be sent.

    Args:
        send_list: A list to store tuples of target websockets and message.
        websocket: The websocket that sent the original message.
        token: The ID of the websocket session.
        data: The data payload of the received message.

    Returns:
        The updated `send_list` containing messages to be sent to clients.
    """
    users_list, message_type = ({}, data.get("type"))
    if message_type == "connect":
        board_id = data.get("board_id", False)
        message_username = data.get("username")

        if board_id:
            sesssdb.set(token, {
                "board_id": board_id,
                "username": message_username,
            })

        boards.add_client(board_id)
        color_username = usersdb.get_user_color(message_username)
        send_list.append(
            [
                websocket,
                {
                    "type": "connect_status",
                    "user_id": token,
                    "user_color": color_username,
                    "error": False,
                    "board_id": board_id,
                },
            ]
        )

        for sess_tk, sess_data in sesssdb.sess_dta.items():
            if (
                sess_data
                and "data" in sess_data
                and isinstance(sess_data["data"], dict)
                and "board_id" in sess_data["data"]
                and sess_data["data"]["board_id"] == board_id
            ):
                users_list[sess_tk] = {
                    "username": sess_data["data"]["username"],
                    "color": usersdb.get_user_color(sess_data["data"]["username"]),
                }

        send_list.append(
            [
                websocket,
                {"type": "users_list", "users_list": users_list, "board_id": board_id},
            ]
        )

        send_list = send_list_multi(
            send_list,
            clients,
            {
                "type": "user_add",
                "user_id": token,
                "username": message_username,
                "board_id": board_id,
                "color": usersdb.get_user_color(message_username),
            },
        )

        add_user_to_board(board_id, message_username)
        return send_list

    sesss_data = sesssdb.get(token)
    board_id = False
    if sesss_data and "board_id" in sesss_data:
        board_id = sesss_data["board_id"]
        data["board_id"] = board_id
        data["username"] = sesss_data["username"]

    if message_type == "cursor_user":
        send_list = send_list_multi(
            send_list,
            clients,
            {
                "type": "cursor_user",
                "user_id": token,
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
        "board_type",
    ):
        send_list = board_manager_by_id(
            send_list, board_id, message_type, websocket, data
        )

    elif message_type == "start_timer":
        timer_in_minutes = int(data.get("timerInMinutes"))
        if timer_in_minutes < 1 or timer_in_minutes > 20:
            return send_list

        timer_in_seconds = timer_in_minutes * 60
        delta = datetime.timedelta(seconds=timer_in_seconds)
        future_time_utc = datetime.datetime.now() + delta
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

    elif message_type in (
        "start_vote",
        "stats_vote",
    ):
        send_list = votes_manager_by_id(
            send_list, board_id, message_type, websocket, data
        )

    elif message_type == "start_confetti":
        send_list = send_list_multi(send_list, clients, set_confetti_color(data))

    elif message_type in (
        "card_add",
        "card_edit",
        "card_parent",
        "card_unmerge",
        "card_view",
        "card_vote",
        "card_delete",
        "card_write_start",
        "card_write_stop",
        "user_mood",
        "get_mood",
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
        usersdb.set_user_color(data.get("username"), data.get("custom_color"))
        send_list = send_list_multi(send_list, clients, data)

    elif message_type == "message":
        message_content = data.get("content")
        send_list = send_list_multi(
            send_list,
            clients,
            {
                "type": "message",
                "user_id": token,
                "username": sesss_data["username"],
                "content": message_content,
                "board_id": board_id,
            },
        )

    return send_list


def ws_stats():
    """
    Prints statistics about users, clients, and the current position.
    """

    num_boards, num_clients = (len(boards.boards), len(clients.keys()))
    logging.info("\n".join(
        ["--- WS STATS ---", f"> Boards loaded: {num_boards}", f"> Total clients: {num_clients}"]))


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
    global clients

    try:
        parsed_url = urlparse(websocket.request.path)
        query_params = parse_qs(parsed_url.query)
        token = query_params.get("token", False)
        if token:
            token = token[0]

    except AttributeError:
        return False

    if not token or not sesssdb.check(token):
        return False

    clients[token], board_id, send_list = (websocket, False, [])
    ws_stats()

    try:
        while True:
            data = json.loads(await websocket.recv())
            send_list = message_responce(
                send_list, websocket, token, data
            )

            if send_list and len(send_list) > 0:
                for ws_client, message in send_list:
                    await ws_client.send(json.dumps(message))

            send_list = []

    except websockets.exceptions.ConnectionClosedOK:
        logging.info(f"> ConnectionClosed[OK] {token}")
        sesssdb.set(token, False)

    except websockets.exceptions.ConnectionClosedError:
        logging.info(f"> ConnectionClosed[Er] {token}")
        sesssdb.remove(token)

    finally:
        del clients[token]

        for tk, sess in sesssdb.sess_dta.items():
            if (
                sesssdb.get(tk) and
                sess["board_id"] == sesssdb.get(tk)["board_id"] and
                tk in clients
            ):
                try:
                    await clients[tk].send(
                        json.dumps(
                            {
                                "type": "user_remove",
                                "user_id": token,
                                "username": sess["username"],
                                "board_id": board_id,
                            }
                        )
                    )
                except websockets.exceptions.ConnectionClosedError:
                    logging.info(f"> ConnectionClosed[Ex] {token}")

        boards.remove_client(board_id)


async def main():
    """
    Starts a WebSocket server on port 8009, listening on all interfaces.

    This function initiates an asynchronous WebSocket server
    The `handler` function (not shown) is responsible for handling incoming
    The server runs indefinitely until it's manually stopped.
    """
    async with websockets.serve(handler, "0.0.0.0", 8009):
        logging.info("Server WS started")
        await asyncio.Future()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--account_email', default=False)
    args = parser.parse_args()
    ACCOUNT_EMAIL = args.account_email

    time.sleep(3)
    license_manager = lic.LicenseManager(ACCOUNT_EMAIL)
    license_manager.validate_license(['ws'])
    asyncio.run(main())
