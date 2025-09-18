from flask import Blueprint, request, jsonify
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

auth_bp = Blueprint("auth", __name__)

# Supabase connection
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def format_error(message: str, code: int = 400):
    """Helper to format error responses."""
    return jsonify({"success": False, "code": code, "error": message}), code


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return format_error("Name, email, and password are required.", 400)

    try:
        supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"name": name}}
        })

        response_data = {
            "success": True,
            "code": 200,
            "message": "User registered successfully.",
            "user": {
                "email": email,
                "name": name
            }
        }
        return jsonify(response_data), 200

    except Exception as e:
        return format_error(str(e), 400)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return format_error("Email and password are required.", 400)

    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        user = auth_response.user
        session = auth_response.session

        if not user or not session:
            return format_error("Invalid login credentials.", 401)

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
        return jsonify(response_data), 200

    except Exception as e:
        return format_error(str(e), 400)
