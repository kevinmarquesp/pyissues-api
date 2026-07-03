from abc import ABC, abstractmethod
from domain.entities import User
from domain.entities import Project
from domain.entities import Issue

class UserRepo(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def add(self, user: User) -> User: ...

class ProjectRepo(ABC):
    @abstractmethod
    def get_by_id(self, project_id: int) -> Project | None: ...

    @abstractmethod
    def list_by_user(self, user_id: int) -> list[Project]: ...

    @abstractmethod
    def add(self, project: Project) -> Project: ...

    @abstractmethod
    def update(self, project: Project) -> Project: ...

    @abstractmethod
    def delete(self, project_id: int) -> None: ...  # TODO: return deleted project

class IssueRepo(ABC):
    @abstractmethod
    def get_by_id(self, issue_id: int) -> Issue | None: ...

    @abstractmethod
    def list_by_project(
        self, project_id: int,
        status: str | None = None,
        priority: str | None = None
    ) -> list[Issue]: ...

    # TODO: manually pass args, to avoid None id attribute in Issue
    @abstractmethod
    def add(self, issue: Issue) -> Issue: ...

    @abstractmethod
    def update(self, issue: Issue) -> Issue: ...

    @abstractmethod
    def delete(self, issue_id: int) -> None: ...

from domain.entities import Comment

class CommentRepo(ABC):
    @abstractmethod
    def get_by_id(self, comment_id: int) -> Comment | None: ...

    @abstractmethod
    def list_by_issue(self, issue_id: int) -> list[Comment]: ...

    @abstractmethod
    def add(self, comment: Comment) -> Comment: ...

    @abstractmethod
    def update(self, comment: Comment) -> Comment: ...

    @abstractmethod
    def delete(self, comment_id: int) -> None: ...
