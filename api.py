#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Author: Niji Ano
Date: 2025-12-18

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
import uuid
import datetime
import logging

from flask import (
    Flask, render_template, send_from_directory, request, make_response
)
from flask_jsonpify import jsonify

from gevent import monkey
from libs import licence, sessions, tools

monkey.patch_all()

logging.basicConfig(
    filename="retrogile_api.log",
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# ///////////////////////////////////////////////////////////////////////

sesssdb = sessions.Sessions()
app = Flask(__name__, template_folder="./")
current_year = datetime.datetime.now().year
CURRENT_VERSION = "1.0dev"
LIST_LANGS = ['fr', 'es',  'en']

if os.path.isfile("version"):
    with open("version", "r", encoding="utf-8") as file_version:
        CURRENT_VERSION = file_version.read().strip()

# ///////////////////////////////////////////////////////////////////////


def load_translate(lang):
    """Loads translation data from a JSON file.

    This function attempts to load a translation file for the specified lang.
    If the file is found, it parses the JSON data and returns it as a dict.
    If the specified language file is not found, it defaults to loading the
    English translation (en.json).

    Args:
        lang: The language code (e.g., "fr", "es", "en") for the translation.

    Returns:
        A dictionary containing the translation data.  Returns the English
        translation if the requested language file is not found.

    Raises:
        FileNotFoundError: If the default English translation file (en.json) is
                         also not found.  (While the current code catches
                         FileNotFoundError for the target language, it assumes
                         en.json *must* exist.  A robust version might handle
                         this case more explicitly).
        json.JSONDecodeError: If either the target language file or the English
                             default file contains invalid JSON. (This isn't
                             explicitly handled in the code but is a
                             possibility).
    """
    try:
        with open(f"./i18n/{lang}.json", "r", encoding="utf-8") as f:
            return json.load(f)

    except FileNotFoundError:
        with open("./i18n/en.json", "r", encoding="utf-8") as f:
            return json.load(f)


# ///////////////////////////////////////////////////////////////////////


def path_check(path):
    """Checks if a path is safe, disallowing relative paths and separators."""
    return ".." not in path and "/" not in path and "\\" not in path


# ///////////////////////////////////////////////////////////////////////


@app.route("/")
def index():
    """
    Renders the index page if it exists: Renders the template.

    Returns:
        - If "index.html" exists: Renders the template.
        - Otherwise: Returns a JSON response
    """
    if os.path.isfile("./pages/index.html"):
        lang = request.accept_languages.best_match(LIST_LANGS)
        return render_template(
            "./pages/index.html", current_year=current_year,
            current_version=CURRENT_VERSION,
            translates=load_translate(lang)
        )

    return jsonify(["index_not_found"])


@app.route("/LICENSES")
def licenses():
    """
    Renders the licenses page if it exists: Renders the template.

    Returns:
        - If "licenses.html" exists: Renders the template.
        - Otherwise: Returns a JSON response
    """
    if os.path.isfile("./pages/licenses.html"):
        lang = request.accept_languages.best_match(LIST_LANGS)
        return render_template(
            "./pages/licenses.html", current_year=current_year,
            current_version=CURRENT_VERSION,
            translates=load_translate(lang)
        )

    return jsonify(["licenses_not_found"])


@app.route("/create_<string:board_type>/<string:board_name>/<string:author>")
def create_board(board_type, board_name, author):
    """
    Creates a new board with the specified name and author.

    Args:
        board_type (str): Type of board
        board_name (str): The name of the board.
        author (str): The author of the board.

    Returns:
        str: A JSON string containing the path to the newly created board.

    This function creates a new directory for the board if it doesn't exist,
    generates a unique ID for the board, and creates a JSON file
    ```

    The function then returns a JSON string containing the path to the newly
    created board.
    """

    board_dir = "./board/"
    if not os.path.isdir(board_dir):
        os.mkdir(board_dir)

    board_id = str(uuid.uuid4().hex)
    board_filename = f"{board_id}.json"

    data_lst = {"start": {}, "stop": {}, "continue": {}}
    if board_type == "speed":
        data_lst = {"good": {}, "bad": {}, "start_stop": {}}

    with open(f"{board_dir}{board_filename}", "w", encoding="utf-8") as file:
        json.dump(
            {
                "version": 7,
                "type": board_type,
                "board_name": tools.remove_symbols(board_name),
                "author": tools.remove_symbols(author),
                "timer": False,
                "votes": False,
                "votes_list": {},
                "data": data_lst,
                "tmps": {},
                "users_list": {},
            },
            file,
            indent=4,
        )

    return jsonify([f"./{board_type}/{board_id}"])


@app.route("/board/")
def home():
    """
    Renders the home page if it exists: Renders the template.

    Returns:
        - If 'home.html' exists: Renders the 'home.html' template.
        - Otherwise: Returns a JSON response
    """
    if os.path.isfile("./pages/home.html"):
        lang = request.accept_languages.best_match(LIST_LANGS)
        return render_template(
            "./pages/home.html", current_year=current_year,
            current_version=CURRENT_VERSION,
            translates=load_translate(lang),
        )

    return jsonify(["board_not_found"])


@app.route("/board/<string:board_id>")
def board(board_id):
    """
    Retrieves and renders a specific board.

    Args:
        board_id (str): The unique identifier of the board.

    Returns:
        str: The rendered HTML template for the board if found,
             otherwise a JSON response indicating the board is not found.
    """
    if os.path.isfile("./pages/board.html"):
        lang = request.accept_languages.best_match(LIST_LANGS)
        return render_template(
            "./pages/board.html", current_year=current_year,
            current_version=CURRENT_VERSION,
            translates=load_translate(lang),
        )

    return jsonify([f"board_not_found_{board_id}"])


@app.route("/speed/<string:board_id>")
def speed(board_id):
    """
    Retrieves and renders a specific speed board.

    Args:
        board_id (str): The unique identifier of the board.

    Returns:
        str: The rendered HTML template for the board if found,
             otherwise a JSON response indicating the board is not found.
    """
    if os.path.isfile("./pages/speed.html"):
        lang = request.accept_languages.best_match(LIST_LANGS)
        return render_template(
            "./pages/speed.html", current_year=current_year,
            current_version=CURRENT_VERSION,
            translates=load_translate(lang),
        )

    return jsonify([f"board_not_found_{board_id}"])


@app.route("/js/<string:path>", methods=["GET"])
def js(path):
    """
    Serves a JavaScript file from the `js` directory.

    Args:
        path (str): The relative path to the JavaScript file

    Returns:
        flask.Response:
            - If the file exists, returns the JavaScript file
            - If the file doesn't exist, returns a JSON response
    """
    if os.path.isfile("js/" + path):
        return send_from_directory(
            "js", path, mimetype="application/javascript")

    return jsonify(["js_not_found"])


@app.route("/jsi/<string:path>", methods=["GET"])
def jsi(path):
    """
    Renders a JavaScript file from the `js` directory.

    Args:
        path (str): The relative path to the JavaScript file

    Returns:
        flask.Response:
            - If the file exists, returns the JavaScript file
            - If the file doesn't exist, returns a JSON response
    """
    if os.path.isfile("js/" + path) and path_check(path):
        fetch_mode = request.headers.get('Sec-Fetch-Mode', False)
        fetch_dest = request.headers.get('Sec-Fetch-Dest', False)
        board_id = False

        referer = request.headers.get('Referer', False)
        if referer:
            board_id = referer.split('/')[-1]
            if (
                ("https" in referer and (
                    fetch_mode == "no-cors" and fetch_dest == "script"
                )) or
                "https" not in referer
            ):
                lang = request.accept_languages.best_match(LIST_LANGS)
                data = render_template(
                    "js/" + path,
                    translates=load_translate(lang),
                    ws_session=sesssdb.create(),
                    board_id=board_id,
                )

                response = make_response(data)
                response.headers['Content-Type'] = 'application/javascript'

                return response

        return jsonify(["jsi_direct_access_blocked"])

    return jsonify(["jsi_not_found"])


@app.route("/css/<string:path>", methods=["GET"])
def css(path):
    """
    Serves a CSS file file from the `css` directory.

    Args:
        path (str): The relative path to the CSS file

    Returns:
        flask.Response:
            - If the file exists, returns the CSS file
            - If the file doesn't exist, returns a JSON response
    """
    if os.path.isfile("css/" + path):
        return send_from_directory("css", path, mimetype="text/css")

    return jsonify(["css_not_found"])


@app.route("/img/<string:path>", methods=["GET"])
def png(path):
    """
    Retrieves a PNG image from the specified path.

    Args:
        path (str): The relative path to the PNG image

    Returns:
        flask.Response:
            - If the image is found, returns the image content.
            - If the image is not found, returns a JSON response
    """
    if os.path.isfile("img/" + path):
        return send_from_directory("img", path, mimetype="image/png")

    return jsonify(["png_not_found"])


@app.route("/i18n/<string:path>", methods=["GET"])
def i18n(path):
    """
    Retrieves a i18n json from the specified path.

    Args:
        path (str): The relative path to the i18n json

    Returns:
        flask.Response:
            - If the i18n is found, returns the i18n content.
            - If the i18n is not found, returns a JSON response
    """
    if os.path.isfile("i18n/" + path):
        return send_from_directory("i18n", path, mimetype="application/json")

    return jsonify(["i18n_not_found"])


# ///////////////////////////////////////////////////////////////////////


if __name__ == "__main__":
    try:
        licence_manager = licence.LicenceManager()
        licence_manager.validate_licence()
        logging.info("Server API started")
        app.run(host="0.0.0.0", port=8008, debug=False)

    except OSError as e:
        logging.error(f"Server API error: {e}")
