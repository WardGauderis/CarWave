from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from config import Config
from .models import db


bootstrap = Bootstrap()
migrate = Migrate()


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    db.init_app(app)
    migrate.init_app(app, db)

    bootstrap.init_app(app)

    return app
