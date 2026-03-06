"""Register all blueprints on the app."""
from app.routes.articles import articles_bp
from app.routes.auth import auth_bp
from app.routes.health import health_bp


def register_blueprints(app):
    app.register_blueprint(articles_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(health_bp)
