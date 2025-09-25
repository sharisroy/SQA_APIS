from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_key_pair(name):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key = private_key.public_key()
    pem_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(f"{name}_private_key.pem", "wb") as f:
        f.write(pem_private_key)

    with open(f"{name}_public_key.pem", "wb") as f:
        f.write(pem_public_key)

    print(f"{name.capitalize()} key pair generated successfully.")


# Generate key pairs for the server and the client
generate_key_pair("server")
generate_key_pair("client")