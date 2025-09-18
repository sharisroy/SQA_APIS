from flask import Blueprint, render_template

home_bp = Blueprint("home", __name__, url_prefix="")

# Serve the static HTML page on base URL
@home_bp.route("/", methods=["GET"], strict_slashes=False)
@home_bp.route("/home", methods=["GET"], strict_slashes=False)
def home():
    return render_template("index.html")
