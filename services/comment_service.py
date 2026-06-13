from domain.entities import Comment
from domain.repositories import CommentRepo, IssueRepo, ProjectRepo


class CommentServiceException(Exception):
    pass


class CommentNotFoundError(CommentServiceException):
    pass


class CommentPermissionError(CommentServiceException):
    pass


class CommentService:
    def __init__(self, comment_repo: CommentRepo, issue_repo: IssueRepo, project_repo: ProjectRepo):
        self.comment_repo = comment_repo
        self.issue_repo = issue_repo
        self.project_repo = project_repo

    # mirrors IssueService._assert_project_owned, but also checks the issue belongs to the project
    def _assert_issue_owned(self, user_id: int, project_id: int, issue_id: int) -> None:
        project = self.project_repo.get_by_id(project_id)

        if project is None:
            raise CommentNotFoundError("project not found")

        if project.user_id != user_id:
            raise CommentPermissionError("you don't own this project")

        issue = self.issue_repo.get_by_id(issue_id)

        if issue is None or issue.project_id != project_id:
            raise CommentNotFoundError("issue not found")

    def create(self, user_id: int, project_id: int, issue_id: int, body: str) -> Comment:
        self._assert_issue_owned(user_id, project_id, issue_id)

        # TODO: validate body length / strip whitespace
        comment = Comment(id=None, issue_id=issue_id, user_id=user_id, body=body)
        return self.comment_repo.add(comment)

    def list_for_issue(self, user_id: int, project_id: int, issue_id: int) -> list[Comment]:
        self._assert_issue_owned(user_id, project_id, issue_id)

        return self.comment_repo.list_by_issue(issue_id)

    def get_owned(self, user_id: int, project_id: int, issue_id: int, comment_id: int) -> Comment:
        self._assert_issue_owned(user_id, project_id, issue_id)

        comment = self.comment_repo.get_by_id(comment_id)

        if comment is None or comment.issue_id != issue_id:
            raise CommentNotFoundError("comment not found")

        return comment

    # only the comment's author can edit/delete it
    def _assert_comment_author(self, user_id: int, comment: Comment) -> None:
        if comment.user_id != user_id:
            raise CommentPermissionError("you don't own this comment")

    def update(self, user_id: int, project_id: int, issue_id: int, comment_id: int, body: str) -> Comment:
        comment = self.get_owned(user_id, project_id, issue_id, comment_id)
        self._assert_comment_author(user_id, comment)

        comment.body = body
        return self.comment_repo.update(comment)

    def delete(self, user_id: int, project_id: int, issue_id: int, comment_id: int) -> None:
        comment = self.get_owned(user_id, project_id, issue_id, comment_id)
        self._assert_comment_author(user_id, comment)

        self.comment_repo.delete(comment.id)
