from abc import ABC, abstractmethod


class AuthRepository(ABC):
  @abstractmethod
  def create_account_and_credentials(
    self, username: str, email: str, password: str) -> any | None:  # Account
    ...
