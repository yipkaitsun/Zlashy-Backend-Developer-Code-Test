# Flask App

A minimal Flask web application with SQLAlchemy ORM and MySQL. API docs via Swagger UI.

## Setup with Docker (no virtual environment needed)

1. **Start the stack** (MySQL + Flask app):

   ```bash
   docker compose up -d --build
   ```

2. **Create tables and seed data** (run once after first start):

   ```bash
   docker compose exec web flask init-db
   ```

3. Open in your browser:

   - App: [http://127.0.0.1:5001](http://127.0.0.1:5001)
   - Swagger UI: [http://127.0.0.1:5001/apidocs/](http://127.0.0.1:5001/apidocs/)

The web app runs on port **5001** (MySQL on 3306). Connection to the database uses the container name `flask-app-mysql`; no local MySQL or virtual environment required.

## Endpoints

- `GET /api/article?id=...` – Single article (JSON)
- `GET /api/articles` – Articles list with pagination, offset, limit, search (JSON)
- `POST /api/auth/login` – Login to generate token
- `POST /api/auth/logout` – Logout to revoke token
- `GET /health` – Health check (JSON)
- `GET /apidocs/` – Swagger UI

## Run locally (optional)

If you prefer to run without Docker:

1. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Run MySQL (e.g. `docker compose up -d mysql`) or use an existing database. Set the URL if needed:

   ```bash
   export DATABASE_URL="mysql+pymysql://root:password@localhost/flask_app"
   ```

3. Create tables and seed, then run the app:

   ```bash
   flask --app run:app init-db
   python run.py
   ```

   App and Swagger will be at [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Config
- Demo username/password for auth is store in DockerFile
- If Run locally   
 ```bash
   export AUTH_USERNAME="username"
   export AUTH_PASSWORD="password"
 ```
default username/password = auth/auth

## Security & Validation

### Input Validation

Route parameters are declared as **Pydantic model annotations** (e.g. `query: ArticleId`, `body: LoginBody`). The `flask-pydantic` library reads these annotations and validates incoming request data automatically — type mismatches, missing required fields, or constraint violations (`ge=1`, `min_length=1`, `Literal[...]`) return a `400` error before route logic executes.

### SQL Injection Prevention

- All database access goes through **SQLAlchemy ORM**, which uses parameterised queries — user input is never interpolated into SQL strings.
- Text search uses SQLAlchemy's `.icontains(term, autoescape=True)`, which escapes LIKE wildcard characters (`%`, `_`) automatically so user input is treated as literal text.
- Pydantic enforces types at the boundary (e.g. `int` for IDs, page, offset, cursor), so invalid values are rejected before reaching any query.

### Authentication

- Token-based auth using `secrets.token_urlsafe` (cryptographically random, not JWT). Tokens are stored in the database with a 7-day expiry.
- The `@require_token` decorator extracts the `Bearer` token from the `Authorization` header and validates it against the database. Protected routes (`/article`, `/articles`, `/logout`) use this decorator.
- Login credentials are configured via environment variables (`AUTH_USERNAME`, `AUTH_PASSWORD`).

### Response Schemas

All API responses are serialised through Pydantic models (`ArticleResponse`, `ArticlesResponse`, `LoginResponse`, `LogoutResponse`, `ErrorResponse`, `Pagination`). The Swagger/OpenAPI specs are auto-generated from these same models via `pydantic_to_swagger_schema()`, so documentation always matches the actual response shape.