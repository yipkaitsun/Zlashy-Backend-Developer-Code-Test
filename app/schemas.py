"""API request/query/response schemas"""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ArticleQueryParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number (min 1)")
    limit: Optional[int] = Field(
        default=None, ge=1, description="Items per page (min 1 when provided)"
    )
    offset: Optional[int] = Field(
        default=None, ge=0, description="Number of results to skip (use with limit)"
    )
    q: Optional[str] = Field(default=None, description="Search term (filters by title/description)")
    filter_by: Optional[Literal["title", "description"]] = Field(
        default=None, description="Column to apply q search in (default: both)"
    )
    cursor: Optional[int] = Field(
        default=None, ge=0, description="Cursor-based pagination: return items after this article id (use with limit)"
    )


class ArticleId(BaseModel):
    id: int = Field(ge=1, description="Article ID")


# ── Response schemas ──


class ArticleDetail(BaseModel):
    id: int
    title: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ArticleSummary(BaseModel):
    id: int
    title: str


class ArticleResponse(BaseModel):
    article: ArticleDetail

    @classmethod
    def from_model(cls, article) -> "ArticleResponse":
        return cls(article=ArticleDetail.model_validate(article))


class Pagination(BaseModel):
    page: Optional[int] = None
    limit: Optional[int] = None
    pages: Optional[int] = None
    returned: Optional[int] = None
    cursor: Optional[int] = None
    next_cursor: Optional[int] = None


class ArticlesResponse(BaseModel):
    articles: List[ArticleSummary]
    pagination: Pagination

    @classmethod
    def from_rows(cls, rows, pagination: Pagination) -> "ArticlesResponse":
        return cls(
            articles=[ArticleSummary(id=r[0], title=r[1]) for r in rows],
            pagination=pagination,
        )


class LoginBody(BaseModel):
    """Request body for POST /auth/login."""
    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class LoginResponse(BaseModel):
    token: str


class LogoutResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    error: str
