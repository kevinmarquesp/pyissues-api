from dataclasses import dataclass
from enum import Enum

@dataclass
class User:  # TODO: separate into `Account`, `Profile` and `Credentials`
    id: int | None  # TODO: use a non incremental id
    username: str
    email: str
    password: str

@dataclass
class Project:
    id: int | None
    user_id: int
    name: str
    description: str | None

class Status(str, Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"

    @classmethod
    def values(cls):
        return [s.value for s in cls]

# allowed status transitions (key -> set of statuses it can move to)
_VALID_TRANSITIONS = {
    Status.TODO.value: {Status.DOING.value},
    Status.DOING.value: {Status.TODO.value, Status.DONE.value},
    Status.DONE.value: {Status.DOING.value},
}

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @classmethod
    def values(cls):
        return [p.value for p in cls]

@dataclass
class Issue:
    id: int | None
    project_id: int
    title: str
    description: str | None
    status: str
    priority: str

    # TODO: move this llogic to a validation/service layer
    def can_transition_to(self, new_status: str) -> bool:  
        if new_status == self.status:
            return True

        return new_status in _VALID_TRANSITIONS.get(self.status, set())
