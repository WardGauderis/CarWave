from os import environ


class Config:
    """
    Config class with values that is passed to the flask application
    """

    # TODO official carwave email
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = 'carwave.ppdb@gmail.com'
    MAIL_DEFAULT_SENDER = 'carwave.ppdb@gmail.com'
    MAIL_PASSWORD = 'SxRTZSMeRL2gdza'
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URI") or 'postgresql://app@localhost/carwave_db?user=postgres&password=postgres'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://app@localhost/carwave_db?user=app&password=app'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = (environ.get("SECRET_KEY") or b"\xdd/\xb0f\x0co\xe06O\xf6.\xac\xbe)\xcd\xb7")
