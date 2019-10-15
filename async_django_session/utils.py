import json
import secrets
import string
from datetime import datetime, timezone

KEY_CHARS = string.ascii_lowercase + string.digits


def now_utc():
    return datetime.utcnow().replace(tzinfo=timezone.utc)


def new_session_key():
    return "".join(secrets.choice(KEY_CHARS) for i in range(32))


def json_dumps(obj):
    return json.dumps(obj, separators=(",", ":")).encode("latin-1")
