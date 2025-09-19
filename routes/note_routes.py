from flask import Blueprint, request, jsonify
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import uuid

# Load environment
load_dotenv()

note_bp = Blueprint("note", __name__)

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
    """Validate token and return user id, or None."""
    if not token:
        return None, format_error("Missing Authorization header.", 401)
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
    user_resp = supabase.auth.get_user(token)
    if not user_resp.user:
        return None, format_error("Invalid or expired token.", 401)
    return user_resp.user.id, None


# -------------------
# POST /note → Add a note
# -------------------
@note_bp.route("/", methods=["POST"])
def add_note():
    token = request.headers.get("Authorization")
    data = request.json or {}

    if not data.get("note") or not data.get("title"):
        return format_error("Title and Note are required.", 400)

    user_id, error = get_user_from_token(token)
    if error:
        return error

    note_id = str(uuid.uuid4())
    try:
        supabase.table("notes").insert({
            "id": note_id,
            "user_id": user_id,
            "title": data["title"],
            "note": data["note"]
        }).execute()
        return jsonify({
            "success": True,
            "code": 200,
            "note": {
                "id": note_id,
                "title": data["title"]
            }
        }), 200
    except Exception as e:
        return format_error(str(e), 400)


# -------------------
# GET /note/<id> → Retrieve a note by ID
# -------------------
@note_bp.route("/<note_id>", methods=["GET"])
def get_note(note_id):
    token = request.headers.get("Authorization")
    user_id, error = get_user_from_token(token)
    if error:
        return error

    try:
        note_resp = supabase.table("notes").select("*").eq("id", note_id).eq("user_id", user_id).execute()
        if not note_resp.data:
            return format_error("Note not found.", 404)
        note = note_resp.data[0]
        return jsonify({
            "success": True,
            "code": 200,
            "note": {
                "title": note.get("title"),
                "note": note["note"]
            }
        }), 200
    except Exception as e:
        return format_error(str(e), 400)


# -------------------
# GET /note → Get all notes for the authenticated user with pagination
# -------------------
@note_bp.route("/", methods=["GET"])
def get_all_notes():
    token = request.headers.get("Authorization")
    user_id, error = get_user_from_token(token)
    if error:
        return error

    try:
        page = max(int(request.args.get("page", 1)), 1)
        per_page = max(int(request.args.get("per_page", 10)), 1)
        offset = (page - 1) * per_page

        notes_resp = supabase.table("notes").select("*", count="exact")\
            .eq("user_id", user_id)\
            .range(offset, offset + per_page - 1).execute()

        notes_data = notes_resp.data or []
        total_notes = notes_resp.count or 0

        response = {
            "success": True,
            "code": 200,
            "page": page,
            "per_page": per_page,
            "total_notes": total_notes,
            "notes": [{"id": note["id"], "title": note.get("title")} for note in notes_data]
        }
        return jsonify(response), 200
    except Exception as e:
        return format_error(str(e), 400)


# -------------------
# PATCH /note/<id> → Update a note by ID
# -------------------
@note_bp.route("/<note_id>", methods=["PATCH"])
def update_note(note_id):
    token = request.headers.get("Authorization")
    data = request.json or {}
    if not data.get("note") or not data.get("title"):
        return format_error("Title and Note are required to update.", 400)

    user_id, error = get_user_from_token(token)
    if error:
        return error

    try:
        note_resp = supabase.table("notes").select("*").eq("id", note_id).eq("user_id", user_id).execute()
        if not note_resp.data:
            return format_error("Note not found.", 404)

        supabase.table("notes").update({
            "title": data["title"],
            "note": data["note"]
        }).eq("id", note_id).eq("user_id", user_id).execute()
        return jsonify({"success": True, "code": 200}), 200
    except Exception as e:
        return format_error(str(e), 400)


# -------------------
# DELETE /note/<id> → Delete a note by ID
# -------------------
@note_bp.route("/<note_id>", methods=["DELETE"])
def delete_note(note_id):
    token = request.headers.get("Authorization")
    user_id, error = get_user_from_token(token)
    if error:
        return error

    try:
        note_resp = supabase.table("notes").select("*").eq("id", note_id).eq("user_id", user_id).execute()
        if not note_resp.data:
            return format_error("Note not found.", 404)

        supabase.table("notes").delete().eq("id", note_id).eq("user_id", user_id).execute()
        return jsonify({"success": True, "code": 200}), 200
    except Exception as e:
        return format_error(str(e), 400)
