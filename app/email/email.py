from app import mail
from app.crud import *
from flask_mail import Message
from flask import render_template
import requests as req


def address_to_location(address):
    try:
        url = "https://nominatim.openstreetmap.org/lookup?osm_ids=" + address
        params = {"format": "json"}
        r = req.get(url=url, params=params)
        data = r.json()
        return data[0]['display_name']
    except:
        return "Nomatin server error"

def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_new_message_email(sender, recipient, data):
    if recipient.email is None or recipient.email== '': return
    send_email('[Carwave] You have recieved a new message!',
               recipients=[recipient.email],
               text_body=render_template('send_new_message_email.txt',
                                         sender=sender, recipient=recipient, data=data),
               html_body=render_template('send_new_message_email.html',
                                         sender=sender, recipient=recipient, data=data))

def send_new_review_email(sender, recipient, data):
    if recipient.email is None or recipient.email== '': return
    send_email('[Carwave] You have recieved a new review!',
               recipients=[recipient.email],
               text_body=render_template('send_new_review_email.txt',
                                         sender=sender, recipient=recipient, data=data),
               html_body=render_template('send_new_review_email.html',
                                         sender=sender, recipient=recipient, data=data))


def send_passenger_request_email(user, drive: Ride):
    recipient =  read_user_from_id(drive.driver_id).email
    if recipient is None or recipient == '': return
    send_email('[Carwave] You have a new pending request',
               recipients=[recipient],
               text_body=render_template('send_passenger_request_email.txt',
                                         user=user, recipient = read_user_from_id(drive.driver_id).username, from_adress = address_to_location(drive.departure_id), to_adress = address_to_location(drive.arrival_id), dep_time = drive.departure_time, ar_time = drive.arrival_time),
               html_body=render_template('send_passenger_request_email.html',
                                         user=user, recipient = read_user_from_id(drive.driver_id).username, from_adress = address_to_location(drive.departure_id), to_adress = address_to_location(drive.arrival_id), dep_time = drive.departure_time, ar_time = drive.arrival_time, ride=drive))

def send_passenger_request_accept_email(passenger, drive: Ride):
    if passenger.email is None or passenger.email== '': return
    send_email('[Carwave] Your passenger request has been accepted!',
           recipients=[passenger.email],
           text_body=render_template('send_passenger_request_accept_email.txt',
                                     user=passenger, driver = read_user_from_id(drive.driver_id).username, from_adress = address_to_location(drive.departure_id), to_adress = address_to_location(drive.arrival_id), dep_time = drive.departure_time, ar_time = drive.arrival_time),
           html_body=render_template('send_passenger_request_accept_email.html',
                                     user=passenger, driver = read_user_from_id(drive.driver_id).username, from_adress = address_to_location(drive.departure_id), to_adress = address_to_location(drive.arrival_id), dep_time = drive.departure_time, ar_time = drive.arrival_time))

def send_passenger_request_reject_email(passenger, drive: Ride):
    if passenger.email is None or passenger.email == '': return
    send_email('[Carwave] Your passenger request has been rejected.',
           recipients=[passenger.email],
           text_body=render_template('send_passenger_request_reject_email.txt',
                                     user=passenger, driver = read_user_from_id(drive.driver_id).username, from_adress = address_to_location(drive.departure_id), to_adress = address_to_location(drive.arrival_id), dep_time = drive.departure_time, ar_time = drive.arrival_time),
           html_body=render_template('send_passenger_request_reject_email.html',
                                     user=passenger, driver = read_user_from_id(drive.driver_id).username, from_adress = address_to_location(drive.departure_id), to_adress = address_to_location(drive.arrival_id), dep_time = drive.departure_time, ar_time = drive.arrival_time))

def send_drive_deleted_email(drive: Ride):
    for passenger_request in drive.accepted_requests():
        passenger = passenger_request.passenger
        if passenger.email is None or passenger.email == '': continue
        send_email('[Carwave] Ride cancelled.',
           recipients=[passenger.email],
           text_body=render_template('send_drive_deleted_email.txt',
                                     user=passenger, driver = read_user_from_id(drive.driver_id).username, from_adress = address_to_location(drive.departure_id), to_adress = address_to_location(drive.arrival_id), dep_time = drive.departure_time, ar_time = drive.arrival_time),
           html_body=render_template('send_drive_deleted_email.html',
                                     user=passenger, driver = read_user_from_id(drive.driver_id).username, from_adress = address_to_location(drive.departure_id), to_adress = address_to_location(drive.arrival_id), dep_time = drive.departure_time, ar_time = drive.arrival_time))