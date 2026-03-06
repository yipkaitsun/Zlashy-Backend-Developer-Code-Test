"""Simple token-based auth (random token, no JWT). Tokens stored in DB."""
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import request

from app.db import db
from app.models import Token
from app.schemas import ErrorResponse

DEMO_USERNAME = os.environ.get("AUTH_USERNAME", "auth")
DEMO_PASSWORD = os.environ.get("AUTH_PASSWORD", "auth")

TOKEN_EXPIRY_DAYS = 7


def _utcnow():
    return datetime.utcnow()


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def create_token(username: str) -> str:
    token_str = generate_token()
    expires_at = _utcnow() + timedelta(days=TOKEN_EXPIRY_DAYS)
    row = Token(token=token_str, expires_at=expires_at)
    db.session.add(row)
    db.session.commit()
    return token_str


def _get_valid_token(token: str) -> Token | None:
    """Return Token row if it exists and is not expired, else None. Expiry checked in DB."""
    return Token.query.filter_by(token=token).filter(Token.expires_at > _utcnow()).first()


def validate_token(token: str) -> bool:
    """Return True if token is valid and not expired, else False."""
    return _get_valid_token(token) is not None


def get_bearer_token() -> str | None:
    """Extract Bearer token from Authorization header."""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    return auth[7:].strip() or None



def require_token(f):
    """Decorator: require valid Bearer token (validate_token only); else 401."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_bearer_token()
        if not token:
            return ErrorResponse(error="Missing or invalid Authorization header").model_dump(), 401
        if not validate_token(token):
            return ErrorResponse(error="Invalid or expired token").model_dump(), 401
        return f(*args, **kwargs)
    return decorated


def revoke_token(token: str) -> bool:
    row = _get_valid_token(token)
    if row is None:
        return
    db.session.delete(row)
    db.session.commit()


def check_credentials(username: str, password: str) -> bool:
    return username == DEMO_USERNAME and password == DEMO_PASSWORD
