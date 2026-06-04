import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl

from fastapi import HTTPException, status

from app.config import settings


# --- Minimal HS256 JWT (avoids cryptography/cffi dependency) ---

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    pad = 4 - len(s) % 4
    return base64.urlsafe_b64decode(s + "=" * (pad % 4))


def _build_data_check_string(pairs: list[tuple[str, str]]) -> str:
    return "\n".join(f"{k}={v}" for k, v in sorted(pairs, key=lambda x: x[0]))


def validate_init_data(init_data: str) -> dict:
    pairs = parse_qsl(init_data, keep_blank_values=True)

    received_hash = dict(pairs).get("hash")
    if not received_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing hash")

    check_pairs = [(k, v) for k, v in pairs if k != "hash"]
    data_check_string = _build_data_check_string(check_pairs)

    secret_key = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
    calc_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calc_hash, received_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid hash")

    data = dict(check_pairs)

    auth_date = int(data.get("auth_date", 0))
    if time.time() - auth_date > 86400:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="initData expired")

    user_json = data.get("user")
    if not user_json:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user field")

    user_data = json.loads(user_json)
    return user_data


def create_access_token(user_id: int) -> str:
    expire = int((datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)).timestamp())
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url_encode(json.dumps({"sub": str(user_id), "exp": expire}).encode())
    signing_input = f"{header}.{payload}"
    sig = hmac.new(
        settings.JWT_SECRET.encode(),
        signing_input.encode(),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64url_encode(sig)}"


def decode_access_token(token: str) -> int:
    invalid = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        header, payload_b64, sig_b64 = token.split(".")
    except ValueError:
        raise invalid

    signing_input = f"{header}.{payload_b64}"
    expected_sig = hmac.new(
        settings.JWT_SECRET.encode(),
        signing_input.encode(),
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(expected_sig, _b64url_decode(sig_b64)):
        raise invalid

    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except Exception:
        raise invalid

    if payload.get("exp", 0) < time.time():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

    return int(payload["sub"])
