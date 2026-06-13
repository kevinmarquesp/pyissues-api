from flask import Flask
from api.health_routes import health_bp
from api.auth_routes import auth_bp
from api.project_routes import project_bp
from api.issue_routes import issue_bp
from api.comment_routes import comment_bp
from infra.db import close_db
from config import Config


def create_app(config_class=Config):
  app = Flask(__name__)

  app.config.from_object(config_class)
  app.teardown_appcontext(close_db)

  app.register_blueprint(health_bp)
  app.register_blueprint(auth_bp)
  app.register_blueprint(project_bp)
  app.register_blueprint(issue_bp)
  app.register_blueprint(comment_bp)

  return app


if __name__ == '__main__':
  app = create_app()

  app.run(host='0.0.0.0', port=5000)
