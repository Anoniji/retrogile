#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Retrogile Sessions Manager
"""

import json
import uuid
import os


class Sessions:
    """
    A class for managing user sessions using a JSON file.
    """

    def __init__(self):
        """
        Initializes the Sessions object.
        """
        self.filename = "board/sessions.db"
        if not os.path.exists(self.filename):
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump([], f)

    def create(self):
        """
        Generates a unique session ID (UUID) and adds it to the session file.

        Returns:
            str: The generated session ID.
        """
        session_id = str(uuid.uuid4())
        try:
            with open(self.filename, "r+", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
                data.append(session_id)
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)

        except FileNotFoundError:
            # Gère le cas où le fichier n'existe pas encore
            with open(self.filename, 'w') as f:
                json.dump([session_id], f, indent=4)
        return session_id

    def check(self, session_id):
        """
        Checks if a session ID exists in the session file. If found, removes it and returns True.

        Args:
            session_id (str): The session ID to check.

        Returns:
            bool: True if the session ID was found and removed, False otherwise.
        """
        with open(self.filename, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return False

            if session_id in data:
                data.remove(session_id)
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                return True

            return False
