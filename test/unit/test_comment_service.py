import pytest

from domain.entities import Comment, Issue, Project, Status, Priority
from domain.repositories import CommentRepo, IssueRepo, ProjectRepo
from services.comment_service import (
    CommentService,
    CommentNotFoundError,
    CommentPermissionError,
)


# --- fake in-memory repos, implementing the same interfaces as the SQLite ones ---

class FakeProjectRepo(ProjectRepo):
    def __init__(self):
        self._projects = {}

    def get_by_id(self, project_id):
        return self._projects.get(project_id)

    def list_by_user(self, user_id):
        return [p for p in self._projects.values() if p.user_id == user_id]

    def add(self, project):
        project.id = len(self._projects) + 1
        self._projects[project.id] = project
        return project

    def update(self, project):
        self._projects[project.id] = project
        return project

    def delete(self, project_id):
        self._projects.pop(project_id, None)


class FakeIssueRepo(IssueRepo):
    def __init__(self):
        self._issues = {}

    def get_by_id(self, issue_id):
        return self._issues.get(issue_id)

    def list_by_project(self, project_id, status=None, priority=None):
        return [i for i in self._issues.values() if i.project_id == project_id]

    def add(self, issue):
        issue.id = len(self._issues) + 1
        self._issues[issue.id] = issue
        return issue

    def update(self, issue):
        self._issues[issue.id] = issue
        return issue

    def delete(self, issue_id):
        self._issues.pop(issue_id, None)


class FakeCommentRepo(CommentRepo):
    def __init__(self):
        self._comments = {}

    def get_by_id(self, comment_id):
        return self._comments.get(comment_id)

    def list_by_issue(self, issue_id):
        return [c for c in self._comments.values() if c.issue_id == issue_id]

    def add(self, comment):
        comment.id = len(self._comments) + 1
        self._comments[comment.id] = comment
        return comment

    def update(self, comment):
        self._comments[comment.id] = comment
        return comment

    def delete(self, comment_id):
        self._comments.pop(comment_id, None)


# --- fixtures: a project (owned by user 1) with one issue already in it ---

@pytest.fixture
def project_repo():
    repo = FakeProjectRepo()
    repo.add(Project(id=None, user_id=1, name="Demo", description=None))
    return repo


@pytest.fixture
def issue_repo(project_repo):
    repo = FakeIssueRepo()
    project = project_repo.get_by_id(1)
    repo.add(Issue(
        id=None, project_id=project.id, title="Fix bug",
        description=None, status=Status.TODO.value, priority=Priority.MEDIUM.value,
    ))
    return repo


@pytest.fixture
def comment_repo():
    return FakeCommentRepo()


@pytest.fixture
def service(comment_repo, issue_repo, project_repo):
    return CommentService(comment_repo, issue_repo, project_repo)


# --- tests ---

def test_create_comment_success(service):
    comment = service.create(user_id=1, project_id=1, issue_id=1, body="looks good")

    assert comment.id is not None
    assert comment.issue_id == 1
    assert comment.user_id == 1
    assert comment.body == "looks good"


def test_create_comment_project_not_found(service):
    with pytest.raises(CommentNotFoundError):
        service.create(user_id=1, project_id=999, issue_id=1, body="hi")


def test_create_comment_wrong_project_owner(service):
    # user 2 doesn't own project 1
    with pytest.raises(CommentPermissionError):
        service.create(user_id=2, project_id=1, issue_id=1, body="not mine")


def test_create_comment_issue_not_in_project(service):
    with pytest.raises(CommentNotFoundError):
        service.create(user_id=1, project_id=1, issue_id=999, body="hi")


def test_list_for_issue_returns_only_that_issues_comments(service):
    service.create(user_id=1, project_id=1, issue_id=1, body="first")
    service.create(user_id=1, project_id=1, issue_id=1, body="second")

    comments = service.list_for_issue(user_id=1, project_id=1, issue_id=1)

    assert len(comments) == 2
    assert [c.body for c in comments] == ["first", "second"]


def test_get_owned_not_found_for_other_issue(service):
    comment = service.create(user_id=1, project_id=1, issue_id=1, body="hello")

    # comment exists, but we ask for it under a different (nonexistent) issue
    with pytest.raises(CommentNotFoundError):
        service.get_owned(user_id=1, project_id=1, issue_id=999, comment_id=comment.id)


def test_update_comment_success_by_author(service):
    comment = service.create(user_id=1, project_id=1, issue_id=1, body="original")

    updated = service.update(user_id=1, project_id=1, issue_id=1, comment_id=comment.id, body="edited")

    assert updated.body == "edited"


def test_update_comment_wrong_author_raises_permission_error(service):
    comment = service.create(user_id=1, project_id=1, issue_id=1, body="original")

    # only user 1 (author) can edit, even though user 1 also owns the project
    with pytest.raises(CommentPermissionError):
        service.update(user_id=2, project_id=1, issue_id=1, comment_id=comment.id, body="hacked")


def test_delete_comment_success_by_author(service, comment_repo):
    comment = service.create(user_id=1, project_id=1, issue_id=1, body="to delete")

    service.delete(user_id=1, project_id=1, issue_id=1, comment_id=comment.id)

    assert comment_repo.get_by_id(comment.id) is None


def test_delete_comment_wrong_author_raises_permission_error(service):
    comment = service.create(user_id=1, project_id=1, issue_id=1, body="protected")

    with pytest.raises(CommentPermissionError):
        service.delete(user_id=2, project_id=1, issue_id=1, comment_id=comment.id)
