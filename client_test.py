import json
import requests
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os

# Define the paths to the keys
SERVER_PUBLIC_KEY_PATH = "keys/server_public_key.pem"
CLIENT_PRIVATE_KEY_PATH = "keys/client_private_key.pem"

# Ensure the required key files exist before proceeding
if not os.path.exists(SERVER_PUBLIC_KEY_PATH) or not os.path.exists(CLIENT_PRIVATE_KEY_PATH):
    print("Error: Required key files not found.")
    print(f"Please ensure '{SERVER_PUBLIC_KEY_PATH}' and '{CLIENT_PRIVATE_KEY_PATH}' exist in your project.")
    exit()

# Load the server's public key (for encryption)
with open(SERVER_PUBLIC_KEY_PATH, "rb") as key_file:
    server_public_key = serialization.load_pem_public_key(key_file.read())

# Load the client's private key (for signing)
with open(CLIENT_PRIVATE_KEY_PATH, "rb") as key_file:
    client_private_key = serialization.load_pem_private_key(key_file.read(), password=None)

# The sensitive data to be encrypted
login_data = {
    "email": "haris@gmail.com",
    "password": "haris123"
}
payload_bytes = json.dumps(login_data).encode('utf-8')

# Encrypt the payload with the server's public key
encrypted_payload = server_public_key.encrypt(
    payload_bytes,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Sign the original, unencrypted payload with the client's private key
signature = client_private_key.sign(
    payload_bytes,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# Prepare the data for the API request
url = "http://127.0.0.1:5001/auth/secure/login"
headers = {"Content-Type": "application/json"}
data = {
    "payload": encrypted_payload.hex(),
    "signature": signature.hex()
}

print(data)

# Send the secure login request
try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    print("Secure Login Successful!")
    print(json.dumps(response.json(), indent=4))
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    if response:
        print(f"Server response: {response.json()}")