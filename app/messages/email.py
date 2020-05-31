from flask_mail import Message
from flask import render_template

from app import mail


def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_new_message_email(sender, recipient):
    if recipient.email is not None or recipient.email== '': return
    send_email('[Carwave] You have recieved a new message!',
               recipients=[recipient.email],
               text_body=render_template('new_message_email.txt',
                                         sender=sender, recipient=recipient),
               html_body=render_template('new_message_email.html',
                                         sender=sender, recipient=recipient))

