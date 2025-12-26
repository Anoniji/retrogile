#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Script Name: Retrogile Sessions Manager
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
import time
import json
import uuid


class Sessions:
    """
    A class for managing user sessions using a JSON file.
    """

    def __init__(self):
        """
        Initializes the Sessions object.
        """
        self.duration = 1 * 3600  # Convert to seconds
        self.filename = "board/sessions.db"
        self.sess_dta = {}

        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.sess_dta = json.load(f)
            except json.JSONDecodeError:
                # File exists but is corrupted, reinitialize
                with open(self.filename, "w", encoding="utf-8") as f:
                    json.dump({}, f)
        else:
            # File doesn't exist, create it with empty dict
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump({}, f)


    def create(self):
        """
        Generates a unique session ID (UUID) and adds it to the session file.

        Returns:
            str: The generated session ID.
        """
        session_id = str(uuid.uuid4())
        duration = self.duration * 3600
        expiration_timestamp = time.time() + duration

        with open(self.filename, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

            if not isinstance(data, dict):
                data = {}

            data[session_id] = {
                "created": time.time(),
                "expires": expiration_timestamp,
                "data": False
            }
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
            self.sess_dta = data

        return session_id

    def set(self, session_id, session_data):
        """
        Sets or updates session data for a given session ID in the session file.

        Args:
            session_id (str): The unique identifier for the session.
            session_data (dict): The data to be associated with the session.

        Returns:
            bool: True if the session data was successfully set or updated, False otherwise.
                  Returns False if the session file is corrupted or the session ID is not found.
        """
        with open(self.filename, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return False

            if session_id in data:
                data[session_id]["data"] = session_data
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                self.sess_dta = data
                return True

        return False

    def get(self, session_id):
        """
        Retrieves session data associated with a given session ID.

        Args:
            session_id (str): The ID of the session to retrieve.

        Returns:
            dict or False: The session data if the session ID exists, False otherwise.
        """
        if session_id in self.sess_dta:
            return self.sess_dta[session_id]["data"]

        return False

    def remove(self, session_id):
        """
        Removes a session from the stored session data.

        This method attempts to remove a session identified by `session_id` from the
        JSON data stored in the file specified by `self.filename`.

        Args:
            session_id (str): The ID of the session to remove.

        Returns:
            bool: True if the session was successfully removed, False otherwise.
                  Returns False if the session ID is not found or if the JSON file
                  cannot be decoded.
        """
        with open(self.filename, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return False

            if session_id in data:
                del data[session_id]
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                self.sess_dta = data
                return True

        return False

    def check(self, session_id):
        """
        Checks if a session ID exists in the session file. If found, returns True.

        Args:
            session_id (str): The session ID to check.

        Returns:
            bool: True if the session ID was found, False otherwise.
        """
        with open(self.filename, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
                self.sess_dta = data
            except json.JSONDecodeError:
                return False

            if session_id in data and not data[session_id]["data"]:
                expires = data[session_id]["expires"]
                current_time = time.time()
                if expires > current_time:
                    return True

                del data[session_id]
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                self.sess_dta = data
                return False

        return False
