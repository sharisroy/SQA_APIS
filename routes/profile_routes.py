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

# -------------------
# Helper Functions
# -------------------
def format_error(message: str, code: int = 400):
    return jsonify({"success": False, "code": code, "error": message}), code

def get_user_from_token(token: str):
    """Validate token and return user info, or error response."""
    if not token:
        return None, format_error("Missing Authorization header.", 401)
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
    user_resp = supabase.auth.get_user(token)
    if not user_resp.user:
        return None, format_error("Invalid or expired token.", 401)
    return user_resp.user, None


# -------------------
# GET /me → Retrieve user profile
# -------------------
@profile_bp.route("/me", methods=["GET"])
def profile():
    token = request.headers.get("Authorization")
    user, error = get_user_from_token(token)
    if error:
        return error

    try:
        response_data = {
            "success": True,
            "code": 200,
            "message": "Profile retrieved successfully.",
            "user": {
                "email": user.email,
                "name": user.user_metadata.get("name") if user.user_metadata else None
            }
        }
        return jsonify(response_data), 200
    except Exception as e:
        return format_error(str(e), 400)
