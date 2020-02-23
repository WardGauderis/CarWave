from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

"""
File with the database models described using SQLAlchemy
"""
class Driver(db.Model):
    __tablename__ = 'drivers'
    driver_id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)

    def __init__(self, driver_id, rating):
        self.rating = rating
        self.driver_id = driver_id

    def __repr__(self):
        return '<id {}>'.format(self.driver_id)