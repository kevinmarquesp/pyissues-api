from app.domain.models.auth import Session, Jwt
from app.domain.repositories.auth import AuthRepo
from app.domain.repositories.credentials import CredentialsRepo
from app.domain.repositories.account import AccountRepo

from pydantic import EmailStr

class AuthService:
  _auth_repo: AuthRepo
  _credentials_repo: CredentialsRepo
  _account_repo: AccountRepo

  def __init__(
    self,
    auth_repo: AuthRepo,
    credentials_repo: CredentialsRepo,
    account_repo: AccountRepo):

    self._auth_repo = auth_repo
    self._credentials_repo = credentials_repo
    self._account_repo = account_repo

  def login_with_credentials(
    self, email: EmailStr, password: str) -> tuple[Session, Jwt]:

    credentials = self._credentials_repo.find_by_email(email)
    account = self._account_repo.find_by_id(credentials.account_id)

    credentials.check_password(password)

    session = Session(account_id=account.id)
    token = Jwt(sub=account.id, role=account.role)

    self._auth_repo.save_session(session)

    return session, token

  def refresh_access_token(self, str_token: str) -> Jwt:
    token = Jwt.decode(str_token)
    session = self._auth_repo.get_session_by_account_id(token.sub)
    new_token = Jwt(sub=token.sub, role=token.role)

    session.check_due()

    return new_token

