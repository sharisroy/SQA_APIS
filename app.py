from flask import Flask, request, jsonify
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import jwt

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Supabase connection
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


@app.route("/")
def home():
    return jsonify({"message": "API Testing with Supabase!"})


@app.route("/signup", methods=["POST"])
def signup():
    data = request.json or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")

    if not email or not password or not name or not phone:
        return jsonify({"success": False, "error": "Name, email, phone and password required"}), 400

    try:
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "name": name,
                    "phone": phone
                }
            }
        })

        session = auth_response.session
        user = auth_response.user

        response_data = {
            "success": True,
            "message": "User signed up successfully",
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password required"}), 400

    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        session = auth_response.session
        user = auth_response.user

        response_data = {
            "success": True,
            "email": user.email if user else None,
            "name": user.user_metadata.get("name") if user and user.user_metadata else None,
            "phone": user.user_metadata.get("phone") if user and user.user_metadata else None,
            "access_token": session.access_token if session else None,
            "expires_at": session.expires_at if session else None,
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route("/me", methods=["GET"])
def profile():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"success": False, "error": "Missing Authorization header"}), 401

    try:
        # Remove Bearer prefix if present
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        # Verify the token with Supabase
        user = supabase.auth.get_user(token)

        if not user:
            return jsonify({"success": False, "error": "Invalid or expired token"}), 401

        response_data = {
            "success": True,
            "email": user.user.email,
            "name": user.user.user_metadata.get("name") if user.user.user_metadata else None,
            "phone": user.user.user_metadata.get("phone") if user.user.user_metadata else None,
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
