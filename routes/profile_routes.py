from flask import Blueprint, request, jsonify
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

profile_bp = Blueprint("profile", __name__)

# Supabase connection
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


@profile_bp.route("/me", methods=["GET"])
def profile():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"success": False, "code": 401, "error": "Missing Authorization header."}), 401

    try:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        user = supabase.auth.get_user(token)

        if not user:
            return jsonify({"success": False, "code": 401, "error": "Invalid or expired token."}), 401

        response_data = {
            "success": True,
            "code": 200,
            "message": "Profile retrieved successfully.",
            "user": {
                "email": user.user.email,
                "name": user.user.user_metadata.get("name") if user.user.user_metadata else None,
                "phone": user.user.user_metadata.get("phone") if user.user.user_metadata else None,
            }
        }
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"success": False, "code": 400, "error": str(e)}), 400
