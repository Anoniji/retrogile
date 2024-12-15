#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import json
import uuid
import logging

from flask import Flask, render_template, send_from_directory
from flask_jsonpify import jsonify

from gevent import monkey
monkey.patch_all()

logging.basicConfig(filename="retrogile.log", level=logging.DEBUG)


# ///////////////////////////////////////////////////////////////////////

app = Flask(__name__, template_folder="./pages/")


@app.route("/")
def index():
    if os.path.isfile("index.html"):
        return render_template("index.html")

    return jsonify(["index_not_found"])


@app.route("/LICENSES")
def licenses():
    if os.path.isfile("licenses.html"):
        return render_template("licenses.html")

    return jsonify(["licenses_not_found"])


@app.route("/create_board/<string:board_name>/<string:author>")
def create_board(board_name, author):
    board_dir = './board/'
    if not os.path.isdir(board_dir):
        os.mkdir(board_dir)

    board_id = str(uuid.uuid4().hex)
    board_filename = f'{board_id}.json'
    with open(f'{board_dir}{board_filename}', 'w') as fichier:
        json.dump({
            "board_name": board_name,
            "author": author,
            "timer": False,
            "data": {
                "start": {},
                "stop": {},
                "continue": {}
            },
            "tmps": {}
        }, fichier, indent=4)

    return jsonify(["./board/" + board_id])


@app.route("/board/")
def home():
    if os.path.isfile("home.html"):
        return render_template("home.html")

    return jsonify(["board_not_found"])


@app.route("/board/<string:board_id>")
def board(board_id):
    if os.path.isfile("board.html"):
        return render_template("board.html")

    return jsonify(["board_not_found"])


@app.route("/js/<string:path>", methods=["GET"])
def js(path):
    if os.path.isfile("js/" + path):
        return send_from_directory(
            "js", path, mimetype="application/javascript"
        )

    return jsonify(["js_not_found"])


@app.route("/css/<string:path>", methods=["GET"])
def css(path):
    if os.path.isfile("css/" + path):
        return send_from_directory("css", path, mimetype="text/css")

    return jsonify(["css_not_found"])


@app.route("/img/<string:path>", methods=["GET"])
def png(path):
    if os.path.isfile("img/" + path):
        return send_from_directory("img/", path, mimetype="image/png")

    return jsonify(["png_not_found"])


# ///////////////////////////////////////////////////////////////////////


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8008, debug=True)

    except OSError as e:
        logging.error(f"Server error: {e}")
