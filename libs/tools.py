#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Retrogile Tools
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
