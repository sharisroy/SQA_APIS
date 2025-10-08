from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime
import uuid

note_bp = Blueprint("note", __name__)

# Dummy secret key (replace with your real one, or import from config)
SECRET_KEY = "your_secret_key_here"

# In-memory notes storage (for demo)
NOTES_DB = []


# ==========================================================
# 🔐 JWT Token Validation Helper
# ==========================================================
def verify_bearer_token():
    """Validate Authorization header and decode JWT."""
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


# ==========================================================
# 📝 CREATE NOTE
# ==========================================================
@note_bp.route("/create", methods=["POST"])
def create_note():
    """Create a new note (protected)."""
    user, error_response, status = verify_bearer_token()
    if error_response:
        return error_response, status

    data = request.get_json()
    if not data or "title" not in data or "content" not in data:
        return jsonify({"success": False, "code": 400, "error": "Missing required fields: title, content"}), 400

    note = {
        "id": str(uuid.uuid4()),
        "title": data["title"],
        "content": data["content"],
        "owner": user.get("username"),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": None
    }
    NOTES_DB.append(note)

    return jsonify({"success": True, "message": "Note created successfully", "note": note}), 201


# ==========================================================
# 📜 GET ALL NOTES
# ==========================================================
@note_bp.route("/list", methods=["GET"])
def list_notes():
    """Get all notes for the authenticated user."""
    user, error_response, status = verify_bearer_token()
    if error_response:
        return error_response, status

    username = user.get("username")
    user_notes = [n for n in NOTES_DB if n["owner"] == username]

    return jsonify({"success": True, "notes": user_notes}), 200


# ==========================================================
# 🔍 GET NOTE BY ID
# ==========================================================
@note_bp.route("/<note_id>", methods=["GET"])
def get_note_by_id(note_id):
    """Retrieve a single note by ID."""
    user, error_response, status = verify_bearer_token()
    if error_response:
        return error_response, status

    username = user.get("username")
    note = next((n for n in NOTES_DB if n["id"] == note_id and n["owner"] == username), None)

    if not note:
        return jsonify({"success": False, "code": 404, "error": "Note not found"}), 404

    return jsonify({"success": True, "note": note}), 200


# ==========================================================
# ✏️ UPDATE NOTE (PATCH)
# ==========================================================
@note_bp.route("/update/<note_id>", methods=["PATCH"])
def update_note(note_id):
    """Update note title or content."""
    user, error_response, status = verify_bearer_token()
    if error_response:
        return error_response, status

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "code": 400, "error": "Missing JSON body"}), 400

    username = user.get("username")
    for note in NOTES_DB:
        if note["id"] == note_id and note["owner"] == username:
            if "title" in data:
                note["title"] = data["title"]
            if "content" in data:
                note["content"] = data["content"]
            note["updated_at"] = datetime.utcnow().isoformat()
            return jsonify({"success": True, "message": "Note updated successfully", "note": note}), 200

    return jsonify({"success": False, "code": 404, "error": "Note not found or unauthorized"}), 404


# ==========================================================
# 🗑️ DELETE NOTE
# ==========================================================
@note_bp.route("/delete/<note_id>", methods=["DELETE"])
def delete_note(note_id):
    """Delete a note by ID."""
    user, error_response, status = verify_bearer_token()
    if error_response:
        return error_response, status

    username = user.get("username")
    global NOTES_DB
    before_count = len(NOTES_DB)
    NOTES_DB = [n for n in NOTES_DB if not (n["id"] == note_id and n["owner"] == username)]

    if len(NOTES_DB) == before_count:
        return jsonify({"success": False, "code": 404, "error": "Note not found or unauthorized"}), 404

    return jsonify({"success": True, "message": "Note deleted successfully"}), 200
