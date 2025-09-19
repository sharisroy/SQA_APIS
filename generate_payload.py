import json
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import requests

# === Load keys ===
with open("keys/server_public.pem", "rb") as f:
    server_public = serialization.load_pem_public_key(f.read())

with open("keys/client_private.pem", "rb") as f:
    client_private = serialization.load_pem_private_key(f.read(), password=None)

# === Prepare login data ===
login_data = {
    "email": "haris@gmail.com",
    "password": "haris123"
}
login_json = json.dumps(login_data).encode()

# === Encrypt login JSON with server public key ===
encrypted = server_public.encrypt(
    login_json,
    padding.PKCS1v15()
)
encrypted_b64 = base64.b64encode(encrypted).decode()

# === Sign the encrypted data with client private key ===
signature = client_private.sign(
    encrypted,
    padding.PKCS1v15(),
    hashes.SHA256()
)
signature_b64 = base64.b64encode(signature).decode()

# === Output payload JSON ===
payload = {
    "data": encrypted_b64,
    "signature": signature_b64
}

print("Paste this in Postman body:")
print(json.dumps(payload, indent=4))

# === Optional: Send directly to Flask endpoint ===
response = requests.post("http://127.0.0.1:5000/auth/secure/login", json=payload)
print("\nServer Response:")
print(response.json())
