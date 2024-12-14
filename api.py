from flask import Flask, render_template, send_from_directory
from flask_jsonpify import jsonify
import os
import json
import uuid
import logging

from gevent import monkey
monkey.patch_all()

logging.basicConfig(filename="retrogile.log", level=logging.DEBUG)


# ///////////////////////////////////////////////////////////////////////

app = Flask(__name__, template_folder="./pages/")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/LICENSES")
def licenses():
    return render_template("licenses.html")


@app.route("/create_board/<string:board_name>/<string:author>")
def create_board(board_name, author):
    board_dir = './board/'
    if not os.path.isdir(board_dir):
        os.mkdir(board_dir)

    board_id = uuid.uuid4().hex
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
    return render_template("home.html")

@app.route("/board/<string:board_id>")
def board(board_id):
    return render_template("board.html")


@app.route("/js/<string:path>", methods=["GET"])
def JS(path):
    if os.path.isfile("js/" + path):
        try:
            return send_from_directory(
                "js", path, mimetype="application/javascript"
            )
        except Exception as e:
            return jsonify(["send_from_directory_error: " + str(e)])

    return jsonify(["js_not_found"])


@app.route("/css/<string:path>", methods=["GET"])
def CSS(path):
    if os.path.isfile("css/" + path):
        try:
            return send_from_directory("css", path, mimetype="text/css")
        except Exception as e:
            return jsonify(["send_from_directory_error: " + str(e)])

    return jsonify(["css_not_found"])


@app.route("/img/<string:path>", methods=["GET"])
def PNG(path):
    if os.path.isfile("img/" + path):
        try:
            return send_from_directory("img/", path, mimetype="image/png")
        except Exception as e:
            return jsonify(["send_from_directory_error: " + str(e)])

    return jsonify(["png_not_found"])


# ///////////////////////////////////////////////////////////////////////


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8008, debug=False)

    except OSError as e:
        logging.error(f"Server error: {e}")
