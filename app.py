# ============================================
# app.py — Main Flask Application Entry Point
# ============================================

from flask import Flask, request, jsonify, render_template
import logging
from routes.home_routes import home_bp
from routes.auth_routes import auth_bp
from routes.profile_routes import profile_bp
from routes.note_routes import note_bp
from routes.generate_payload import secure_bp


# -------------------
# Flask App Setup
# -------------------
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] in %(module)s: %(message)s",
)
app.logger.setLevel(logging.INFO)


# -------------------
# Blueprint Registration
# -------------------
app.register_blueprint(home_bp)
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(secure_bp, url_prefix="/secure")
app.register_blueprint(profile_bp, url_prefix="/profile")
app.register_blueprint(note_bp, url_prefix="/note")


# -------------------
# Route: Secure Login Page
# -------------------
@app.route("/secure_login")
def secure_login_page():
    """Renders the Secure Login Generator HTML page."""
    return render_template("secure_login_generator.html")


# -------------------
# Global Error Handlers
# -------------------
@app.errorhandler(400)
def handle_bad_request(error):
    """Handle malformed or invalid requests globally."""
    request_body = request.get_data(as_text=True)
    app.logger.error(f"400 Bad Request: {error.description if hasattr(error, 'description') else error}")
    app.logger.error(f"Received data: {request_body}")
    return (
        jsonify({
            "success": False,
            "code": 400,
            "error": "Bad Request. The request body might be malformed or empty."
        }),
        400,
    )


@app.errorhandler(401)
def handle_unauthorized(error):
    """Handle unauthorized access globally."""
    return jsonify({
        "success": False,
        "code": 401,
        "error": "Unauthorized. Please provide a valid token or credentials."
    }), 401


@app.errorhandler(404)
def handle_not_found(error):
    """Handle routes or resources not found."""
    return jsonify({
        "success": False,
        "code": 404,
        "error": "Resource not found."
    }), 404


@app.errorhandler(405)
def handle_method_not_allowed(error):
    """Handle invalid HTTP methods."""
    return jsonify({
        "success": False,
        "code": 405,
        "error": "Method Not Allowed. Please check the request method."
    }), 405


@app.errorhandler(500)
def handle_internal_error(error):
    """Handle any unhandled internal errors."""
    app.logger.error(f"500 Internal Server Error: {str(error)}")
    return jsonify({
        "success": False,
        "code": 500,
        "error": "Internal Server Error. Please try again later."
    }), 500


# -------------------
# Run the App
# -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
