# In app.py

from flask import Flask, request, jsonify, render_template
from routes.home_routes import home_bp
from routes.auth_routes import auth_bp
from routes.profile_routes import profile_bp
from routes.note_routes import note_bp
from routes.generate_payload import secure_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(home_bp)
@app.route("/secure_login")
def secure_login_page():
    return render_template("secure_login_generator.html")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(secure_bp, url_prefix="/secure")
app.register_blueprint(profile_bp, url_prefix="/profile")
app.register_blueprint(note_bp, url_prefix="/note")

# --- ADD A GLOBAL ERROR HANDLER ---
@app.errorhandler(400)
def bad_request(error):
    # This will now catch any 400 errors, including malformed requests
    # Log the full request body for debugging
    request_body = request.get_data(as_text=True)
    app.logger.error(f"400 Bad Request Error: {error.description}")
    app.logger.error(f"Received data: {request_body}")
    return jsonify({"success": False, "code": 400, "error": "Bad Request. The request body might be malformed or empty."}), 400
# ----------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)