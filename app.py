from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)

# Create messages directory if it doesn't exist
MESSAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "messages")
if not os.path.exists(MESSAGES_DIR):
    os.makedirs(MESSAGES_DIR)


def get_messages(user_id):
    filename = os.path.join(MESSAGES_DIR, f"{user_id}.json")
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return []


def save_message(user_id, message):
    filename = os.path.join(MESSAGES_DIR, f"{user_id}.json")
    messages = get_messages(user_id)
    messages.append(
        {
            "id": str(uuid.uuid4()),
            "content": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    with open(filename, "w") as f:
        json.dump(messages, f)
    print(f"Message saved to {filename}")  # Debug print


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create", methods=["POST"])
def create_link():
    user_id = str(uuid.uuid4())
    return jsonify({"link": f"/message/{user_id}"})


@app.route("/message/<user_id>")
def message_page(user_id):
    return render_template("message.html", user_id=user_id)


@app.route("/send/<user_id>", methods=["POST"])
def send_message(user_id):
    message = request.form.get("message")
    print(f"Received message for user {user_id}: {message}")  # Debug print
    if message:
        save_message(user_id, message)
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/view/<user_id>")
def view_messages(user_id):
    messages = get_messages(user_id)
    print(f"Retrieved {len(messages)} messages for user {user_id}")  # Debug print
    return render_template("view.html", messages=messages)


if __name__ == "__main__":
    app.run(debug=True)
