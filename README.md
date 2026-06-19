# Python Issues Tracker API

A RESTful issue-tracking backend built with Flask and SQLite — a self-contained mini Jira/Linear clone
exposing JSON endpoints for managing projects, issues, and comments with JWT-based authentication.
The project was used as a learning exercise to practice layered backend architecture (DDD/MVC),
ownership-based authorization, domain-enforced state transitions, and both unit and integration testing,
all without any external infrastructure dependencies.

> [!WARNING]
> **This project's initial codebase and this documentation were generated with AI assistance.**
> The developer used AI to accelerate the scaffold and avoid boilerplate, but is fully aware of the
> trade-offs: the code has not been audited for security, the test coverage is not production-grade,
> and several design decisions may not reflect best practices. The intent is to rewrite this from
> scratch using the generated version as a reference, understanding every layer before it is committed.
> Do not treat this as production-ready software.

---

## How It Was Built

**Stack:** Python 3, Flask, SQLite3 (via the standard `sqlite3` module), PyJWT, passlib/bcrypt, pytest, Make

**Architecture:** The project follows a DDD-inspired layered structure — `domain/` holds pure entities and
value objects with no framework imports; `services/` orchestrates business rules and raises domain
exceptions; `infra/` owns all SQL and I/O; `api/` contains thin Flask blueprints that parse requests,
delegate to services, and return JSON. `app.py` acts as the application factory.

**What this project covers, and what a rewrite should internalize:**

- Structuring a Flask project without the default `app/` layout, keeping layers flat and explicit
- Writing domain entities as plain dataclasses with no ORM dependency
- Enforcing business rules at the domain level (e.g. status transitions: `todo → doing → done` only)
- Implementing JWT auth from scratch: hashing passwords with bcrypt, signing/verifying tokens with PyJWT
- Writing a `@jwt_required` decorator that injects `g.user_id` into the request context
- Using `sqlite3.Row` for dict-like DB access without an ORM
- Applying ownership checks consistently across all resource layers (projects, issues, comments)
- Organizing pytest with `unit/` and `integration/` splits and a `conftest.py` fixture for a temp DB
- Writing a `Makefile` as a simple build system (`run`, `test`, `db/init`, `clean`)
- Structuring a `Dockerfile` and `docker-compose.yml` for later deployment without running them locally

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/kevinmarquesp/pyissues-api.git
cd pyissues-api

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
make install

# 4. Copy and configure environment variables
cp .env.example .env
# Edit .env and set at minimum:
#   SECRET_KEY=your-secret-key-here
#   DB_PATH=db.sqlite3

# 5. Initialize the database schema
make db/init

# 6. Start the development server
make run
```

The API will be available at `http://localhost:5000`.

---

## Testing

```bash
# Run the full test suite (unit + integration)
make test

# Run only unit tests
.venv/bin/pytest tests/unit/ -v

# Run only integration tests
.venv/bin/pytest tests/integration/ -v
```

Integration tests spin up a temporary in-memory SQLite database via the `conftest.py` fixture —
no manual setup required.

### Manual / smoke testing (requires `curl` and `jq`)

A Bash smoke-test script is included at `tests/smoke/smoke.sh`. It covers auth, full CRUD lifecycles,
ownership enforcement, and invalid state transitions.

```bash
# List available test scenarios
./smoke.sh --list

# Run all smoke tests against the local server
./smoke.sh --all

# Run a single scenario
./smoke.sh test_issue_full_lifecycle
```

> The server must be running (`make run`) before executing smoke tests.

---

## API Overview

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | — | Create a new user account |
| `POST` | `/auth/login` | — | Authenticate and receive a JWT |
| `GET` | `/health` | — | Database connectivity check |
| `GET/POST` | `/projects` | ✓ | List or create projects |
| `GET/PUT/DELETE` | `/projects/<id>` | ✓ | Read, update, or delete a project |
| `GET/POST` | `/projects/<id>/issues` | ✓ | List or create issues (supports `?status=` and `?priority=` filters) |
| `GET/PUT/DELETE` | `/projects/<id>/issues/<id>` | ✓ | Read, update, or delete an issue |
| `GET/POST` | `/projects/<id>/issues/<id>/comments` | ✓ | List or create comments |
| `GET/PUT/DELETE` | `/projects/<id>/issues/<id>/comments/<id>` | ✓ | Read, update, or delete a comment |

All protected endpoints require an `Authorization: Bearer <token>` header.

---

## See Also

- [Flask documentation](https://flask.palletsprojects.com/) — application factory pattern, Blueprints, `flask.g`
- [PyJWT](https://pyjwt.readthedocs.io/) — JWT encoding/decoding used in `services/auth_service.py`
- [passlib](https://passlib.readthedocs.io/) — bcrypt password hashing
- [pytest fixtures](https://docs.pytest.org/en/stable/reference/fixtures.html) — how `conftest.py` provides the test client and temp DB
- [Domain-Driven Design reference](https://martinfowler.com/bliki/DomainDrivenDesign.html) — the layering philosophy this project attempts to follow
