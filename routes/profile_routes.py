from flask import Blueprint, request, jsonify
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

profile_bp = Blueprint("profile", __name__)

# Initialize Supabase connection
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# -------------------
# Helper Functions
# -------------------
def format_error(message: str, code: int = 400):
    """Return consistent JSON error format."""
    return jsonify({"success": False, "code": code, "error": message}), code


def get_user_from_token(token: str):
    """Validate the Bearer token and return Supabase user object or an error."""
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
        return None, format_error(f"Token validation error: {str(e)}", 401)


# -------------------
# GET /profile/me → Retrieve user profile
# -------------------
@profile_bp.route("/me", methods=["GET"])
def get_profile():
    """Return the currently authenticated user's profile information."""
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
                "id": user.id,
                "email": user.email,
                "name": user.user_metadata.get("name") if user.user_metadata else None,
                "phone": user.user_metadata.get("phone") if user.user_metadata else None,
            },
        }
        return jsonify(response_data), 200

    except Exception as e:
        return format_error(f"Failed to retrieve profile: {str(e)}", 500)
