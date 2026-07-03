import sqlite3

from domain.entities import Project
from domain.repositories import ProjectRepo


class SQLiteProjectRepo(ProjectRepo):
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def get_by_id(self, project_id: int) -> Project | None:
        row = self.db.execute(
            "SELECT id, user_id, name, description FROM projects WHERE id = ?",
            (project_id,)
        ).fetchone()

        return self._row_to_project(row)

    def list_by_user(self, user_id: int) -> list[Project]:
        rows = self.db.execute(
            "SELECT id, user_id, name, description FROM projects WHERE user_id = ?",
            (user_id,)
        ).fetchall()

        return [self._row_to_project(row) for row in rows]

    def add(self, project: Project) -> Project:
        cursor = self.db.execute(
            "INSERT INTO projects (user_id, name, description) VALUES (?, ?, ?)",
            (project.user_id, project.name, project.description)
        )
        self.db.commit()

        project.id = cursor.lastrowid
        return project

    def update(self, project: Project) -> Project:
        self.db.execute(
            "UPDATE projects SET name = ?, description = ? WHERE id = ?",
            (project.name, project.description, project.id)
        )
        self.db.commit()

        return project

    def delete(self, project_id: int) -> None:
        self.db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.db.commit()

    def _row_to_project(self, row: sqlite3.Row | None) -> Project | None:
        if row is None:
            return None

        return Project(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            description=row["description"],
        )
