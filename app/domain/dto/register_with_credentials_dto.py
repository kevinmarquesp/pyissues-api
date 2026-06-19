from datetime import datetime


class RegisterWithCredentialsDto:
  class Params:
    username: str
    email: str
    password: str

  class Response:
    id: str
    created_at: datetime
