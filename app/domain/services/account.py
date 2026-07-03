from app.domain.models.account import Account, Profile, Provider
from app.domain.models.credentials import Credentials
from app.domain.repositories.account import AccountRepo

class AccountService:
  _account_repo: AccountRepo

  def __init__(self, account_repo: AccountRepo):
    self._account_repo = account_repo

  def register_with_credentials(
    self, username: str, email: str, password: str) -> Account:

    account = Account(username=username, provider=Provider.CREDENTIALS)
    credentials = Credentials(
      account_id=account.id, email=email, password=password)
    profile = Profile(
      account_id=account.id, name=account.username, email=credentials.email)

    self._account_repo.create_account_with_credentials(account, credentials)
    self._account_repo.create_profile(profile)

    return account

