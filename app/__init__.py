from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import Config
from flask_login import LoginManager

bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
# login.login_message = 'Please log in to access this page.'


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
    from app.map import bp as map_bp
    app.register_blueprint(map_bp)
    from app.text import bp as text_bp
    app.register_blueprint(text_bp)

    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    return app
