from flask_mail import Message
from flask import current_app
from flask import render_template

from app import mail


def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user):
    print("hallo3")
    token = user.get_reset_password_token()
    send_email('[Carwave] Reset Your Password',
               recipients=[user.email],
               text_body=render_template('reset_password_email.txt',
                                         user=user, token=token),
               html_body=render_template('reset_password_email.html',
                                         user=user, token=token))

