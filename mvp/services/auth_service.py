from datetime import datetime, timedelta, timezone
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from domain.entities import User
from domain.repositories import UserRepo
from config import Config

class AuthServiceException(Exception):
  pass

class AuthService:
  def __init__(self, user_repo: UserRepo):
    self.user_repo = user_repo


  def register(self, username: str, email: str, password: str) -> any:
    # TODO: assert username string
    # TODO: assert email string

    user = User(
      id=None, username=username, email=email,
      password=generate_password_hash(password))  # TODO: add a password secret

    # TODO: create a custom exception message for when email/username exists
    try:
      return self.user_repo.add(user)

    except Exception as e:
      raise AuthServiceException(f"Couldn't add a new user: {str(e)}")


  def login(self, username: str, password: str) -> any:  # TODO: use email
    user = self.user_repo.get_by_username(username)

    if not user or not check_password_hash(user.password, password):
      raise AuthServiceException('Invalid username or password')

    return self._generate_token(user)


  def _generate_token(self, user):
    payload = {
      "sub": str(user.id),  # autoincrement integer id by now
      "username": user.username,
      "exp": datetime.now(timezone.utc) + \
        timedelta(hours=int(Config.JWT_EXPIRES_HOURS)),
      "iat": datetime.now(timezone.utc)}

    # TODO: put the algorithm in the config module/env
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


  def decode_token(self, token):
    try:
      return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])  # (!)

    except jwt.ExpiredSignatureError as e:
      raise AuthServiceException(f'Token expired: {str(e)}')

    except jwt.InvalidTokenError as e:
      raise AuthServiceException(f'Invalid token: {str(e)}')
