from app.models import User, db


def create_user(json):
    user = User(json)
    db.session.add(user)
    db.session.commit()
    return user


def read_user():
    pass


def update_user():
    pass


def delete_user():
    pass
