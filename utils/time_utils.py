from datetime import datetime
from zoneinfo import ZoneInfo


def get_server_time():
    """Returns the server's local time in UTC."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def get_real_time(timezone_str="Asia/Dhaka"):
    """Returns real time for a given timezone (default: Dhaka)."""
    try:
        tz = ZoneInfo(timezone_str)
        return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return "Invalid timezone"
