from domain.entities import Issue, Status, Priority
from domain.repositories import IssueRepo, ProjectRepo


class IssueServiceException(Exception):
    pass


class IssueNotFoundError(IssueServiceException):
    pass


class IssuePermissionError(IssueServiceException):
    pass


class InvalidStatusTransitionError(IssueServiceException):
    pass


class IssueService:
    def __init__(self, issue_repo: IssueRepo, project_repo: ProjectRepo):
        self.issue_repo = issue_repo
        self.project_repo = project_repo

    # raises ProjectNotFoundError/ProjectPermissionError-equivalent checks here
    # TODO: consider importing those exceptions instead of duplicating logic
    def _assert_project_owned(self, user_id: int, project_id: int) -> None:
        project = self.project_repo.get_by_id(project_id)

        if project is None:
            raise IssueNotFoundError("project not found")

        if project.user_id != user_id:
            raise IssuePermissionError("you don't own this project")

    def create(
        self, user_id: int, project_id: int,
        title: str, description: str | None,
        priority: str | None = None
    ) -> Issue:
        self._assert_project_owned(user_id, project_id)

        # TODO: validate title length / strip whitespace
        if priority is None:
            priority = Priority.MEDIUM.value
        elif priority not in Priority.values():
            raise IssueServiceException(f"invalid priority: {priority}")

        issue = Issue(
            id=None, project_id=project_id, title=title,
            description=description, status=Status.TODO.value, priority=priority
        )
        return self.issue_repo.add(issue)

    def list_for_project(
        self, user_id: int, project_id: int,
        status: str | None = None, priority: str | None = None
    ) -> list[Issue]:
        self._assert_project_owned(user_id, project_id)

        return self.issue_repo.list_by_project(project_id, status, priority)

    def get_owned(self, user_id: int, project_id: int, issue_id: int) -> Issue:
        self._assert_project_owned(user_id, project_id)

        issue = self.issue_repo.get_by_id(issue_id)

        if issue is None or issue.project_id != project_id:
            raise IssueNotFoundError("issue not found")

        return issue

    def update(
        self, user_id: int, project_id: int, issue_id: int,
        title: str, description: str | None,
        status: str | None, priority: str | None
    ) -> Issue:
        issue = self.get_owned(user_id, project_id, issue_id)

        issue.title = title
        issue.description = description

        if priority is not None:
            if priority not in Priority.values():
                raise IssueServiceException(f"invalid priority: {priority}")
            issue.priority = priority

        if status is not None:
            if status not in Status.values():
                raise IssueServiceException(f"invalid status: {status}")

            if not issue.can_transition_to(status):
                raise InvalidStatusTransitionError(
                    f"cannot transition from '{issue.status}' to '{status}'"
                )

            issue.status = status

        return self.issue_repo.update(issue)

    def delete(self, user_id: int, project_id: int, issue_id: int) -> None:
        issue = self.get_owned(user_id, project_id, issue_id)
        self.issue_repo.delete(issue.id)
