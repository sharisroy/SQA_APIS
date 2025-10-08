from flask import Blueprint, request, jsonify, current_app, send_file
from supabase import create_client, Client
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv
from datetime import datetime
import os
import json
import pytz

# ----------------------------- #
# 🔧 Setup
# ----------------------------- #

load_dotenv()
bd_timezone = pytz.timezone("Asia/Dhaka")

auth_bp = Blueprint("auth", __name__)

# ----------------------------- #
# 🧩 Supabase Client Initialization
# ----------------------------- #
try:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    raise RuntimeError(f"Failed to connect to Supabase: {e}")

# ----------------------------- #
# 🔐 Load Cryptographic Keys
# ----------------------------- #
try:
    with open("keys/server_private_key.pem", "rb") as f:
        server_private_key = serialization.load_pem_private_key(f.read(), password=None)
    with open("keys/client_public_key.pem", "rb") as f:
        client_public_key = serialization.load_pem_public_key(f.read())
except FileNotFoundError as e:
    raise RuntimeError(
        f"Missing key file: {e}. Ensure 'keys/server_private_key.pem' and 'keys/client_public_key.pem' exist."
    )

# ----------------------------- #
# ⚙️ Utility Functions
# ----------------------------- #
def format_error(message: str, code: int = 400):
    """Standardized JSON error response."""
    return jsonify({"success": False, "code": code, "error": message}), code


# ----------------------------- #
# 🧾 Routes
# ----------------------------- #

@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Handles new user registration."""
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return format_error("Name, email, and password are required.", 400)

    try:
        supabase.auth.sign_up(
            {"email": email, "password": password, "options": {"data": {"name": name}}}
        )

        response_data = {
            "success": True,
            "code": 200,
            "message": "User registered successfully.",
            "user": {"email": email, "name": name},
        }
        return jsonify(response_data), 200

    except Exception as e:
        return format_error(f"Signup failed: {e}", 400)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Handles user login with plain (unencrypted) credentials."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return format_error("Email and password are required.", 400)

    try:
        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user, session = auth_response.user, auth_response.session

        if not user or not session:
            return format_error("Invalid login credentials.", 401)

        # Convert expires_at (int timestamp) to local time
        expires_at_dt = datetime.fromtimestamp(session.expires_at, tz=bd_timezone)

        response_data = {
            "success": True,
            "code": 200,
            "message": "Login successful.",
            "user": {
                "email": user.email,
                "name": user.user_metadata.get("name") if user.user_metadata else None,
            },
            "auth": {
                "access_token": session.access_token,
                "expires_at": expires_at_dt.isoformat()
            },
        }
        return jsonify(response_data), 200

    except Exception as e:
        return format_error(f"Login failed: {e}", 400)


@auth_bp.route("/secure/login", methods=["POST"])
def secure_login():
    """Handles user login using encrypted and signed credentials."""
    data = request.get_json() or {}
    current_app.logger.info(f"Received encrypted payload: {data}")

    encrypted_payload_hex = data.get("payload")
    signature_hex = data.get("signature")

    if not all([encrypted_payload_hex, signature_hex]):
        return format_error("Payload and signature are required.", 400)

    try:
        encrypted_payload = bytes.fromhex(encrypted_payload_hex)
        signature = bytes.fromhex(signature_hex)

        # Decrypt payload
        decrypted_bytes = server_private_key.decrypt(
            encrypted_payload,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
        )
        decrypted_payload = json.loads(decrypted_bytes.decode("utf-8"))

        # Verify signature
        client_public_key.verify(
            signature,
            decrypted_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )

        email = decrypted_payload.get("email")
        password = decrypted_payload.get("password")

        if not all([email, password]):
            return format_error("Email and password are required inside the payload.", 400)

        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user, session = auth_response.user, auth_response.session

        if not user or not session:
            return format_error("Invalid login credentials.", 401)

        # Convert expires_at (int timestamp) to local time
        expires_at_dt = datetime.fromtimestamp(session.expires_at, tz=bd_timezone)

        response_data = {
            "success": True,
            "code": 200,
            "message": "Secure login successful.",
            "user": {
                "email": user.email,
                "name": user.user_metadata.get("name") if user.user_metadata else None,
            },
            "auth": {
                "access_token": session.access_token,
                "expires_at": expires_at_dt.isoformat()
            },
        }
        return jsonify(response_data), 200

    except Exception as e:
        current_app.logger.error(f"Cryptographic or login error: {e}")
        return format_error(f"Invalid encrypted payload or signature: {e}", 400)


@auth_bp.route("/public-key", methods=["GET"])
def get_public_key():
    """Serves the server's public key for client encryption."""
    try:
        return send_file("keys/server_public_key.pem", mimetype="application/x-pem-file")
    except FileNotFoundError:
        return format_error("Server public key file not found.", 404)


@auth_bp.route("/client-private-key", methods=["GET"])
def get_client_private_key():
    """Serves the client’s private key (for testing only)."""
    try:
        return send_file("keys/client_private_key.pem", mimetype="application/x-pem-file")
    except FileNotFoundError:
        return format_error("Client private key file not found.", 404)
