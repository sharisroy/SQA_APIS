
from flask import Flask
from routes.home_routes import home_bp
from routes.auth_routes import auth_bp
from routes.profile_routes import profile_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(home_bp)                 # for / and /home
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(profile_bp, url_prefix="/profile")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)







# from flask import Flask, request, jsonify
# from supabase import create_client, Client
# import os
# from dotenv import load_dotenv
# from datetime import datetime
# import pytz   # pip install pytz
#
# # Load environment variables
# load_dotenv()
#
# app = Flask(__name__)
#
# # Supabase connection
# url: str = os.getenv("SUPABASE_URL")
# key: str = os.getenv("SUPABASE_KEY")
# supabase: Client = create_client(url, key)
#
#
# # ---------------------- Utility: Timestamps ---------------------- #
# def get_timestamps():
#     """Return both UTC and local server time with timezone."""
#     utc_now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
#     local_tz = pytz.timezone("Asia/Dhaka")  # Change to your preferred timezone
#     local_time = datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S %Z%z")
#     return {
#         "server_time_utc": utc_now,
#         "server_time_local": local_time
#     }
#
#
# # ---------------------- HOME ENDPOINT ---------------------- #
# @app.route("/")
# @app.route("/home")
# def home():
#     response_data = {
#         "success": True,
#         "code": 200,
#         "message": "The Home API endpoint is responding successfully.",
#         "details": {
#             "description": "Welcome to the API project. This is your first API response.",
#             "note": "The project is designed to help you practice both manual and automated API testing.",
#             "next_steps": [
#                 "Signup → Create a new account using name, phone, email, and password.",
#                 "Login → Authenticate with email and password to receive an access token.",
#                 "Profile → Use the access token to retrieve your profile details."
#             ]
#         },
#         "timestamps": get_timestamps()
#     }
#     return jsonify(response_data), 200
#
#
# # ---------------------- SIGNUP ENDPOINT ---------------------- #
# @app.route("/signup", methods=["POST"])
# def signup():
#     data = request.json or {}
#     name = data.get("name")
#     email = data.get("email")
#     password = data.get("password")
#     phone = data.get("phone")
#
#     if not name or not email or not phone or not password:
#         return jsonify({
#             "success": False,
#             "code": 400,
#             "message": "Missing required fields.",
#             "required_fields": ["name", "email", "phone", "password"],
#             "timestamps": get_timestamps()
#         }), 400
#
#     try:
#         auth_response = supabase.auth.sign_up({
#             "email": email,
#             "password": password,
#             "options": {
#                 "data": {
#                     "name": name,
#                     "phone": phone
#                 }
#             }
#         })
#
#         user = auth_response.user
#
#         response_data = {
#             "success": True,
#             "code": 201,
#             "message": "User registration successful.",
#             "user": {
#                 "email": user.email,
#                 "name": user.user_metadata.get("name") if user and user.user_metadata else None,
#                 "phone": user.user_metadata.get("phone") if user and user.user_metadata else None
#             },
#             "timestamps": get_timestamps()
#         }
#         return jsonify(response_data), 201
#
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "code": 400,
#             "message": "User registration failed.",
#             "error": str(e),
#             "timestamps": get_timestamps()
#         }), 400
#
#
# # ---------------------- LOGIN ENDPOINT ---------------------- #
# @app.route("/login", methods=["POST"])
# def login():
#     data = request.json or {}
#     email = data.get("email")
#     password = data.get("password")
#
#     if not email or not password:
#         return jsonify({
#             "success": False,
#             "code": 400,
#             "message": "Email and password are required.",
#             "timestamps": get_timestamps()
#         }), 400
#
#     try:
#         auth_response = supabase.auth.sign_in_with_password({
#             "email": email,
#             "password": password
#         })
#
#         session = auth_response.session
#         user = auth_response.user
#
#         response_data = {
#             "success": True,
#             "code": 200,
#             "message": "Login successful.",
#             "user": {
#                 "email": user.email if user else None,
#                 "name": user.user_metadata.get("name") if user and user.user_metadata else None,
#                 "phone": user.user_metadata.get("phone") if user and user.user_metadata else None,
#             },
#             "auth": {
#                 "access_token": session.access_token if session else None,
#                 "expires_at": session.expires_at if session else None
#             },
#             "timestamps": get_timestamps()
#         }
#         return jsonify(response_data), 200
#
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "code": 401,
#             "message": "Login failed. Invalid email or password.",
#             "error": str(e),
#             "timestamps": get_timestamps()
#         }), 401
#
#
# # ---------------------- PROFILE ENDPOINT ---------------------- #
# @app.route("/me", methods=["GET"])
# def profile():
#     token = request.headers.get("Authorization")
#
#     if not token:
#         return jsonify({
#             "success": False,
#             "code": 401,
#             "message": "Authorization token is required.",
#             "timestamps": get_timestamps()
#         }), 401
#
#     try:
#         # Remove Bearer prefix if present
#         if token.startswith("Bearer "):
#             token = token.split(" ")[1]
#
#         # Verify token with Supabase
#         user_response = supabase.auth.get_user(token)
#         if not user_response or not user_response.user:
#             return jsonify({
#                 "success": False,
#                 "code": 401,
#                 "message": "Invalid or expired token.",
#                 "timestamps": get_timestamps()
#             }), 401
#
#         user = user_response.user
#         response_data = {
#             "success": True,
#             "code": 200,
#             "message": "Profile details retrieved successfully.",
#             "user": {
#                 "email": user.email,
#                 "name": user.user_metadata.get("name") if user.user_metadata else None,
#                 "phone": user.user_metadata.get("phone") if user.user_metadata else None
#             },
#             "timestamps": get_timestamps()
#         }
#         return jsonify(response_data), 200
#
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "code": 400,
#             "message": "Failed to retrieve profile details.",
#             "error": str(e),
#             "timestamps": get_timestamps()
#         }), 400
#
#
# # ---------------------- RUN APP ---------------------- #
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
