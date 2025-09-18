from flask import jsonify
from utils.time_utils import get_server_time, get_real_time

def success_response(message, data=None, code=200, timezone="Asia/Dhaka"):
    """
    Standard success JSON response with timestamps.
    """
    response = {
        "success": True,
        "code": code,
        "message": message,
        "data": data if data else {},
        "timestamps": {
            "server_time": get_server_time(),
            "real_time": get_real_time(timezone)
        }
    }
    return jsonify(response), code


def error_response(error_message, code=400, timezone="Asia/Dhaka"):
    """
    Standard error JSON response with timestamps.
    """
    response = {
        "success": False,
        "code": code,
        "error": error_message,
        "timestamps": {
            "server_time": get_server_time(),
            "real_time": get_real_time(timezone)
        }
    }
    return jsonify(response), code
