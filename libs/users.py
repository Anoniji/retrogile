import json
import os
import hashlib
import uuid


class Users:
    def __init__(self):
        self.filename = "board/users.db"
        self.users = self._load_users()

    def _username_color(self, username):
        """
        Generates a unique hexadecimal color code for a username.

        First, it checks if a custom color is defined for the user in the specified board's JSON file.
        If a custom color is found, it returns that color. Otherwise, it generates a dark color 
        based on the username using a SHA256 hash.

        Args:
            username (str): The username.

        Returns:
            str: The hexadecimal color code in the format "#RRGGBB".
        """

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

    def _load_users(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _save_users(self):
        with open(self.filename, 'w') as f:
            json.dump(self.users, f, indent=4)

    def get_user(self, username):
        if username in self.users:
            return self.users[username]

        return self._create_user(username)

    def _create_user(self, username):
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
        user = self.get_user(username)
        return user.get("username", username)

    def get_user_color(self, username):
        user = self.get_user(username)
        return user.get("color", self._username_color(username))

    def set_user_color(self, username, color):
        user = self.get_user(username)
        user['color'] = color
        self._save_users()
