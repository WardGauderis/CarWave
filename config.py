import os


class Config:
    """
    Config class with values that is passed to the flask application
    """

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'psql:/// whatever postgres uri is'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

