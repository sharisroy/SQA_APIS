
from flask import Flask
from routes.home_routes import home_bp
from routes.auth_routes import auth_bp
from routes.profile_routes import profile_bp
from routes.note_routes import note_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(home_bp)                 # for / and /home
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(profile_bp, url_prefix="/profile")

app.register_blueprint(note_bp, url_prefix="/note")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

