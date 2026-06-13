from domain.entities import Project, Issue
from domain.repositories import ProjectRepo, IssueRepo, UserRepo
from domain.entities import User


class FakeProjectRepo(ProjectRepo):
    def __init__(self):
        self._projects: dict[int, Project] = {}
        self._next_id = 1

    def get_by_id(self, project_id):
        return self._projects.get(project_id)

    def list_by_user(self, user_id):
        return [p for p in self._projects.values() if p.user_id == user_id]

    def add(self, project):
        project.id = self._next_id
        self._projects[project.id] = project
        self._next_id += 1
        return project

    def update(self, project):
        self._projects[project.id] = project
        return project

    def delete(self, project_id):
        self._projects.pop(project_id, None)


class FakeIssueRepo(IssueRepo):
    def __init__(self):
        self._issues: dict[int, Issue] = {}
        self._next_id = 1

    def get_by_id(self, issue_id):
        return self._issues.get(issue_id)

    def list_by_project(self, project_id, status=None, priority=None):
        result = [i for i in self._issues.values() if i.project_id == project_id]

        if status is not None:
            result = [i for i in result if i.status == status]

        if priority is not None:
            result = [i for i in result if i.priority == priority]

        return result

    def add(self, issue):
        issue.id = self._next_id
        self._issues[issue.id] = issue
        self._next_id += 1
        return issue

    def update(self, issue):
        self._issues[issue.id] = issue
        return issue

    def delete(self, issue_id):
        self._issues.pop(issue_id, None)


class FakeUserRepo(UserRepo):
    def __init__(self):
        self._users: dict[int, User] = {}
        self._next_id = 1

    def get_by_id(self, user_id):
        return self._users.get(user_id)

    def get_by_username(self, username):
        return next((u for u in self._users.values() if u.username == username), None)

    def get_by_email(self, email):
        return next((u for u in self._users.values() if u.email == email), None)

    def add(self, user):
        if self.get_by_username(user.username) or self.get_by_email(user.email):
            raise ValueError("user already exists")

        user.id = self._next_id
        self._users[user.id] = user
        self._next_id += 1
        return user
