#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Script Name: Retrogile license Manager
Author: Niji Ano
Date: 2026-06-07

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
import json
from datetime import datetime, timezone
import gevent.monkey

gevent.monkey.patch_all()

import requests
import jwt


class LicenseManager:
    """
    Manages the license verification process for an application.

    This class provides functionality to:
        - Read or create a license file containing a JWT.
        - Validate the license by contacting a remote server.

    Attributes:
        license_file (str, optional): The name of the license file. Defaults to "license.jwt".
        account_email (str): The email for license JWT.

    Methods:
        _get_license_jwt(): Retrieves the license JWT from the file,
                             or creates it if the file doesn't exist.
        validate_license(): Validates the license by contacting the remote server.
    """
    def __init__(self, account_email, license_file="license.jwt"):
        """
        Initializes the licenseManager object.

        Args:
            license_file (str, optional): The name of the license file. Defaults to "license.jwt".
        """
        self.account_email = account_email
        self.license_file = os.path.join('board', license_file)

        if not self.account_email and not os.path.isfile(self.license_file):
            print('account_email: not set and no license, please set ACCOUNT_EMAIL parameter')
            sys.exit(-1)

        self.jwt_license = self._get_license_jwt()

    def _get_license_jwt(self):
        """
        Retrieves the license JWT from the file, or creates it if the file doesn't exist.

        Returns:
            str: The license JWT.
        """
        if os.path.exists(self.license_file):
            with open(self.license_file, "r", encoding="utf-8") as f:
                return json.loads(f.read().strip())

        return False

    def validate_license(self, type_lst = None):
        """
        Validates the license by contacting the remote server.
        """
        if type_lst is None:
            type_lst = []

        url = "https://license.retrogile.com/jwt?mail="
        if not self.jwt_license:
            url += self.account_email
        else:
            url += self.jwt_license.get('email')

        try:
            response = requests.get(url, timeout=3)
            response.raise_for_status()
            jwt_data = response.json()

            if not jwt_data.get('success', False):
                print("License_error: Server Offline or Invalid license")
                sys.exit(-1)

            if not self.jwt_license:
                if not jwt_data.get('encryption_key', False):
                    print("License_error: The license file no longer exists locally")
                    sys.exit(-1)

                del jwt_data['success']
                with open(self.license_file, "w", encoding="utf-8") as f:
                    f.write(json.dumps(jwt_data))

                self.jwt_license = self._get_license_jwt()
                if not self.jwt_license:
                    print("License_error: Unable to write the license file")
                    sys.exit(-1)

            encryption_key = self.jwt_license.get('encryption_key')
            jwt_key = jwt_data.get('jwt')
            jwt_decoded = jwt.decode(jwt_key, encryption_key, algorithms=["HS256"])

            if (
                not jwt_decoded.get('type', False) == 'license' or
                not jwt_decoded.get('version', False) == '2' or
                not isinstance(jwt_decoded.get('permits', False), list)
            ):
                print("Error: Schema verification failed")
                sys.exit(1)

            gen_datetime = datetime.fromisoformat(
                jwt_data.get('last_accessed_at').replace('Z', '+00:00'))
            now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
            gen_datetime_naive = gen_datetime.replace(tzinfo=None)
            diff = abs((now_utc - gen_datetime_naive).total_seconds())
            tolerance = 20
            is_within_tolerance = diff <= tolerance

            if not is_within_tolerance:
                print("Error: The license was not loaded quickly enough")
                sys.exit(1)

            for type_check in type_lst:
                if type_check not in jwt_decoded.get('permits'):
                    print("Error: License does not authorize the launch of this service")
                    sys.exit(1)

            print(' * The license authorizes the launch of this service')

        except jwt.exceptions.InvalidSignatureError:
            print("Error: Signature verification failed")
            sys.exit(1)

        except requests.exceptions.RequestException:
            print("Error: Unable to contact the license server")
            sys.exit(1)
