from app.domain.models.credentials import Credentials

from pydantic import EmailStr
from ulid import ULID

from abc import ABC, abstractmethod

class CredentialsRepo(ABC):
  @abstractmethod
  def find_by_email(self, email: EmailStr) -> Credentials:
    ...

  @abstractmethod
  def get_by_account_id(self, account_id: ULID) -> Credentials:
    ...

  @abstractmethod
  def change_email(self, credentials: Credentials, new_email: EmailStr):
    ...

  @abstractmethod
  def change_password(self, credentials: Credentials, new_password: EmailStr):
    ...

