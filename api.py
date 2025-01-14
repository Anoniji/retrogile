#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Retrogile API
"""

import os
import json
import uuid
import datetime
import logging

from flask import Flask, render_template, send_from_directory
from flask_jsonpify import jsonify

from gevent import monkey

monkey.patch_all()

logging.basicConfig(filename="retrogile.log", level=logging.DEBUG)


# ///////////////////////////////////////////////////////////////////////

app = Flask(__name__, template_folder="./pages/")
current_year = datetime.datetime.now().year
CURRENT_VERSION = "1.0dev"

if os.path.isfile("version"):
    with open("version", "r", encoding="utf-8") as file_version:
        CURRENT_VERSION = file_version.read().strip()


@app.route("/")
def index():
    """
    Renders the index page if it exists: Renders the template.

    Returns:
        - If "index.html" exists: Renders the template.
        - Otherwise: Returns a JSON response
    """
    if os.path.isfile("./pages/index.html"):
        return render_template(
            "index.html", current_year=current_year,
            current_version=CURRENT_VERSION
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
        return render_template(
            "licenses.html", current_year=current_year,
            current_version=CURRENT_VERSION
        )

    return jsonify(["licenses_not_found"])


@app.route("/create_board/<string:board_name>/<string:author>")
def create_board(board_name, author):
    """
    Creates a new board with the specified name and author.

    Args:
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
    with open(f"{board_dir}{board_filename}", "w", encoding="utf-8") as file:
        json.dump(
            {
                "version": 3,
                "board_name": board_name,
                "author": author,
                "timer": False,
                "votes": False,
                "votes_list": {},
                "data": {"start": {}, "stop": {}, "continue": {}},
                "tmps": {},
                "users_list": [],
            },
            file,
            indent=4,
        )

    return jsonify(["./board/" + board_id])


@app.route("/board/")
def home():
    """
    Renders the home page if it exists: Renders the template.

    Returns:
        - If 'home.html' exists: Renders the 'home.html' template.
        - Otherwise: Returns a JSON response
    """
    if os.path.isfile("./pages/home.html"):
        return render_template(
            "home.html", current_year=current_year,
            current_version=CURRENT_VERSION
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
        return render_template(
            "board.html", current_year=current_year,
            current_version=CURRENT_VERSION, board_id=board_id
        )

    return jsonify(["board_not_found"])


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
        return send_from_directory("js", path, mimetype="application/javascript")

    return jsonify(["js_not_found"])


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
        return send_from_directory("img/", path, mimetype="image/png")

    return jsonify(["png_not_found"])


# ///////////////////////////////////////////////////////////////////////


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8008, debug=True)

    except OSError as e:
        logging.error(f"Server error: {e}")
