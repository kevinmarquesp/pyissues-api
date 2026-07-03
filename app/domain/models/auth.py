from app.domain.models.account import Role

from pydantic import BaseModel, Field, field_serializer
from ulid import ULID
import jwt

from datetime import datetime, timedelta
from enum import StrEnum, auto

class Context(StrEnum):
  ACCESS: str = auto()

class SessionExpiredException(Exception):
  pass

class Session(BaseModel):
  account_id: ULID
  context: Context = Context.ACCESS
  expires_at: datetime = Field(  # todo: config
    default_factory=lambda: datetime.now() + timedelta(days=7))

  def check_due(self):
    if datetime.now() > self.expires_at:
      raise SessionExpiredException(
        f"session '{self.account_id}' ({self.context}) expired")

class JwtExpiredException(Exception):
  pass

class Jwt(BaseModel):
  sub: ULID
  role: Role
  iat: datetime = Field(default_factory=lambda: datetime.now())
  exp: datetime = Field(  # todo: config
    default_factory=lambda: datetime.now() + timedelta(minutes=15))

  @field_serializer("sub", mode="plain")
  def _id_to_string(self, sub: ULID):
    return str(sub)

  def encode(self) -> str:

    # todo: config secret
    return jwt.encode(self.model_dump(), "secret", algorithm="HS256")

  @staticmethod
  def decode(token: str) -> Jwt:

    # todo: config secret
    return Jwt(**jwt.decode(token, "secret", algorithms=["HS256"]))

  def check_due(self):
    if datetime.now() > self.exp:
      raise JwtExpiredException(f"jwt '{self.sub}' expired")

