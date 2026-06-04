"""
Generates a valid signed Telegram initData string for local testing.

Usage:
    python scripts/make_init_data.py

Reads BOT_TOKEN from .env (or environment). Prints the initData string
that can be passed as {"init_data": "..."} to POST /auth/telegram.
"""
import hashlib
import hmac
import json
import os
import sys
import time
from urllib.parse import urlencode

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load .env manually so the script works without importing app.config
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not set. Add it to .env or export it.", file=sys.stderr)
    sys.exit(1)

user_payload = {
    "id": 123456789,
    "first_name": "Test",
    "last_name": "User",
    "username": "testuser",
    "language_code": "ru",
}

params = {
    "query_id": "AAHdF6IQAAAAAN0XohDhrOrc",
    "user": json.dumps(user_payload, separators=(",", ":")),
    "auth_date": str(int(time.time())),
}

data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))

secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
calc_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

params["hash"] = calc_hash

init_data = urlencode(params)
print(init_data)
