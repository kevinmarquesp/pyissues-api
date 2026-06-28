from datetime import datetime


class RefreshJwtDto:
  class Params:
    jwt: str
    session: str


  class Response:
    jwt: str
    created_at: datetime
