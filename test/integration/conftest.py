import os
import tempfile
import pytest

from app import create_app
from infra.db import get_db
from config import Config


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    class TestConfig(Config):
        SQLITE3_FILE = db_path
        FLASK_DEBUG = False
        JWT_SECRET = "test-secret"

    app = create_app(TestConfig)

    with app.app_context():
        db = get_db()
        with open("infra/sql/schema.sql") as f:
            db.executescript(f.read())
        db.commit()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_header(client):
    def _make(username="kevin", email="kevin@example.com", password="secret123"):
        client.post("/auth/register", json={
            "username": username, "email": email, "password": password
        })
        resp = client.post("/auth/login", json={
            "username": username, "password": password
        })
        token = resp.get_json()["token"]
        return {"Authorization": f"Bearer {token}"}

    return _make
