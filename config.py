from os import getenv


class Config:
  FLASK_DEBUG = getenv('FLASK_DEBUG', '0') == '1'
  SQLITE3_FILE = getenv('SQLITE3_FILE', 'db.sqlite3')
  JWT_SECRET = getenv('JWT_SECRET', 'development.jm3aB6BMC8GfvQBpa0YA')
  JWT_EXPIRES_HOURS = getenv('JWT_EXPIRES_HOURS', '24')
