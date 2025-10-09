# routes/note_routes.py
from flask import Blueprint, request, jsonify, Response
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime
import json

# -----------------------------
# 🔧 Setup
# -----------------------------
load_dotenv()
note_bp = Blueprint("note", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# -----------------------------
# ⚙️ Helper Functions
# -----------------------------
def format_error(message: str, code: int = 400):
    return jsonify({"code": code, "message": message}), code


def get_user_from_token(token: str):
    """Validate JWT token and return user object or error."""
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


# -----------------------------
# 📝 POST /note → Create Note
# -----------------------------
@note_bp.route("/", methods=["POST"])
def create_note():
    token = request.headers.get("Authorization")
    user, error = get_user_from_token(token)
    if error:
        return error

    data = request.json or {}
    title = data.get("title")
    note_text = data.get("note")

    if not title or not note_text:
        return format_error("Title and note are required.", 400)

    note_id = str(uuid.uuid4())
    try:
        supabase.table("notes").insert({
            "id": note_id,
            "user_id": user.id,
            "title": title,
            "note": note_text,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": None
        }).execute()

        response_data = {
            "code": 201,
            "message": "Note created successfully",
            "note": {"id": note_id, "title": title, "note": note_text}
        }

        return Response(json.dumps(response_data, indent=4), status=201, mimetype="application/json")
    except Exception as e:
        return format_error(f"Failed to create note: {str(e)}", 500)


# -----------------------------
# 📜 GET /note → List Notes with Pagination
# -----------------------------
@note_bp.route("/", methods=["GET"])
def list_notes():
    token = request.headers.get("Authorization")
    user, error = get_user_from_token(token)
    if error:
        return error

    try:
        # Pagination query params
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        offset = (page - 1) * per_page

        # Fetch total notes count
        total_resp = supabase.table("notes").select("*", count="exact").eq("user_id", user.id).execute()
        total_notes = total_resp.count or 0
        total_pages = (total_notes + per_page - 1) // per_page

        # Fetch notes with pagination, latest first
        resp = (
            supabase.table("notes")
            .select("*")
            .eq("user_id", user.id)
            .order("created_at", desc=True)
            .range(offset, offset + per_page - 1)
            .execute()
        )
        notes = resp.data or []

        response_data = {
            "code": 200,
            "message": "All notes retrieved successfully",
            "notes": notes,
            "meta": {
                "current_page": page,
                "per_page": per_page,
                "total": total_notes,
                "total_pages": total_pages
            }
        }

        return Response(json.dumps(response_data, indent=4), status=200, mimetype="application/json")

    except Exception as e:
        return format_error(f"Failed to list notes: {str(e)}", 500)


# -----------------------------
# 🔍 GET /note/<id> → Get Note by ID
# -----------------------------
@note_bp.route("/<note_id>", methods=["GET"])
def get_note(note_id):
    token = request.headers.get("Authorization")
    user, error = get_user_from_token(token)
    if error:
        return error

    try:
        resp = supabase.table("notes").select("*").eq("id", note_id).eq("user_id", user.id).execute()
        if not resp.data:
            return format_error("Note not found.", 404)

        note = resp.data[0]
        response_data = {
            "code": 200,
            "message": "Note retrieved successfully",
            "note": note
        }

        return Response(json.dumps(response_data, indent=4), status=200, mimetype="application/json")
    except Exception as e:
        return format_error(f"Failed to fetch note: {str(e)}", 500)


# -----------------------------
# ✏️ PATCH /note/<id> → Update Note
# -----------------------------
@note_bp.route("/<note_id>", methods=["PATCH"])
def update_note(note_id):
    token = request.headers.get("Authorization")
    user, error = get_user_from_token(token)
    if error:
        return error

    data = request.json or {}
    if not data.get("title") and not data.get("note"):
        return format_error("Title or note required to update.", 400)

    update_data = {}
    if "title" in data:
        update_data["title"] = data["title"]
    if "note" in data:
        update_data["note"] = data["note"]
    update_data["updated_at"] = datetime.utcnow().isoformat()

    try:
        resp = supabase.table("notes").update(update_data).eq("id", note_id).eq("user_id", user.id).execute()
        if not resp.data:
            return format_error("Note not found.", 404)

        response_data = {
            "code": 200,
            "message": "Note updated successfully",
            "note": resp.data[0]
        }

        return Response(json.dumps(response_data, indent=4), status=200, mimetype="application/json")
    except Exception as e:
        return format_error(f"Failed to update note: {str(e)}", 500)


# -----------------------------
# 🗑️ DELETE /note/<id> → Delete Note
# -----------------------------
@note_bp.route("/<note_id>", methods=["DELETE"])
def delete_note(note_id):
    token = request.headers.get("Authorization")
    user, error = get_user_from_token(token)
    if error:
        return error

    try:
        resp = supabase.table("notes").delete().eq("id", note_id).eq("user_id", user.id).execute()
        if not resp.data:
            return format_error("Note not found.", 404)

        response_data = {
            "code": 200,
            "message": "Note deleted successfully"
        }

        return Response(json.dumps(response_data, indent=4), status=200, mimetype="application/json")
    except Exception as e:
        return format_error(f"Failed to delete note: {str(e)}", 500)
