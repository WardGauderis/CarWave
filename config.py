from os import environ


class Config:
    """
    Config class with values that is passed to the flask application
    """

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = (environ.get("SECRET_KEY") or b"\xdd/\xb0f\x0co\xe06O\xf6.\xac\xbe)\xcd\xb7")
