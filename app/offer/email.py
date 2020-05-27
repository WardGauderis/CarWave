from app import mail
from app.models import Ride
from app.crud import *
from flask_mail import Message
from flask import render_template
from requests import request as req

def address_to_location(address):
    url = "https://nominatim.openstreetmap.org/search/" + address
    params = {"format": "json"}
    r = req.get(url=url, params=params)
    data = r.json()
    return [data[0]['lat'], data[0]['lon']]

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

def send_passenger_request_accept_email(passenger, drive: Ride):
    send_email('[Carwave] Your passenger request has been accepted!',
               recipients=[passenger.email],
               text_body=render_template('send_passenger_request_accept_email.txt',
                                         user=passenger, driver = read_user_from_id(drive.driver_id).username, from_adress = drive.departure_address, to_adress = drive.arrival_address, dep_time = drive.departure_time, ar_time = drive.arrival_time),
               html_body=render_template('send_passenger_request_accept_email.html',
                                         user=passenger, driver = read_user_from_id(drive.driver_id).username, from_adress = drive.departure_address, to_adress = drive.arrival_address, dep_time = drive.departure_time, ar_time = drive.arrival_time))

def send_passenger_request_reject_email(passenger, drive: Ride):
    send_email('[Carwave] Your passenger request has been rejected.',
               recipients=[passenger.email],
               text_body=render_template('send_passenger_request_reject_email.txt',
                                         user=passenger, driver = read_user_from_id(drive.driver_id).username, from_adress = drive.departure_address, to_adress = drive.arrival_address, dep_time = drive.departure_time, ar_time = drive.arrival_time),
               html_body=render_template('send_passenger_request_reject_email.html',
                                         user=passenger, driver = read_user_from_id(drive.driver_id).username, from_adress = drive.departure_address, to_adress = drive.arrival_address, dep_time = drive.departure_time, ar_time = drive.arrival_time))