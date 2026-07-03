import sqlite3

from domain.entities import User
from domain.repositories import UserRepo


class SQLiteUserRepo(UserRepo):
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        row = self.db.execute(
            "SELECT id, username, email, password FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        return self._row_to_user(row)

    def get_by_username(self, username: str) -> User | None:
        row = self.db.execute(
            "SELECT id, username, email, password FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        return self._row_to_user(row)

    def get_by_email(self, email: str) -> User | None:
        row = self.db.execute(
            "SELECT id, username, email, password FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        return self._row_to_user(row)

    def add(self, user: User) -> User:
        cursor = self.db.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (user.username, user.email, user.password)
        )
        self.db.commit()

        user.id = cursor.lastrowid
        return user

    def _row_to_user(self, row: sqlite3.Row | None) -> User | None:
        if row is None:
            return None

        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            password=row["password"],
        )
