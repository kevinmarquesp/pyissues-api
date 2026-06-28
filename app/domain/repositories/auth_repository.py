from abc import ABC, abstractmethod


class AuthRepository(ABC):
  @abstractmethod
  def register_with_credentials(
    self, username: str, email: str, password: str) -> any | None:
    ...

  @abstractmethod
  def get_account_credentials(self, account_id: str) -> any | None:
    ...

  @abstractmethod
  def authenticate(self, account_id: str) -> any | None:
    ...

  @abstractmethod
  def get_account_session(self, account_id: str) -> any | None:
    ...
