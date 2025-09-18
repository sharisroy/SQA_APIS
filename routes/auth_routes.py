from flask import Blueprint, request, jsonify
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

auth_bp = Blueprint("auth", __name__)

# Supabase connection
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")

    if not email or not password or not name or not phone:
        return jsonify({
            "success": False,
            "code": 400,
            "error": "Name, email, phone, and password are required."
        }), 400

    try:
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"name": name, "phone": phone}}
        })

        response_data = {
            "success": True,
            "code": 200,
            "message": "User registered successfully.",
            "user": {
                "email": email,
                "name": name,
                "phone": phone
            }
        }
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"success": False, "code": 400, "error": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "code": 400,
            "error": "Email and password are required."
        }), 400

    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        session = auth_response.session
        user = auth_response.user

        response_data = {
            "success": True,
            "code": 200,
            "message": "Login successful.",
            "user": {
                "email": user.email if user else None,
                "name": user.user_metadata.get("name") if user and user.user_metadata else None,
                "phone": user.user_metadata.get("phone") if user and user.user_metadata else None,
            },
            "auth": {
                "access_token": session.access_token if session else None,
                "expires_at": session.expires_at if session else None
            }
        }
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"success": False, "code": 400, "error": str(e)}), 400
