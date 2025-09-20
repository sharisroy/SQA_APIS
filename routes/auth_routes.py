from flask import Blueprint, request, jsonify, current_app, send_file
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import json

# Load environment variables from .env file
load_dotenv()

# Define the Blueprint for authentication routes
auth_bp = Blueprint("auth", __name__)

# Supabase client setup
try:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    raise RuntimeError(f"Failed to connect to Supabase: {e}")

# Load cryptographic keys from the 'keys' directory
try:
    with open("keys/server_private_key.pem", "rb") as key_file:
        server_private_key = serialization.load_pem_private_key(key_file.read(), password=None)
    with open("keys/client_public_key.pem", "rb") as key_file:
        client_public_key = serialization.load_pem_public_key(key_file.read())
except FileNotFoundError as e:
    raise RuntimeError(
        f"Required key file not found: {e}. Please ensure 'keys' folder exists and contains 'server_private_key.pem' and 'client_public_key.pem'.")


def format_error(message: str, code: int = 400):
    return jsonify({"success": False, "code": code, "error": message}), code


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Handles new user registration."""
    data = request.json or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return format_error("Name, email, and password are required.", 400)

    try:
        supabase.auth.sign_up({"email": email, "password": password, "options": {"data": {"name": name}}})
        response_data = {
            "success": True,
            "code": 200,
            "message": "User registered successfully.",
            "user": {"email": email, "name": name}
        }
        return jsonify(response_data), 200
    except Exception as e:
        return format_error(f"Signup failed: {str(e)}", 400)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Handles user login with unencrypted credentials."""
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return format_error("Email and password are required.", 400)

    try:
        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user = auth_response.user
        session = auth_response.session

        if not user or not session:
            return format_error("Invalid login credentials.", 401)

        response_data = {
            "success": True,
            "code": 200,
            "message": "Login successful.",
            "user": {"email": user.email, "name": user.user_metadata.get("name") if user.user_metadata else None},
            "auth": {"access_token": session.access_token, "expires_at": session.expires_at}
        }
        return jsonify(response_data), 200
    except Exception as e:
        return format_error(f"Login failed: {str(e)}", 400)


@auth_bp.route("/secure/login", methods=["POST"])
def secure_login():
    """Handles user login with encrypted and signed credentials."""
    data = request.json or {}
    current_app.logger.info(f"Received data from client: {data}")
    encrypted_payload_hex = data.get("payload")
    signature_hex = data.get("signature")

    if not encrypted_payload_hex or not signature_hex:
        return format_error("Payload and signature are required.", 400)

    try:
        encrypted_payload = bytes.fromhex(encrypted_payload_hex)
        signature = bytes.fromhex(signature_hex)

        # Decrypt payload using the server's private key
        decrypted_bytes = server_private_key.decrypt(
            encrypted_payload,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        decrypted_payload = json.loads(decrypted_bytes.decode('utf-8'))

        # Verify signature using the client's public key
        client_public_key.verify(
            signature,
            decrypted_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

        email = decrypted_payload.get("email")
        password = decrypted_payload.get("password")

        if not all([email, password]):
            return format_error("Email and password are required inside the payload.", 400)

        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user = auth_response.user
        session = auth_response.session

        if not user or not session:
            return format_error("Invalid login credentials.", 401)

        response_data = {
            "success": True,
            "code": 200,
            "message": "Secure login successful.",
            "user": {"email": user.email, "name": user.user_metadata.get("name") if user.user_metadata else None},
            "auth": {"access_token": session.access_token, "expires_at": session.expires_at}
        }
        return jsonify(response_data), 200
    except Exception as e:
        current_app.logger.error(f"Cryptographic or login error: {e}")
        return format_error(f"Invalid encrypted payload or signature: {str(e)}", 400)


@auth_bp.route("/public-key", methods=["GET"])
def get_public_key():
    """Serves the server's public key for clients to use for encryption."""
    try:
        return send_file("keys/server_public_key.pem", mimetype="application/x-pem-file")
    except FileNotFoundError:
        return jsonify({"success": False, "error": "Server public key file not found."}), 404



@auth_bp.route("/client_private_key", methods=["GET"])
def get_client_private_key():
    """Serves the server's public key for clients to use for encryption."""
    try:
        return send_file("keys/client_private_key.pem", mimetype="application/x-pem-file")
    except FileNotFoundError:
        return jsonify({"success": False, "error": "Server public key file not found."}), 404