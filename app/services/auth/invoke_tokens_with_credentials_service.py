from app.domain.repositories.auth_repository import AuthRepository
from app.domain.dto.invoke_tokens_with_credentials_dto import (
  InvokeTokensWithCredentialsDto)


class InvokeTokensWithCredentialsService:
  _auth_repository: AuthUserRepository

  def __init__(self, auth_repository: AuthUserRepository) -> None:
    self._auth_repository = auth_repository


  def execute(self, params: InvokeTokensWithCredentialsDto.Params) -> \
    InvokeTokensWithCredentialsDto.Response:
    pass
