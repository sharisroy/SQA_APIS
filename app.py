from flask import Flask, request, jsonify
from supabase import create_client, Client
import os
from dotenv import load_dotenv

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
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password required"}), 400

    try:
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        session = auth_response.session
        user = auth_response.user

        response_data = {
            "success": True,
            "email": user.email if user else None,
            "access_token": session.access_token if session else None,
            "expires_at": session.expires_at if session else None,
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
            "access_token": session.access_token if session else None,
            "expires_at": session.expires_at if session else None,
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
