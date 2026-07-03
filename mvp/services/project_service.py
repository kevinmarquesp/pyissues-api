from domain.entities import Project
from domain.repositories import ProjectRepo


class ProjectServiceException(Exception):
    pass


class ProjectNotFoundError(ProjectServiceException):
    pass


class ProjectPermissionError(ProjectServiceException):
    pass


class ProjectService:
    def __init__(self, project_repo: ProjectRepo):
        self.project_repo = project_repo

    def create(self, user_id: int, name: str, description: str | None) -> Project:
        # TODO: validate name length / strip whitespace
        project = Project(id=None, user_id=user_id, name=name, description=description)
        return self.project_repo.add(project)

    def list_for_user(self, user_id: int) -> list[Project]:
        return self.project_repo.list_by_user(user_id)

    def get_owned(self, user_id: int, project_id: int) -> Project:  # TODO: Maybe a is_owned() is better
        project = self.project_repo.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError("project not found")

        if project.user_id != user_id:
            raise ProjectPermissionError("you don't own this project")

        return project

    # TODO: specify that name and description will be updated with another separated object
    def update(self, user_id: int, project_id: int, name: str, description: str | None) -> Project:
        project = self.get_owned(user_id, project_id)

        project.name = name
        project.description = description

        return self.project_repo.update(project)

    # TODO: return the deleted project
    def delete(self, user_id: int, project_id: int) -> None:
        project = self.get_owned(user_id, project_id)
        self.project_repo.delete(project.id)
