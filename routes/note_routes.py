from flask import Blueprint, request, jsonify, current_app
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

note_bp = Blueprint("note", __name__)

# Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# -------------------
# Helper Functions
# -------------------
def format_error(message: str, code: int = 400):
    """Consistent JSON error structure."""
    return jsonify({"success": False, "code": code, "error": message}), code


def get_user_from_token(token: str):
    """Validate JWT token and return user_id or an error."""
    if not token:
        return None, format_error("Missing Authorization header.", 401)

    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        user_resp = supabase.auth.get_user(token)
        if not user_resp.user:
            return None, format_error("Invalid or expired token.", 401)
        return user_resp.user.id, None
    except Exception as e:
        return None, format_error(f"Token validation error: {str(e)}", 401)


# -------------------
# POST /note → Create a new note
# -------------------
@note_bp.route("/", methods=["POST"])
def add_note():
    """Create a new note for the authenticated user."""
    try:
        token = request.headers.get("Authorization")
        data = request.get_json() or {}

        if not data.get("title") or not data.get("note"):
            return format_error("Title and Note are required.", 400)

        user_id, error = get_user_from_token(token)
        if error:
            return error

        note_id = str(uuid.uuid4())
        supabase.table("notes").insert({
            "id": note_id,
            "user_id": user_id,
            "title": data["title"],
            "note": data["note"]
        }).execute()

        return jsonify({
            "success": True,
            "code": 200,
            "message": "Note created successfully.",
            "note": {"id": note_id, "title": data["title"]}
        }), 200

    except Exception as e:
        return format_error(f"Failed to add note: {str(e)}", 500)


# -------------------
# GET /note/<id> → Retrieve note by ID
# -------------------
@note_bp.route("/<note_id>", methods=["GET"])
def get_note(note_id):
    """Retrieve a specific note by ID for the logged-in user."""
    try:
        token = request.headers.get("Authorization")
        user_id, error = get_user_from_token(token)
        if error:
            return error

        note_resp = supabase.table("notes").select("*").eq("id", note_id).eq("user_id", user_id).execute()
        if not note_resp.data:
            return format_error("Note not found.", 404)

        note = note_resp.data[0]
        return jsonify({
            "success": True,
            "code": 200,
            "note": {
                "id": note["id"],
                "title": note["title"],
                "note": note["note"]
            }
        }), 200

    except Exception as e:
        return format_error(f"Failed to get note: {str(e)}", 500)


# -------------------
# GET /note → Get all notes (with pagination)
# -------------------
@note_bp.route("/", methods=["GET"])
def get_all_notes():
    """Retrieve all notes for the user, with pagination support."""
    try:
        token = request.headers.get("Authorization")
        user_id, error = get_user_from_token(token)
        if error:
            return error

        page = max(int(request.args.get("page", 1)), 1)
        per_page = max(int(request.args.get("per_page", 10)), 1)
        offset = (page - 1) * per_page

        notes_resp = supabase.table("notes").select("*", count="exact") \
            .eq("user_id", user_id) \
            .range(offset, offset + per_page - 1) \
            .execute()

        notes = notes_resp.data or []
        total_notes = notes_resp.count or 0

        return jsonify({
            "success": True,
            "code": 200,
            "page": page,
            "per_page": per_page,
            "total_notes": total_notes,
            "notes": [{"id": n["id"], "title": n["title"]} for n in notes]
        }), 200

    except Exception as e:
        return format_error(f"Failed to fetch notes: {str(e)}", 500)


# -------------------
# PATCH /note/<id> → Update note
# -------------------
@note_bp.route("/<note_id>", methods=["PATCH"])
def update_note(note_id):
    """Update an existing note for the logged-in user."""
    try:
        token = request.headers.get("Authorization")
        data = request.get_json() or {}

        if not data.get("title") or not data.get("note"):
            return format_error("Both Title and Note fields are required.", 400)

        user_id, error = get_user_from_token(token)
        if error:
            return error

        existing = supabase.table("notes").select("*").eq("id", note_id).eq("user_id", user_id).execute()
        if not existing.data:
            return format_error("Note not found.", 404)

        supabase.table("notes").update({
            "title": data["title"],
            "note": data["note"]
        }).eq("id", note_id).eq("user_id", user_id).execute()

        return jsonify({"success": True, "code": 200, "message": "Note updated successfully."}), 200

    except Exception as e:
        return format_error(f"Failed to update note: {str(e)}", 500)


# -------------------
# DELETE /note/<id> → Delete note
# -------------------
@note_bp.route("/<note_id>", methods=["DELETE"])
def delete_note(note_id):
    """Delete a note by ID for the authenticated user."""
    try:
        token = request.headers.get("Authorization")
        user_id, error = get_user_from_token(token)
        if error:
            return error

        existing = supabase.table("notes").select("*").eq("id", note_id).eq("user_id", user_id).execute()
        if not existing.data:
            return format_error("Note not found.", 404)

        supabase.table("notes").delete().eq("id", note_id).eq("user_id", user_id).execute()

        return jsonify({"success": True, "code": 200, "message": "Note deleted successfully."}), 200

    except Exception as e:
        return format_error(f"Failed to delete note: {str(e)}", 500)
