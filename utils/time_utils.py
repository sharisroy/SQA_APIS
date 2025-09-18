from datetime import datetime
import pytz

def get_server_time():
    """
    Returns current server time in UTC.
    """
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

def get_real_time(timezone="Asia/Dhaka"):
    """
    Returns current local time based on provided timezone.
    Default: Asia/Dhaka
    """
    try:
        tz = pytz.timezone(timezone)
        return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        # fallback in case timezone is invalid
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S Local")
