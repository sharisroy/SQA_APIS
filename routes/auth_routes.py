from flask import Blueprint, request, jsonify, current_app, send_file
from supabase import create_client, Client
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv
from datetime import datetime
import os
import json
import pytz

# ---------------------------------------------------------------------
# 🔧 Setup
# ---------------------------------------------------------------------
load_dotenv()
bd_timezone = pytz.timezone("Asia/Dhaka")

auth_bp = Blueprint("auth", __name__)

# ---------------------------------------------------------------------
# 🧩 Supabase Client Initialization
# ---------------------------------------------------------------------
try:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    raise RuntimeError(f"Failed to connect to Supabase: {e}")

# ---------------------------------------------------------------------
# 🔐 Load Cryptographic Keys
# ---------------------------------------------------------------------
try:
    with open("keys/server_private_key.pem", "rb") as f:
        server_private_key = serialization.load_pem_private_key(f.read(), password=None)
    with open("keys/client_public_key.pem", "rb") as f:
        client_public_key = serialization.load_pem_public_key(f.read())
except FileNotFoundError as e:
    raise RuntimeError(
        f"Missing key file: {e}. Ensure 'keys/server_private_key.pem' and 'keys/client_public_key.pem' exist."
    )


# ---------------------------------------------------------------------
# ⚙️ Utility
# ---------------------------------------------------------------------
def format_error(message: str, code: int = 400):
    """Return standardized JSON error."""
    return jsonify({"success": False, "code": code, "error": message}), code


# ---------------------------------------------------------------------
# 🧾 Routes
# ---------------------------------------------------------------------
@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Register a new user."""
    data = request.get_json() or {}
    name, email, password = data.get("name"), data.get("email"), data.get("password")

    if not all([name, email, password]):
        return format_error("Name, email, and password are required.", 400)

    try:
        supabase.auth.sign_up(
            {"email": email, "password": password, "options": {"data": {"name": name}}}
        )
        return jsonify({
            "success": True,
            "code": 200,
            "message": "User registered successfully.",
            "user": {"email": email, "name": name},
        }), 200

    except Exception as e:
        return format_error(f"Signup failed: {e}", 400)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Handle normal login."""
    data = request.get_json() or {}
    email, password = data.get("email"), data.get("password")

    if not all([email, password]):
        return format_error("Email and password are required.", 400)

    try:
        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user, session = auth_response.user, auth_response.session

        if not user or not session:
            return format_error("Invalid login credentials.", 401)

        expires_at_dt = datetime.fromtimestamp(session.expires_at, tz=bd_timezone)

        return jsonify({
            "success": True,
            "code": 200,
            "message": "Login successful.",
            "user": {
                "email": user.email,
                "name": user.user_metadata.get("name") if user.user_metadata else None,
            },
            "auth": {
                "access_token": session.access_token,
                "expires_at": expires_at_dt.isoformat(),
            },
        }), 200

    except Exception as e:
        return format_error(f"Login failed: {e}", 400)


@auth_bp.route("/secure/login", methods=["POST"])
def secure_login():
    """Login with encrypted + signed payload."""
    data = request.get_json() or {}
    encrypted_hex = data.get("payload")
    signature_hex = data.get("signature")

    if not all([encrypted_hex, signature_hex]):
        return format_error("Payload and signature are required.", 400)

    try:
        encrypted_bytes = bytes.fromhex(encrypted_hex)
        signature = bytes.fromhex(signature_hex)

        decrypted_bytes = server_private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
        )
        decrypted_payload = json.loads(decrypted_bytes.decode("utf-8"))

        client_public_key.verify(
            signature,
            decrypted_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )

        email = decrypted_payload.get("email")
        password = decrypted_payload.get("password")

        if not all([email, password]):
            return format_error("Email and password required inside payload.", 400)

        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user, session = auth_response.user, auth_response.session
        if not user or not session:
            return format_error("Invalid login credentials.", 401)

        expires_at_dt = datetime.fromtimestamp(session.expires_at, tz=bd_timezone)

        return jsonify({
            "success": True,
            "code": 200,
            "message": "Secure login successful.",
            "user": {
                "email": user.email,
                "name": user.user_metadata.get("name") if user.user_metadata else None,
            },
            "auth": {
                "access_token": session.access_token,
                "expires_at": expires_at_dt.isoformat(),
            },
        }), 200

    except Exception as e:
        current_app.logger.error(f"Secure login failed: {e}")
        return format_error(f"Invalid encrypted payload or signature: {e}", 400)


@auth_bp.route("/public-key", methods=["GET"])
def get_public_key():
    """Get server’s public key."""
    try:
        return send_file("keys/server_public_key.pem", mimetype="application/x-pem-file")
    except FileNotFoundError:
        return format_error("Server public key file not found.", 404)
