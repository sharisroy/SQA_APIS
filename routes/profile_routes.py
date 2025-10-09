from flask import Blueprint, request, jsonify
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime

# -----------------------------
# 🔧 Setup
# -----------------------------
load_dotenv()
profile_bp = Blueprint("profile", __name__)

# -----------------------------
# 🧩 Supabase Connection
# -----------------------------
SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# ⚙️ Helper Functions
# -----------------------------
def format_error(message: str, code: int = 400):
    """Standardized JSON error response."""
    return jsonify({"success": False, "code": code, "error": message}), code


def get_user_from_token(token: str):
    """Validate Bearer token and return user object, or error response."""
    if not token:
        return None, format_error("Missing Authorization header.", 401)

    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        user_resp = supabase.auth.get_user(token)
        if not user_resp.user:
            return None, format_error("Invalid or expired token.", 401)
        return user_resp.user, None
    except Exception as e:
        return None, format_error(f"Token validation failed: {str(e)}", 500)


# -----------------------------
# 👤 GET /me → Retrieve User Profile
# -----------------------------
@profile_bp.route("/me", methods=["GET"])
def get_profile():
    token = request.headers.get("Authorization")
    user, error = get_user_from_token(token)
    if error:
        return error

    try:
        profile_data = {
            "email": user.email,
            "name": user.user_metadata.get("name") if user.user_metadata else None,
            "joined_at": user.user_metadata.get("joined_at") if user.user_metadata else None
        }

        return jsonify({
            "success": True,
            "code": 200,
            "message": "Profile retrieved successfully.",
            "user": profile_data
        }), 200

    except Exception as e:
        return format_error(f"Failed to retrieve profile: {str(e)}", 500)
