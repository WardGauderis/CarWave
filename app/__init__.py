import logging
from logging.handlers import RotatingFileHandler
from time import strftime

from flask import Flask, app, request
from flask.json import dumps
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import Config
from flask_login import LoginManager
from flask_moment import Moment

bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
moment = Moment()
# login.login_message = 'Please log in to access this page.'

# Rudimentary request logging
logger = logging.getLogger(__name__)
handler = RotatingFileHandler("logs/requests.log", maxBytes=100000, backupCount=10)
logger.addHandler(handler)

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    from app.error import bp as errors_bp
    app.register_blueprint(errors_bp)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    from app.text import bp as text_bp
    app.register_blueprint(text_bp)
    from app.offer import bp as offer_bp
    app.register_blueprint(offer_bp)
    from app.profile import bp as profile_bp
    app.register_blueprint(profile_bp)

    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    moment.init_app(app)

    # Logging
    @app.after_request
    def after_request(response):
        timestamp = strftime("[%Y-%b-%d %H:%M]")
        req_json = request.get_json(silent=True)
        logger.error(
            "%s %s %s %s %s %s\n%s",
            timestamp,
            request.remote_addr,
            request.method,
            request.scheme,
            request.full_path,
            response.status,
            dumps(req_json, indent=2) if req_json is not None else "",
        )
        return response

    return app
