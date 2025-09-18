from flask import Blueprint
from utils.response_utils import success_response

# only url_prefix, no strict_slashes here
home_bp = Blueprint("home", __name__, url_prefix="")

@home_bp.route("/", methods=["GET"], strict_slashes=False)
@home_bp.route("/home", methods=["GET"], strict_slashes=False)
def home():
    data = {
        "description": "This is your first API response.",
        "note": "This project is designed to help you practice both manual and automated API testing.",
        "next_steps": [
            "Signup → Register with name, phone, email, and password to create a new account.",
            "Login → Authenticate using email and password to receive an access token.",
            "Profile → Retrieve your profile details using the provided access token."
        ]
    }
    return success_response("The Home API endpoint is working successfully.", data)
