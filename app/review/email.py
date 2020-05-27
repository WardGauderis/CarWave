from flask_mail import Message
from flask import render_template

from app import mail


def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_new_review_email(sender, recipient):
    send_email('[Carwave] You have recieved a new review!',
               recipients=[recipient.email],
               text_body=render_template('new_review_email.txt',
                                         sender=sender, recipient=recipient),
               html_body=render_template('new_review_email.html',
                                         sender=sender, recipient=recipient))

