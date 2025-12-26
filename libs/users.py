#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Script Name: Retrogile Users Manager
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

import json
import os
import hashlib
import uuid


class Users:
    """
    Manages user data, including loading, saving, creating, and retrieving user information.
    User data is stored in a JSON file.
    """

    def __init__(self):
        """
        Initializes the Users class.
        Loads user data from the specified file or creates an empty user dictionary.
        """
        self.filename = "board/users.db"
        self.users = self._load_users()

    def _username_color(self, username):
        """
        Generates a unique hexadecimal color code for a username.

        If no custom color is found, it generates a dark color based on
        the username using a SHA256 hash.

        Args:
            username (str): The username.

        Returns:
            str: The hexadecimal color code in the format "#RRGGBB".
        """

        # Generate a dark color based on the username.
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

    def _load_users(self):
        """
        Loads user data from the JSON file.

        Returns:
            dict: A dictionary containing user data, or an empty dictionary
                  if the file does not exist or is invalid.
        """
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _save_users(self):
        """
        Saves user data to the JSON file.
        """
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.users, f, indent=4)

    def get_user(self, username):
        """
        Retrieves user data for a given username. Creates the user if they do not exist.

        Args:
            username (str): The username.

        Returns:
            dict: A dictionary containing user data.
        """
        if username in self.users:
            return self.users[username]

        return self._create_user(username)

    def _create_user(self, username):
        """
        Creates a new user with a unique ID and color.

        Args:
            username (str): The username.

        Returns:
            dict: A dictionary containing the newly created user's data.
        """
        user_id = str(uuid.uuid4())
        new_user = {
            "id": user_id,
            "username": username,
            "color": self._username_color(username)
        }
        self.users[username] = new_user
        self._save_users()
        return new_user

    def get_user_display_name(self, username):
        """
        Retrieves the display name for a given username.

        Args:
            username (str): The username.

        Returns:
            str: The display name of the user, or the username if not found.
        """
        user = self.get_user(username)
        return user.get("username", username)

    def get_user_color(self, username):
        """
        Retrieves the color for a given username.

        Args:
            username (str): The username.

        Returns:
            str: The color of the user, or a generated color if not found.
        """
        user = self.get_user(username)
        return user.get("color", self._username_color(username))

    def set_user_color(self, username, color):
        """
        Sets the color for a given username.

        Args:
            username (str): The username.
            color (str): The hexadecimal color code.
        """
        user = self.get_user(username)
        user["color"] = color
        self._save_users()
