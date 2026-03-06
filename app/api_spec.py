"""OpenAPI/Swagger spec definitions for Flasgger (@swag_from)."""
from pydantic import BaseModel

from app.schemas import (
    ArticleId, ArticleQueryParams, ArticleResponse, ArticlesResponse,
    LoginBody, LoginResponse, LogoutResponse, ErrorResponse,
)


def pydantic_to_swagger_schema(model: type[BaseModel]) -> dict:
    """Convert a Pydantic model to an OpenAPI 2.0 schema object."""
    json_schema = model.model_json_schema()
    defs = json_schema.get("$defs", {})

    def _resolve(node: dict) -> dict:
        if "$ref" in node:
            ref_name = node["$ref"].rsplit("/", 1)[-1]
            return _resolve(defs[ref_name])

        if "anyOf" in node:
            non_null = [s for s in node["anyOf"] if s.get("type") != "null"]
            base = _resolve(non_null[0]) if non_null else {"type": "string"}
            if "description" in node:
                base["description"] = node["description"]
            return base

        result: dict = {}
        if "type" in node:
            result["type"] = node["type"]
        if "description" in node:
            result["description"] = node["description"]
        if "example" in node:
            result["example"] = node["example"]
        if "enum" in node:
            result["enum"] = node["enum"]
        if "minimum" in node:
            result["minimum"] = node["minimum"]
        if "default" in node:
            result["default"] = node["default"]

        if "properties" in node:
            result["type"] = "object"
            result["properties"] = {
                k: _resolve(v) for k, v in node["properties"].items()
            }

        if "items" in node:
            result["items"] = _resolve(node["items"])

        return result

    return _resolve(json_schema)


def pydantic_to_swagger_params(model: type[BaseModel], location: str = "query"):
    if location == "body":
        return [{"in": "body", "name": "body", "required": True, "schema": pydantic_to_swagger_schema(model)}]
    schema = pydantic_to_swagger_schema(model)
    required = set(model.model_json_schema().get("required", []))
    params = []
    for name, prop in schema.get("properties", {}).items():
        p = {"name": name, "in": "query", **prop}
        if name in required:
            p["required"] = True
        params.append(p)
    return params


SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {"title": "Flask Articles API", "description": "Articles API with pagination and search", "version": "1.0"},
    "host": "",
    "basePath": "/",
    "schemes": ["http", "https"],
    "tags": [
        {"name": "articles", "description": "Article resources"},
        {"name": "health", "description": "Health check"},
        {"name": "auth", "description": "Authentication (random token, no JWT)"},
    ],
}

SCHEMA_ERROR = pydantic_to_swagger_schema(ErrorResponse)

AUTH_HEADER = {"in": "header", "name": "Authorization", "required": True, "type": "string", "description": "Bearer <token>"}

SWAGGER_ARTICLE = {
    "tags": ["articles"],
    "summary": "Get a single article by ID",
    "parameters": [AUTH_HEADER] + pydantic_to_swagger_params(ArticleId),
    "responses": {
        "200": {"description": "The article", "schema": pydantic_to_swagger_schema(ArticleResponse)},
        "401": {"description": "Missing or invalid token", "schema": SCHEMA_ERROR},
        "404": {"description": "Article not found", "schema": SCHEMA_ERROR},
    },
}

SWAGGER_ARTICLES = {
    "tags": ["articles"],
    "summary": "List articles with pagination and search",
    "parameters": [AUTH_HEADER] + pydantic_to_swagger_params(ArticleQueryParams),
    "responses": {
        "200": {"description": "Paginated list of articles", "schema": pydantic_to_swagger_schema(ArticlesResponse)},
        "401": {"description": "Missing or invalid token", "schema": SCHEMA_ERROR},
    },
}

SWAGGER_HEALTH = {
    "tags": ["health"],
    "summary": "Health check",
    "responses": {"200": {"description": "Service is healthy", "schema": {"type": "object", "properties": {"status": {"type": "string", "example": "ok"}}}}},
}

SWAGGER_LOGIN = {
    "tags": ["auth"],
    "summary": "Login and get a random token",
    "parameters": pydantic_to_swagger_params(LoginBody, location="body"),
    "responses": {
        "200": {"description": "Token issued", "schema": pydantic_to_swagger_schema(LoginResponse)},
        "401": {"description": "Invalid credentials", "schema": SCHEMA_ERROR},
    },
}

SWAGGER_LOGOUT = {
    "tags": ["auth"],
    "summary": "Logout (invalidate token)",
    "parameters": [AUTH_HEADER],
    "responses": {
        "200": {"description": "Token revoked", "schema": pydantic_to_swagger_schema(LogoutResponse)},
        "401": {"description": "Missing or invalid token", "schema": SCHEMA_ERROR},
    },
}
