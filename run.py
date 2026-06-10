from os import getenv
from flask import Flask
from api.health_routes import health_bp


class Config:
  FLASK_DEBUG = getenv('FLASK_DEBUG', '0') == '1'
  SQLITE3_FILE = getenv('SQLITE3_FILE', 'db.sqlite3')
  JWT_SECRET = getenv('JWT_SECRET', 'development_secret')


def create_app(config_class=Config):
  app = Flask(__name__)

  app.config.from_object(config_class)
  app.register_blueprint(health_bp)

  return app


app = create_app()

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
