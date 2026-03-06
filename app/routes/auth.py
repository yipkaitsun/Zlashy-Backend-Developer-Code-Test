"""Auth API: login (random token), me, logout."""
from flask import Blueprint
from flasgger import swag_from
from flask_pydantic import validate

from app.auth import check_credentials, create_token, get_bearer_token, require_token, revoke_token
from app.schemas import LoginBody, LoginResponse, LogoutResponse, ErrorResponse
from app.api_spec import SWAGGER_LOGIN, SWAGGER_LOGOUT

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
@swag_from(SWAGGER_LOGIN)
@validate()
def login(body: LoginBody):
    if not check_credentials(body.username, body.password):
        return ErrorResponse(error="Invalid username or password").model_dump(), 401
    token = create_token(body.username)
    return LoginResponse(token=token).model_dump(), 200


@auth_bp.route("/logout", methods=["POST"])
@swag_from(SWAGGER_LOGOUT)
@require_token
def logout():
    token = get_bearer_token()
    revoke_token(token)
    return LogoutResponse(message="Logged out").model_dump(), 200
