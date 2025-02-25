#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Retrogile Sessions Manager
"""

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
        self.filename = "board/sessions.db"
        self.sess_dta = {}
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump({}, f)

    def create(self):
        """
        Generates a unique session ID (UUID) and adds it to the session file.

        Returns:
            str: The generated session ID.
        """
        session_id = str(uuid.uuid4())
        with open(self.filename, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

            if not isinstance(data, dict):
                data = {}

            data[session_id] = False
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
                data[session_id] = session_data
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
            return self.sess_dta[session_id]

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

            if session_id in data and not data[session_id]:
                return True

        return False
