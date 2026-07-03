from app.domain.models.account import Account, Profile
from app.domain.models.credentials import Credentials

from ulid import ULID

from abc import ABC, abstractmethod

class AccountRepo(ABC):
  @abstractmethod
  def create_account_with_credentials(
    self, account: Account, credentials: Credentials):
    ...

  @abstractmethod
  def create_profile(self, profile: Profile):
    ...

  @abstractmethod
  def find_by_id(self, id: ULID) -> Account:
    ...

