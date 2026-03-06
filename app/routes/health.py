"""Health check route."""
from flask import Blueprint
from flasgger import swag_from

from app.api_spec import SWAGGER_HEALTH

health_bp = Blueprint("health", __name__)


@health_bp.route("/health")
@swag_from(SWAGGER_HEALTH)
def health():
    return {"status": "ok"}, 200
