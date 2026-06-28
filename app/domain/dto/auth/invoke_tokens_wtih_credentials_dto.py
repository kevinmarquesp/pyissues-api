class InvokeTokensWithCredentialsDto:
  class Params:
    email: str
    password: str

  class Response:
    id: str
    jwt: str
    session: str
