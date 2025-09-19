from flask import Blueprint, request, jsonify
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
import base64
import json

load_dotenv()

secure_auth_bp = Blueprint("secure_auth", __name__)

# Supabase client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Load RSA keys
with open(os.getenv("PRIVATE_KEY_PATH"), "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

with open(os.getenv("CLIENT_PUBLIC_KEY_PATH"), "rb") as f:
    client_public_key = serialization.load_pem_public_key(f.read())


def format_error(message: str, code: int = 400):
    return jsonify({"success": False, "code": code, "error": message}), code


@secure_auth_bp.route("/login", methods=["POST"])
def secure_login():
    # === Log incoming payload for debugging ===
    print("==== Incoming Request JSON ====")
    print(request.json)
    print("==============================")

    payload = request.json or {}
    encrypted_data_b64 = payload.get("data")
    signature_b64 = payload.get("signature")

    if not encrypted_data_b64 or not signature_b64:
        return format_error("Both 'data' and 'signature' are required.", 400)

    try:
        encrypted_data = base64.b64decode(encrypted_data_b64)
        signature = base64.b64decode(signature_b64)

        # === Verify signature ===
        try:
            client_public_key.verify(
                signature,
                encrypted_data,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
        except InvalidSignature:
            return format_error("Invalid signature.", 400)

        # === Decrypt data ===
        decrypted_data = private_key.decrypt(
            encrypted_data,
            padding.PKCS1v15()
        )
        login_data = json.loads(decrypted_data.decode())

        # === Extract credentials ===
        email = login_data.get("email")
        password = login_data.get("password")

        if not all([email, password]):
            return format_error("Email and password are required.", 400)

        # === Supabase login ===
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        user = auth_response.user
        session = auth_response.session

        if not user or not session:
            return format_error("Invalid login credentials.", 401)

        # === Success response ===
        response_data = {
            "success": True,
            "code": 200,
            "message": "Login successful.",
            "user": {
                "email": user.email,
                "name": user.user_metadata.get("name") if user.user_metadata else None
            },
            "auth": {
                "access_token": session.access_token,
                "expires_at": session.expires_at
            }
        }
        # === Log decrypted login for debugging ===
        print("==== Decrypted Login Data ====")
        print(login_data)
        print("==============================")
        return jsonify(response_data), 200

    except Exception as e:
        return format_error(str(e), 400)
