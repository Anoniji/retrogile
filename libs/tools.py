#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Script Name: Retrogile Tools
Author: Niji Ano
Date: 2025-12-18

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

    if board_data_old["version"] <= 3:
        board_data_old["version"] = 4

        new_users_list = {}
        for user in board_data_old["users_list"]:
            new_users_list[user] = {
                "custom_color": False,
                "card_visibility": False,
            }
        board_data_old["users_list"] = new_users_list

        for category in board_data_old["data"]:
            for _, child_data in board_data_old["data"][category].items():
                del child_data["hidden"]

    if board_data_old["version"] <= 4:
        board_data_old["version"] = 5
        for user in board_data_old["users_list"].values():
            if "custom_color" in user:
                del user["custom_color"]

    if board_data_old["version"] <= 5:
        board_data_old["version"] = 6

        if len(board_data_old["votes_list"]) > 0:
            first_key = next(iter(board_data_old["votes_list"]))
            first_value = board_data_old["votes_list"][first_key]
            if isinstance(first_value, int):
                new_votes_list = {}
                for key, value in board_data_old["votes_list"].items():
                    new_votes_list[key] = {
                        "remaining": value,
                        "votes": {}
                    }

                board_data_old["votes_list"] = new_votes_list

    if board_data_old["version"] <= 6:
        board_data_old["version"] = 7
        board_data_old["type"] = "board"

    return board_data_old


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

    result, dic_path = (False, False)
    for key, value in data.items():
        if key == id_to_find:
            return value, parent
        if isinstance(value, dict):
            result, dic_path = find_content_by_id(value, id_to_find, key)
        if result:
            return result, dic_path if parent else dic_path

    return None, []


def remove_symbols(text):
    """
    Removes specific symbols from a string.

    Args:
        text: The input string.

    Returns:
        The string without the specified symbols.
    """
    symbols_to_remove = "@^*_{}|\\;/"
    text_without_symbols = text.translate(
        str.maketrans('', '', symbols_to_remove))

    return text_without_symbols
