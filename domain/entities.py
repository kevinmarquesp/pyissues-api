from dataclasses import dataclass

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
