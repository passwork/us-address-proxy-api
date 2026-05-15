# US Address Proxy Service

A backend service built with FastAPI that provides user authentication and proxies US address generation from third-party data sources.

## Features

- **User Authentication** — Token-based login with bcrypt password hashing and Redis session storage
- **Request Authorization** — Global middleware with configurable whitelist support
- **US Address Proxy** — Async proxy to third-party US address generation API with fallback handling
- **Structured API Documentation** — Complete Markdown API docs for local testing

## Tech Stack

- **FastAPI** — Async Python web framework
- **PostgreSQL** — Persistent data storage
- **Redis** — Token session cache
- **SQLAlchemy 2.0** — Async ORM with Alembic migrations
- **httpx** — Async HTTP client for external API calls
- **pytest** — TDD test suite with async support

## Project Structure

```
.
├── app/                    # Application source code
│   ├── api/                # Route handlers
│   ├── core/               # Security, whitelist, exceptions
│   ├── services/           # Business logic & external API calls
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic DTOs
│   ├── database.py         # Async DB engine & session
│   ├── deps.py             # Dependency injections
│   └── main.py             # FastAPI app entry
├── alembic/                # Database migrations
├── scripts/                # Seed & utility scripts
├── tests/                  # TDD test suite
├── docs/                   # Requirement & planning docs
├── requirements.txt
├── pytest.ini
└── README.md
```

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/passwork/us-address-proxy-api.git
cd us-address-proxy-api

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your DB / Redis connection info

# 5. Run database migrations
alembic upgrade head

# 6. Seed test user
python scripts/init_db.py

# 7. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 8. Visit API docs
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## Testing

```bash
# Run unit tests (no external network required)
pytest -m unit -v

# Run integration tests (requires external API access)
pytest -m integration -v

# Run all tests
pytest -v
```

## API Overview

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/auth/login` | POST | No | User login, returns token |
| `/api/v1/address/generate` | GET | Yes | Generate US address via proxy |
| `/docs` | GET | No | Swagger UI (whitelist) |

See [`docs/api.md`](docs/api.md) for detailed API documentation.

## License

MIT
