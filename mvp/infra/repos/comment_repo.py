import sqlite3

from domain.entities import Comment
from domain.repositories import CommentRepo


class SQLiteCommentRepo(CommentRepo):
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def get_by_id(self, comment_id: int) -> Comment | None:
        row = self.db.execute(
            "SELECT id, issue_id, user_id, body FROM comments WHERE id = ?",
            (comment_id,)
        ).fetchone()

        return self._row_to_comment(row)

    def list_by_issue(self, issue_id: int) -> list[Comment]:
        rows = self.db.execute(
            "SELECT id, issue_id, user_id, body FROM comments "
            "WHERE issue_id = ? ORDER BY id ASC",
            (issue_id,)
        ).fetchall()

        return [self._row_to_comment(row) for row in rows]

    def add(self, comment: Comment) -> Comment:
        cursor = self.db.execute(
            "INSERT INTO comments (issue_id, user_id, body) VALUES (?, ?, ?)",
            (comment.issue_id, comment.user_id, comment.body)
        )
        self.db.commit()

        comment.id = cursor.lastrowid
        return comment

    def update(self, comment: Comment) -> Comment:
        self.db.execute(
            "UPDATE comments SET body = ? WHERE id = ?",
            (comment.body, comment.id)
        )
        self.db.commit()

        return comment

    def delete(self, comment_id: int) -> None:
        self.db.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        self.db.commit()

    def _row_to_comment(self, row: sqlite3.Row | None) -> Comment | None:
        if row is None:
            return None

        return Comment(
            id=row["id"],
            issue_id=row["issue_id"],
            user_id=row["user_id"],
            body=row["body"],
        )
