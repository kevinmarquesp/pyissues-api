import pytest

from domain.entities import Project
from domain.repositories import ProjectRepo
from services.project_service import (
    ProjectService,
    ProjectNotFoundError,
    ProjectPermissionError,
)


class FakeProjectRepo(ProjectRepo):
    """In-memory repo so we can test ProjectService without SQLite."""

    def __init__(self):
        self._projects: dict[int, Project] = {}
        self._next_id = 1

    def get_by_id(self, project_id: int) -> Project | None:
        return self._projects.get(project_id)

    def list_by_user(self, user_id: int) -> list[Project]:
        return [p for p in self._projects.values() if p.user_id == user_id]

    def add(self, project: Project) -> Project:
        project.id = self._next_id
        self._next_id += 1
        self._projects[project.id] = project

        return project

    def update(self, project: Project) -> Project:
        self._projects[project.id] = project
        return project

    def delete(self, project_id: int) -> None:
        self._projects.pop(project_id, None)


@pytest.fixture
def repo():
    return FakeProjectRepo()


@pytest.fixture
def service(repo):
    return ProjectService(repo)


def test_create_assigns_id_and_owner(service):
    project = service.create(user_id=1, name="My project", description="desc")

    assert project.id is not None
    assert project.user_id == 1
    assert project.name == "My project"
    assert project.description == "desc"


def test_list_for_user_only_returns_own_projects(service):
    service.create(user_id=1, name="A", description=None)
    service.create(user_id=1, name="B", description=None)
    service.create(user_id=2, name="C", description=None)

    projects = service.list_for_user(1)

    assert len(projects) == 2
    assert all(p.user_id == 1 for p in projects)


def test_get_owned_returns_project_for_owner(service):
    created = service.create(user_id=1, name="A", description=None)

    fetched = service.get_owned(user_id=1, project_id=created.id)

    assert fetched.id == created.id


def test_get_owned_raises_not_found_for_unknown_id(service):
    with pytest.raises(ProjectNotFoundError):
        service.get_owned(user_id=1, project_id=999)


def test_get_owned_raises_permission_error_for_other_user(service):
    created = service.create(user_id=1, name="A", description=None)

    with pytest.raises(ProjectPermissionError):
        service.get_owned(user_id=2, project_id=created.id)


def test_update_changes_name_and_description(service):
    created = service.create(user_id=1, name="Old", description="old desc")

    updated = service.update(
        user_id=1,
        project_id=created.id,
        name="New",
        description="new desc",
    )

    assert updated.name == "New"
    assert updated.description == "new desc"


def test_update_raises_not_found_for_unknown_id(service):
    with pytest.raises(ProjectNotFoundError):
        service.update(user_id=1, project_id=999, name="New", description=None)


def test_update_raises_permission_error_for_other_user(service):
    created = service.create(user_id=1, name="A", description=None)

    with pytest.raises(ProjectPermissionError):
        service.update(user_id=2, project_id=created.id, name="New", description=None)


def test_delete_removes_project(service, repo):
    created = service.create(user_id=1, name="A", description=None)

    service.delete(user_id=1, project_id=created.id)

    assert repo.get_by_id(created.id) is None


def test_delete_raises_not_found_for_unknown_id(service):
    with pytest.raises(ProjectNotFoundError):
        service.delete(user_id=1, project_id=999)


def test_delete_raises_permission_error_for_other_user(service):
    created = service.create(user_id=1, name="A", description=None)

    with pytest.raises(ProjectPermissionError):
        service.delete(user_id=2, project_id=created.id)
