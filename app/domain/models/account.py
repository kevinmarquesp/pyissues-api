from ulid import ULID
from pydantic import BaseModel, Field, field_validator, EmailStr

from enum import StrEnum, auto
import re

class Role(StrEnum):
  USER: str = auto()
  ADMIN: str = auto()
  OWNER: str = auto()

class Provider(StrEnum):
  CREDENTIALS: str = auto()

class Account(BaseModel):
  id: ULID = Field(default_factory=ULID, frozen=True)
  username: str
  role: Role = Role.USER
  provider: Provider

  @field_validator("username", mode="after")
  @classmethod
  def _validate_characters(cls, username: str) -> str:
    assert " " not in username, ""
    assert not re.search("[^a-zA-Z0-9_-]", username), \
      "username: special characters not supported"
    
    return username

  @field_validator("username", mode="after")
  @classmethod
  def _check_reserved_names(cls, username: str) -> str:
    assert username not in ["username", "user", "owner", "admin", "app"], \
      f"reserved username '{username}' not allowed"

    return username

class Visibility(StrEnum):
  PUBLIC: str = auto()
  PRIVATE: str = auto()

class Profile(BaseModel):
  account_id: ULID = Field(frozen=True)
  visibility: Visibility = Visibility.PUBLIC
  name: str
  bio: str | None = None
  email: EmailStr | None = None

