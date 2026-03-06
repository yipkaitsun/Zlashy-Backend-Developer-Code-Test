"""Flask application factory."""
from flask import Flask
from flasgger import Swagger

from app.db import db, init_app as init_db
from app.api_spec import SWAGGER_TEMPLATE
from app.routes import register_blueprints


def create_app():
    app = Flask(__name__)
    init_db(app)
    Swagger(app, template=SWAGGER_TEMPLATE)
    register_blueprints(app)

    @app.cli.command("init-db")
    def init_db_command():
        from app.db import seed_db
        db.create_all()
        print("Tables created.")
        seed_db()

    return app
