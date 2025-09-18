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
# POST /note → Add a note
# -------------------
@note_bp.route("/", methods=["POST"])
def add_note():
    token = request.headers.get("Authorization")
    data = request.json or {}

    if not token:
        return jsonify({"success": False, "code": 401, "error": "Missing Authorization header."}), 401
    if not data.get("note"):
        return jsonify({"success": False, "code": 400, "error": "Note is required."}), 400

    try:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        # Validate user
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            return jsonify({"success": False, "code": 401, "error": "Invalid or expired token."}), 401

        user_id = user_response.user.id
        note_text = data["note"]
        note_id = str(uuid.uuid4())  # generate unique id

        # Store note in Supabase table called "notes"
        supabase.table("notes").insert({"id": note_id, "user_id": user_id, "note": note_text}).execute()

        return jsonify({"success": True, "code": 200, "message": "Note added successfully.", "note_id": note_id}), 200

    except Exception as e:
        return jsonify({"success": False, "code": 400, "error": str(e)}), 400

# -------------------
# GET /note/<id> → Retrieve a note by ID
# -------------------
@note_bp.route("/<note_id>", methods=["GET"])
def get_note(note_id):
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"success": False, "code": 401, "error": "Missing Authorization header."}), 401

    try:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        # Validate user
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            return jsonify({"success": False, "code": 401, "error": "Invalid or expired token."}), 401

        user_id = user_response.user.id

        # Fetch note from Supabase
        note_resp = supabase.table("notes").select("*").eq("id", note_id).eq("user_id", user_id).execute()
        note_data = note_resp.data

        if not note_data or len(note_data) == 0:
            return jsonify({"success": False, "code": 404, "error": "Note not found."}), 404

        # Return first note
        note = note_data[0]
        return jsonify({"success": True, "code": 200, "note": {"id": note["id"], "note": note["note"]}}), 200

    except Exception as e:
        return jsonify({"success": False, "code": 400, "error": str(e)}), 400



# -------------------
# GET /note → Get all notes for the authenticated user
# -------------------
@note_bp.route("/", methods=["GET"])
def get_all_notes():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"success": False, "code": 401, "error": "Missing Authorization header."}), 401

    try:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        # Validate user
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            return jsonify({"success": False, "code": 401, "error": "Invalid or expired token."}), 401

        user_id = user_response.user.id

        # Fetch all notes for this user
        notes_resp = supabase.table("notes").select("*").eq("user_id", user_id).execute()
        notes_data = notes_resp.data

        return jsonify({
            "success": True,
            "code": 200,
            "notes": [{"id": note["id"], "note": note["note"]} for note in notes_data]
        }), 200

    except Exception as e:
        return jsonify({"success": False, "code": 400, "error": str(e)}), 400
