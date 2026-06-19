from app.domain.repositories.auth_repository import AuthRepository
from app.domain.dto.register_with_credentials_dto import (
  RegisterWithCredentialsDto)


class RegisterWithCredentialsService:
  _auth_repository: AuthUserRepository

  def __init__(self, auth_repository: AuthUserRepository) -> None:
    self._auth_repository = auth_repository


  def execute(self, params: RegisterWithCredentialsDto.Params) -> \
    RegisterWithCredentialsDto.Response:
    pass
