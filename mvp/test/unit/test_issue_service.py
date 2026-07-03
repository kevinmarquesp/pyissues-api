import pytest

from domain.entities import Project, Status, Priority
from services.issue_service import (
    IssueService,
    IssueNotFoundError,
    IssuePermissionError,
    InvalidStatusTransitionError,
    IssueServiceException,
)
from test.unit.fakes import FakeIssueRepo, FakeProjectRepo


@pytest.fixture
def project_repo():
    return FakeProjectRepo()


@pytest.fixture
def issue_repo():
    return FakeIssueRepo()


@pytest.fixture
def service(issue_repo, project_repo):
    return IssueService(issue_repo, project_repo)


@pytest.fixture
def owned_project(project_repo):
    project = Project(id=None, user_id=1, name="Owned project", description=None)
    return project_repo.add(project)


def test_create_issue_for_owned_project(service, owned_project):
    issue = service.create(user_id=1, project_id=owned_project.id, title="Fix bug", description=None)

    assert issue.id is not None
    assert issue.project_id == owned_project.id
    assert issue.status == Status.TODO.value
    assert issue.priority == Priority.MEDIUM.value


def test_create_issue_rejects_invalid_priority(service, owned_project):
    with pytest.raises(IssueServiceException):
        service.create(user_id=1, project_id=owned_project.id, title="x", description=None, priority="urgent")


def test_create_issue_for_nonexistent_project(service):
    with pytest.raises(IssueNotFoundError):
        service.create(user_id=1, project_id=999, title="x", description=None)


def test_create_issue_for_project_owned_by_someone_else(service, owned_project):
    with pytest.raises(IssuePermissionError):
        service.create(user_id=2, project_id=owned_project.id, title="x", description=None)


def test_list_for_project_filters_by_status(service, owned_project):
    service.create(user_id=1, project_id=owned_project.id, title="A", description=None)
    second = service.create(user_id=1, project_id=owned_project.id, title="B", description=None)

    service.update(
        user_id=1, project_id=owned_project.id, issue_id=second.id,
        title="B", description=None, status=Status.DOING.value, priority=None
    )

    todo_issues = service.list_for_project(user_id=1, project_id=owned_project.id, status=Status.TODO.value)
    doing_issues = service.list_for_project(user_id=1, project_id=owned_project.id, status=Status.DOING.value)

    assert len(todo_issues) == 1
    assert len(doing_issues) == 1
    assert doing_issues[0].id == second.id


def test_get_owned_raises_not_found_for_issue_in_another_project(service, owned_project, project_repo):
    other_project = project_repo.add(Project(id=None, user_id=1, name="Other", description=None))
    issue = service.create(user_id=1, project_id=other_project.id, title="x", description=None)

    with pytest.raises(IssueNotFoundError):
        service.get_owned(user_id=1, project_id=owned_project.id, issue_id=issue.id)


def test_update_valid_status_transition(service, owned_project):
    issue = service.create(user_id=1, project_id=owned_project.id, title="x", description=None)

    updated = service.update(
        user_id=1, project_id=owned_project.id, issue_id=issue.id,
        title="x", description="now in progress", status=Status.DOING.value, priority=None
    )

    assert updated.status == Status.DOING.value
    assert updated.description == "now in progress"


def test_update_invalid_status_transition_raises(service, owned_project):
    issue = service.create(user_id=1, project_id=owned_project.id, title="x", description=None)

    with pytest.raises(InvalidStatusTransitionError):
        service.update(
            user_id=1, project_id=owned_project.id, issue_id=issue.id,
            title="x", description=None, status=Status.DONE.value, priority=None
        )


def test_update_rejects_invalid_priority(service, owned_project):
    issue = service.create(user_id=1, project_id=owned_project.id, title="x", description=None)

    with pytest.raises(IssueServiceException):
        service.update(
            user_id=1, project_id=owned_project.id, issue_id=issue.id,
            title="x", description=None, status=None, priority="urgent"
        )


def test_delete_removes_issue(service, owned_project, issue_repo):
    issue = service.create(user_id=1, project_id=owned_project.id, title="x", description=None)
    service.delete(user_id=1, project_id=owned_project.id, issue_id=issue.id)

    assert issue_repo.get_by_id(issue.id) is None


def test_delete_issue_in_project_owned_by_someone_else(service, owned_project):
    issue = service.create(user_id=1, project_id=owned_project.id, title="x", description=None)

    with pytest.raises(IssuePermissionError):
        service.delete(user_id=2, project_id=owned_project.id, issue_id=issue.id)
