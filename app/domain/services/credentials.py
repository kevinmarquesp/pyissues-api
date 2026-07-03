from app.domain.models.credentials import Credentials
from app.domain.repositories.credentials import CredentialsRepo

from pydantic import EmailStr
from ulid import ULID

class CredentialsService:
  _credentials_repo: CredentialsRepo

  def __init__(self, credentials_repo: CredentialsRepo):
    self._credentials_repo = credentials_repo

  def change_email(self, account_id: ULID, password: str, new_email: EmailStr):
    credentials = self._credentials_repo.get_by_account_id(account_id)

    credentials.check_password(password)
    self._credentials_repo.change_email(credentials, new_email)

  def change_password(
    self, account_id: ULID, password: str, new_password: str):

    credentials = self._credentials_repo.get_by_account_id(account_id)

    credentials.check_password(password)
    self._credentials_repo.change_password(credentials, new_password)

