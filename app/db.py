"""Database setup, and seed utilities."""
import csv
import os

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# CSV at project root: app/../data/articles.csv
DEFAULT_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "articles.csv")


def init_app(app):
    app.config.setdefault(
        "SQLALCHEMY_DATABASE_URI",
        os.environ.get("DATABASE_URL", "mysql+pymysql://root:password@localhost/flask_app"),
    )
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    db.init_app(app)


def load_articles_from_csv(path=None):
    path = path or os.environ.get("SEED_CSV", DEFAULT_CSV_PATH)
    if not os.path.isfile(path):
        return None
    articles = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = (row.get("title") or "").strip()
            if title:
                articles.append({"title": title, "description": (row.get("description") or "").strip()})
    return articles if articles else None


def seed_db(csv_path=None, app=None):
    """Insert dummy articles into the database from CSV."""
    from flask import current_app
    from app.models import Article

    app = app or current_app
    with app.app_context():
        existing = Article.query.count()
        if existing > 0:
            print(f"Found {existing} existing article(s). Skipping seed (database not empty).")
            return
        data = load_articles_from_csv(csv_path)
        for row in data:
            article = Article(title=row["title"], description=row.get("description") or "")
            db.session.add(article)
        db.session.commit()
        print(f"Inserted {len(data)} dummy articles.")