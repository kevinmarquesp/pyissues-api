import pytest
import jwt
from datetime import datetime, timedelta, timezone

from domain.entities import User
from domain.repositories import UserRepo
from services.auth_service import AuthService, AuthServiceException
from app import Config


class FakeUserRepo(UserRepo):
    def __init__(self):
        self._users = {}
        self._next_id = 1

    def get_by_id(self, user_id):
        return self._users.get(user_id)

    def get_by_username(self, username):
        return next((u for u in self._users.values() if u.username == username), None)

    def get_by_email(self, email):
        return next((u for u in self._users.values() if u.email == email), None)

    def add(self, user):
        if user.username in [u.username for u in self._users.values()]:
            raise Exception('Username already taken')

        if user.email in [u.email for u in self._users.values()]:
            raise Exception('Email already taken')

        user.id = self._next_id
        self._users[user.id] = user
        self._next_id += 1
        return user


@pytest.fixture
def repo():
    return FakeUserRepo()


@pytest.fixture
def auth_service(repo):
    return AuthService(repo)


def test_register_creates_user_with_hashed_password(auth_service):
    user = auth_service.register("kevin", "kevin@example.com", "secret123")

    assert user.id is not None
    assert user.username == "kevin"
    # password should NOT be stored in plain text
    assert user.password != "secret123"


def test_register_duplicate_username_raises(auth_service):
    auth_service.register("kevin", "kevin@example.com", "secret123")

    with pytest.raises(AuthServiceException):
        auth_service.register("kevin", "other@example.com", "anotherpass")


def test_login_success_returns_valid_token(auth_service):
    auth_service.register("kevin", "kevin@example.com", "secret123")

    token = auth_service.login("kevin", "secret123")
    payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])

    assert payload["username"] == "kevin"
    assert "exp" in payload


def test_login_with_wrong_password_raises(auth_service):
    auth_service.register("kevin", "kevin@example.com", "secret123")

    with pytest.raises(AuthServiceException):
        auth_service.login("kevin", "wrongpassword")


def test_login_with_unknown_username_raises(auth_service):
    with pytest.raises(AuthServiceException):
        auth_service.login("ghost", "whatever")


def test_decode_token_valid(auth_service):
    auth_service.register("kevin", "kevin@example.com", "secret123")
    token = auth_service.login("kevin", "secret123")

    payload = auth_service.decode_token(token)

    assert payload["username"] == "kevin"


def test_decode_expired_token_raises(auth_service):
    expired_payload = {
        "sub": "1",
        "username": "kevin",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
    }
    expired_token = jwt.encode(expired_payload, Config.JWT_SECRET, algorithm="HS256")

    with pytest.raises(AuthServiceException):
        auth_service.decode_token(expired_token)


def test_decode_garbage_token_raises(auth_service):
    with pytest.raises(AuthServiceException):
        auth_service.decode_token("not.a.valid.token")
