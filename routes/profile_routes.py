from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime

profile_bp = Blueprint("profile", __name__)

# Dummy secret key (replace with your real secret key)
SECRET_KEY = "your_secret_key_here"


# --- Helper Function for JWT Validation ---
def verify_bearer_token():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None, jsonify({"success": False, "code": 401, "error": "Missing Authorization header"}), 401

    if not auth_header.startswith("Bearer "):
        return None, jsonify({"success": False, "code": 401, "error": "Invalid token format. Must start with 'Bearer '"}), 401

    token = auth_header.split(" ")[1].strip()
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded, None, None
    except jwt.ExpiredSignatureError:
        return None, jsonify({"success": False, "code": 401, "error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return None, jsonify({"success": False, "code": 401, "error": "Invalid token"}), 401


# --- Profile Route ---
@profile_bp.route("/me", methods=["GET"])
def get_my_profile():
    """Fetch user profile info (protected route)."""
    user, error_response, status = verify_bearer_token()
    if error_response:
        return error_response, status

    profile_data = {
        "user_id": user.get("user_id"),
        "username": user.get("username", "Unknown User"),
        "email": user.get("email", "not_provided@example.com"),
        "joined_at": user.get("joined_at", datetime.utcnow().isoformat())
    }

    return jsonify({"success": True, "profile": profile_data}), 200


# --- Example of Profile Update ---
@profile_bp.route("/update", methods=["POST"])
def update_profile():
    """Allow user to update profile info."""
    user, error_response, status = verify_bearer_token()
    if error_response:
        return error_response, status

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "code": 400, "error": "Missing JSON body"}), 400

    updated_fields = {k: v for k, v in data.items() if v}
    updated_fields["updated_at"] = datetime.utcnow().isoformat()

    return jsonify({
        "success": True,
        "message": "Profile updated successfully",
        "updated_fields": updated_fields
    }), 200
