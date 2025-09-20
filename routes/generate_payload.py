# routes/generate_payload.py
from flask import Blueprint, request, jsonify
import json
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os

secure_bp = Blueprint("secure_bp", __name__)

# Define key paths
SERVER_PUBLIC_KEY_PATH = "keys/server_public_key.pem"
CLIENT_PRIVATE_KEY_PATH = "keys/client_private_key.pem"

# Ensure key files exist
if not os.path.exists(SERVER_PUBLIC_KEY_PATH) or not os.path.exists(CLIENT_PRIVATE_KEY_PATH):
    raise FileNotFoundError("Required key files not found in 'keys/' directory.")

# Load server public key
with open(SERVER_PUBLIC_KEY_PATH, "rb") as key_file:
    server_public_key = serialization.load_pem_public_key(key_file.read())

# Load client private key
with open(CLIENT_PRIVATE_KEY_PATH, "rb") as key_file:
    client_private_key = serialization.load_pem_private_key(key_file.read(), password=None)

@secure_bp.route("/generate_payload", methods=["POST"])
def generate_payload():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"success": False, "error": "Please provide 'email' and 'password' in request body"}), 400

    email = data["email"]
    password = data["password"]

    login_data = {"email": email, "password": password}
    payload_bytes = json.dumps(login_data).encode("utf-8")

    # Encrypt the payload
    encrypted_payload = server_public_key.encrypt(
        payload_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Sign the original payload
    signature = client_private_key.sign(
        payload_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    response_data = {
        "payload": encrypted_payload.hex(),
        "signature": signature.hex()
    }

    # Print to server logs (optional)
    print(response_data)

    return jsonify(response_data)
