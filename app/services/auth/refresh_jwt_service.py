from app.domain.repositories.auth_repository import AuthRepository
from app.domain.dto.refresh_jwt_dto import RefreshJwtDto


class RefreshJwtService:
  _auth_repository: AuthUserRepository

  def __init__(self, auth_repository: AuthUserRepository) -> None:
    self._auth_repository = auth_repository


  def execute(self, params: RefreshJwtDto.Params) -> RefreshJwtDto.Response:
    pass
