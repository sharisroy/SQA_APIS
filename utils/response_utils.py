from flask import jsonify
from utils.time_utils import get_server_time, get_real_time


def success_response(message, data=None, code=200):
    """Standard success response structure."""
    response = {
        "success": True,
        "code": code,
        "message": message,
        "server_time": get_server_time(),
        "real_time": get_real_time(),
        "data": data or {}
    }
    return jsonify(response), code


def error_response(message, code=400):
    """Standard error response structure."""
    response = {
        "success": False,
        "code": code,
        "message": message,
        "server_time": get_server_time(),
        "real_time": get_real_time(),
    }
    return jsonify(response), code
