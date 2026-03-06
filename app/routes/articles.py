"""Article API routes."""
from sqlalchemy import or_

from flask import Blueprint
from flasgger import swag_from
from flask_pydantic import validate

from app.models import Article
from app.schemas import ArticleId, ArticleQueryParams, ArticleResponse, ArticlesResponse, Pagination, ErrorResponse
from app.api_spec import SWAGGER_ARTICLE, SWAGGER_ARTICLES
from app.auth import require_token
articles_bp = Blueprint("articles", __name__)


def _pages_after_offset(total, offset, limit):
    remaining = max(0, total - offset)
    return (remaining + limit - 1) // limit if limit and remaining else 0


def _filter_articles_query(q_filter, filter_by):
    query = Article.query
    if not (q_filter and q_filter.strip()):
        return query
    term = q_filter.strip()
    if filter_by == "title":
        query = query.filter(Article.title.icontains(term, autoescape=True))
    elif filter_by == "description":
        query = query.filter(Article.description.icontains(term, autoescape=True))
    else:
        query = query.filter(or_(
            Article.title.icontains(term, autoescape=True),
            Article.description.icontains(term, autoescape=True),
        ))
    return query


@articles_bp.route("/article")
@swag_from(SWAGGER_ARTICLE)
@require_token
@validate()
def get_article(query: ArticleId):
    article = Article.query.get(query.id)
    if article is None:
        return ErrorResponse(error="Article not found").model_dump(), 404
    return ArticleResponse.from_model(article).model_dump(), 200


@articles_bp.route("/articles")
@swag_from(SWAGGER_ARTICLES)
@require_token
@validate()

def list_articles(query: ArticleQueryParams):
    page, limit_param, offset_param = query.page, query.limit, query.offset
    cursor_param = query.cursor
    filtered = _filter_articles_query(query.q, query.filter_by)
    total = filtered.count()
    base_query = filtered.with_entities(Article.id, Article.title).order_by(Article.id)
    rows, pagination = [], Pagination()

    if cursor_param is not None:
        q = base_query.filter(Article.id > cursor_param)
        if limit_param is not None:
            rows = q.limit(limit_param).all()
            next_cursor = rows[-1][0] if len(rows) == limit_param else None
            pagination = Pagination(cursor=cursor_param, limit=limit_param, next_cursor=next_cursor, returned=len(rows))
        else:
            rows = q.all()
            pagination = Pagination(cursor=cursor_param, returned=len(rows))
        return ArticlesResponse.from_rows(rows, pagination).model_dump(exclude_none=True), 200

    if offset_param is not None:
        if limit_param is not None:
            skip = offset_param + (page - 1) * limit_param
            rows = base_query.offset(skip).limit(limit_param).all()
            pages = _pages_after_offset(total, offset_param, limit_param)
            pagination = Pagination(
                page=page, limit=limit_param, pages=pages, returned=len(rows),
            )
        elif page > 1:
            pagination = Pagination(
                page=page, pages=1, returned=0, limit=total
            )
        else:
            rows = base_query.offset(offset_param).all()
            pagination = Pagination(
                page=1, pages=1, returned=len(rows), limit=len(rows),
            )
    elif limit_param is None:
        if page > 1:
            pagination = Pagination(page=page, pages=1, returned=0, limit=total)
        else:
            rows = base_query.all()
            pagination = Pagination(page=1, limit=total, pages=1, returned=len(rows))
    else:
        skip = (page - 1) * limit_param
        rows = base_query.offset(skip).limit(limit_param).all()
        pages = (total + limit_param - 1) // limit_param if total else 0
        pagination = Pagination(
            page=page, limit=limit_param,
            pages=pages, returned=len(rows),
        )

    return ArticlesResponse.from_rows(rows, pagination).model_dump(exclude_none=True), 200
