from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
    flash,
)
import json
import os
from datetime import datetime
import uuid
from cryptography.fernet import Fernet
import re
import hashlib
import secrets
import base64
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # For session management

# Create necessary directories
MESSAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "messages")
USERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users")
for directory in [MESSAGES_DIR, USERS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)


def validate_password(password):
    """Validate that password is 6 digits"""
    return bool(re.match(r"^\d{6}$", password))


def get_user_data(username):
    """Get user data from file"""
    filename = os.path.join(USERS_DIR, f"{username}.json")
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return None


def save_user_data(username, data):
    """Save user data to file"""
    filename = os.path.join(USERS_DIR, f"{username}.json")
    with open(filename, "w") as f:
        json.dump(data, f)


def get_encryption_key(username, password):
    """Generate encryption key from username and password"""
    key_material = f"{username}:{password}".encode()
    # Use SHA-256 to generate a 32-byte key
    key = hashlib.sha256(key_material).digest()
    # Convert to base64 for Fernet
    return base64.urlsafe_b64encode(key)


def encrypt_message(message, username, password):
    """Encrypt message using username and password"""
    try:
        key = get_encryption_key(username, password)
        f = Fernet(key)
        return f.encrypt(message.encode()).decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return None


def decrypt_message(encrypted_message, username, password):
    """Decrypt message using username and password"""
    try:
        key = get_encryption_key(username, password)
        f = Fernet(key)
        return f.decrypt(encrypted_message.encode()).decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return None


def get_messages(user_id):
    """Get messages for a user"""
    filename = os.path.join(MESSAGES_DIR, f"{user_id}.json")
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error reading messages for user {user_id}")
            return []
    return []


def save_message(user_id, message, username, password):
    """Save encrypted message"""
    filename = os.path.join(MESSAGES_DIR, f"{user_id}.json")
    try:
        messages = get_messages(user_id)
        encrypted_message = encrypt_message(message, username, password)
        if encrypted_message:
            messages.append(
                {
                    "id": str(uuid.uuid4()),
                    "content": encrypted_message,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
            with open(filename, "w") as f:
                json.dump(messages, f)
            return True
    except Exception as e:
        print(f"Error saving message: {e}")
    return False


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and PIN are required")
            return redirect(url_for("register"))

        if not validate_password(password):
            flash("PIN must be exactly 6 digits")
            return redirect(url_for("register"))

        if get_user_data(username):
            flash("Username already exists")
            return redirect(url_for("register"))

        user_id = str(uuid.uuid4())
        user_data = {
            "username": username,
            "password": generate_password_hash(password),  # Store hashed PIN
            "user_id": user_id,
        }
        save_user_data(username, user_data)

        session["username"] = username
        session["user_id"] = user_id
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user_data = get_user_data(username)
        if not user_data or not check_password_hash(user_data["password"], password):
            flash("Invalid username or PIN")
            return redirect(url_for("login"))

        session["username"] = username
        session["user_id"] = user_data["user_id"]
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    message_count = len(get_messages(user_id))

    return render_template(
        "dashboard.html", username=session["username"], message_count=message_count
    )


@app.route("/create", methods=["POST"])
def create_link():
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    user_id = session["user_id"]
    return jsonify({"link": f"/message/{user_id}"})


@app.route("/message/<user_id>")
def message_page(user_id):
    user_data = None
    for filename in os.listdir(USERS_DIR):
        with open(os.path.join(USERS_DIR, filename), "r") as f:
            data = json.load(f)
            if data["user_id"] == user_id:
                user_data = data
                break

    if not user_data:
        return "User not found", 404

    return render_template(
        "message.html", user_id=user_id, username=user_data["username"]
    )


@app.route("/send/<user_id>", methods=["POST"])
def send_message(user_id):
    message = request.form.get("message")
    if not message:
        return jsonify({"success": False, "error": "Message is required"})

    user_data = None
    for filename in os.listdir(USERS_DIR):
        with open(os.path.join(USERS_DIR, filename), "r") as f:
            data = json.load(f)
            if data["user_id"] == user_id:
                user_data = data
                break

    if not user_data:
        return jsonify({"success": False, "error": "User not found"})

    if save_message(user_id, message, user_data["username"], user_data["password"]):
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Failed to save message"})


@app.route("/view/<user_id>")
def view_messages(user_id):
    if "username" not in session or session["user_id"] != user_id:
        return redirect(url_for("login"))

    user_data = get_user_data(session["username"])
    if not user_data:
        return redirect(url_for("login"))

    messages = get_messages(user_id)
    decrypted_messages = []
    for msg in messages:
        decrypted_content = decrypt_message(
            msg["content"], user_data["username"], user_data["password"]
        )
        if decrypted_content:
            decrypted_messages.append(
                {
                    "id": msg["id"],
                    "content": decrypted_content,
                    "timestamp": msg["timestamp"],
                }
            )

    return render_template("view.html", messages=decrypted_messages)


if __name__ == "__main__":
    app.run(debug=True)
