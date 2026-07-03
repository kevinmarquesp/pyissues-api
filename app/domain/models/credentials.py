from pydantic import BaseModel, EmailStr, field_validator
from ulid import ULID
from bcrypt import hashpw, gensalt, checkpw

from datetime import datetime
from typing import Any
import re

class Credentials(BaseModel):
  account_id: ULID
  email: EmailStr
  password: bytes
  activated_at: datetime | None = None

  @field_validator("password", mode="after")
  @classmethod
  def _hash_password(cls, password: str | bytes) -> bytes:
    if isinstance(password, bytes):  # bytes is already hashed passwords
      return password

    if not re.search("[^a-zA-Z0-9]", password):
      raise ValueError("password: include at least one special character")

    if not re.search("[a-z]", password):
      raise ValueError("password: include at least one lowercase letter")

    if not re.search("[A-Z]", password):
      raise ValueError("password: include at least one uppercase letter")

    if not re.search("[0-9]", password):
      raise ValueError("password: include at least one digit")

    if not len(password) >= 12:
      raise ValueError("password should be more than 12 characters")

    return hashpw(password.encode(), gensalt())

  def check_password(self, password: str):
    if not checkpw(password.encode(), self.password):
      raise ValueError("passwords did not matched")
    
