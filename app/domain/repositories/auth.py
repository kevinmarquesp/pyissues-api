from app.domain.models.auth import Session

from ulid import ULID

from abc import ABC, abstractmethod

class AuthRepo(ABC):
  @abstractmethod
  def save_session(self, session: Session):
    ...

  @abstractmethod
  def get_session_by_account_id(self, account_id: ULID) -> Session:
    ...

