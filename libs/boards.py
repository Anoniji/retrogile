#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Script Name: Retrogile Boards Manager
Author: Niji Ano
Date: 2025-08-05

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
import json
import copy


class Board:
    """
    Manages boards, storing board data and client connections.

    This class provides methods to load boards from a JSON file, add and remove clients,
    and update board data. It also keeps track of which boards are currently in use
    and unloads boards when no clients are connected.
    """

    def __init__(self):
        """
        Initializes the Board class.
        """
        self.boards = {}  # Dictionary to store boards and their clients

    def get_board(self, board_id):
        """
        Retrieves a board. If the board is not already loaded, it loads it from the JSON file.

        Args:
            board_id (str): The ID of the board.

        Returns:
            dict: The board data and client count, or None if the ID doesn't exist.
        """
        if board_id not in self.boards:
            try:
                json_file = f"./board/{board_id}.json"
                if os.path.isfile(json_file):
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.boards[board_id] = {
                            "data": data,
                            "clients": 0
                        }

                else:
                    return (False, False)

            except FileNotFoundError:
                print(f"Error: The JSON file '{json_file}' was not found.")
                return (False, False)

            except json.JSONDecodeError:
                print(f"Error: The JSON file '{json_file}' is malformed.")
                return (False, False)

        board_data = copy.deepcopy(self.boards)
        return (
            board_data[board_id]["data"],
            self.boards[board_id]["clients"],
        )

    def add_client(self, board_id):
        """
        Adds a client to a board. Loads the board if it's not already loaded.

        Args:
            board_id (str): The ID of the board.
        """
        board, _ = self.get_board(board_id)
        if board:
            self.boards[board_id]["clients"] += 1

    def remove_client(self, board_id):
        """
        Removes a client from a board. If the client count drops to 0, the board is unloaded.

        Args:
            board_id (str): The ID of the board.
        """
        board, _ = self.get_board(board_id)
        if board:
            self.boards[board_id]["clients"] -= 1
            if self.boards[board_id]["clients"] == 0:
                del self.boards[board_id]

    def update_board(self, board_id, new_data):
        """
        Updates the data of a board in the JSON file and in memory.

        Args:
            board_id (str): The ID of the board.
            new_data (dict): The new data for the board.
        """
        board, _ = self.get_board(board_id)

        if board:
            try:
                json_file = f"./board/{board_id}.json"
                with open(json_file, 'w', encoding="utf-8") as f:
                    json.dump(new_data, f, indent=4)

                self.boards[board_id]['data'] = new_data

            except FileNotFoundError:
                print(f"Error: The JSON file '{json_file}' was not found.")

            except json.JSONDecodeError:
                print(f"Error: The JSON file '{json_file}' is malformed.")
