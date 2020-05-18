from app import mail
from app.models import Ride
from app.crud import *
from flask_mail import Message
from flask import render_template

def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_passenger_request_email(user, drive: Ride):
    send_email('[Carwave] You have a new pending request',
               recipients=[read_user_from_id(drive.driver_id).email],
               text_body=render_template('send_passenger_request_email.txt',
                                         user=user, recipient = read_user_from_id(drive.driver_id).username, from_adress = drive.departure_address, to_adress = drive.arrival_address, dep_time = drive.departure_time, ar_time = drive.arrival_time),
               html_body=render_template('send_passenger_request_email.html',
                                         user=user, recipient = read_user_from_id(drive.driver_id).username, from_adress = drive.departure_address, to_adress = drive.arrival_address, dep_time = drive.departure_time, ar_time = drive.arrival_time))
