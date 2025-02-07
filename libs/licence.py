#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Retrogile Licence Manager
"""

import gevent.monkey

gevent.monkey.patch_all() 

import uuid
import requests
import sys
import os

class LicenceManager:
    def __init__(self, licence_file="licence.lic"):
        """
        Initializes the LicenceManager object.

        Args:
            licence_file (str, optional): The name of the licence file. Defaults to "licence.lic".
        """
        self.licence_file = os.path.join('board', licence_file)
        self.uuid = self._get_licence_uuid()

    def _get_licence_uuid(self):
        """
        Retrieves the licence UUID from the file, or creates it if the file doesn't exist.

        Returns:
            str: The licence UUID.
        """
        if not os.path.exists(self.licence_file):
            new_uuid = uuid.uuid4().hex + uuid.uuid4().hex
            with open(self.licence_file, "w") as f:
                f.write(new_uuid)
            return new_uuid
        else:
            with open(self.licence_file, "r") as f:
                return f.read().strip()

    def validate_licence(self):
        """
        Validates the licence by contacting the remote server.
        """
        url = f"https://anoniji.dev/retrogile/licence.php?uuid={self.uuid}"
        try:
            response = requests.get(url, timeout=3)
            response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
            if response.text.strip() == "True":
                return  # Licence valide, on ne fait rien

            print("Error: Invalid licence.")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print("Error: Unable to contact the licence server.")
            sys.exit(1)

