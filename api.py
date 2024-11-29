from flask import Flask, render_template, send_from_directory, redirect
from flask_jsonpify import jsonify
from flask_sock import Sock
import os
import json
import uuid

import logging

logging.basicConfig(filename="retrogile.log", level=logging.DEBUG)

app = Flask(__name__, template_folder="./")
sock = Sock(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/create_board/<string:board_name>")
def create_board(board_name):
    board_dir = './board/'
    if not os.path.isdir(board_dir):
        os.mkdir(board_dir)

    board_id = uuid.uuid4().hex
    print(board_id)
    filename = f'{board_id}.json'
    print(filename)

    return jsonify(["./board/" + board_id])


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


















@sock.route("/socket")
def echo(sock):
    while True:
        data = sock.receive()

        data = json.loads(data)
        message_type = data.get("type")

        if message_type == "message":
            message_content = data.get("content")
            sock.send(message_content)

        else:
            print("unknow_type:", message_type)


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8008, debug=True)
    except OSError as e:
        logging.error(f"Server error: {e}")
