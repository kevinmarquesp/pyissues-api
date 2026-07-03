import sqlite3

from domain.entities import Issue
from domain.repositories import IssueRepo


class SQLiteIssueRepo(IssueRepo):
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def get_by_id(self, issue_id: int) -> Issue | None:
        row = self.db.execute(
            "SELECT id, project_id, title, description, status, priority "
            "FROM issues WHERE id = ?",
            (issue_id,)
        ).fetchone()

        return self._row_to_issue(row)

    def list_by_project(
        self, project_id: int,
        status: str | None = None,
        priority: str | None = None
    ) -> list[Issue]:
        query = (
            "SELECT id, project_id, title, description, status, priority "
            "FROM issues WHERE project_id = ?"
        )
        params: list = [project_id]

        if status is not None:
            query += " AND status = ?"
            params.append(status)

        if priority is not None:
            query += " AND priority = ?"
            params.append(priority)

        rows = self.db.execute(query, params).fetchall()
        return [self._row_to_issue(row) for row in rows]

    def add(self, issue: Issue) -> Issue:
        cursor = self.db.execute(
            "INSERT INTO issues (project_id, title, description, status, priority) "
            "VALUES (?, ?, ?, ?, ?)",
            (issue.project_id, issue.title, issue.description, issue.status, issue.priority)
        )
        self.db.commit()

        issue.id = cursor.lastrowid
        return issue

    def update(self, issue: Issue) -> Issue:
        self.db.execute(
            "UPDATE issues SET title = ?, description = ?, status = ?, priority = ? "
            "WHERE id = ?",
            (issue.title, issue.description, issue.status, issue.priority, issue.id)
        )
        self.db.commit()

        return issue

    def delete(self, issue_id: int) -> None:
        self.db.execute("DELETE FROM issues WHERE id = ?", (issue_id,))
        self.db.commit()

    def _row_to_issue(self, row: sqlite3.Row | None) -> Issue | None:
        if row is None:
            return None

        return Issue(
            id=row["id"],
            project_id=row["project_id"],
            title=row["title"],
            description=row["description"],
            status=row["status"],
            priority=row["priority"],
        )
