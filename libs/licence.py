#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Script Name: Retrogile Licence Manager
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

import sys
import os
import uuid
import gevent.monkey

gevent.monkey.patch_all()

import requests


class LicenceManager:
    """
    Manages the licence verification process for an application.

    This class provides functionality to:
        - Read or create a licence file containing a UUID.
        - Validate the licence by contacting a remote server.

    Attributes:
        licence_file (str, optional): The name of the licence file. Defaults to "licence.lic".
        uuid (str): The licence UUID.

    Methods:
        _get_licence_uuid(): Retrieves the licence UUID from the file, 
                             or creates it if the file doesn't exist.
        validate_licence(): Validates the licence by contacting the remote server.
    """
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
            with open(self.licence_file, "w", encoding="utf-8") as f:
                f.write(new_uuid)
            return new_uuid

        with open(self.licence_file, "r", encoding="utf-8") as f:
            return f.read().strip()

    def validate_licence(self):
        """
        Validates the licence by contacting the remote server.
        """
        url = f"https://licence.anoniji.ovh/retrogile/licence.php?uuid={self.uuid}"
        try:
            response = requests.get(url, timeout=3)
            response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
            if response.text.strip() == "True":
                return  # Licence valide, on ne fait rien

            print("Error: Invalid licence.")
            sys.exit(1)
        except requests.exceptions.RequestException:
            print("Error: Unable to contact the licence server.")
            sys.exit(1)
