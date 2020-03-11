from os import environ


class Config:
    """
    Config class with values that is passed to the flask application
    """

    SQLALCHEMY_DATABASE_URI = "postgres://wrakoymffevbme:745b959f952a0df08b80ff0715c856acfb9c57df552e6d85c115e05c0ba957b4@ec2-46-137-156-205.eu-west-1.compute.amazonaws.com:5432/dc74dtjuu01vrr" or 'postgresql://app@localhost/carwave_db?user=postgres&password=postgres'
    # SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = (environ.get("SECRET_KEY") or b"\xdd/\xb0f\x0co\xe06O\xf6.\xac\xbe)\xcd\xb7")
