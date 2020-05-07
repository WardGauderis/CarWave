from flask import render_template, redirect, render_template, url_for, request, flash
from app.messages import bp
from flask_login import current_user, login_required
from app.models import User
from app.messages.forms import MessageForm


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User
    form = MessageForm()
    if form.validate_on_submit():
        flash('hey')

    return render_template('send_message.html', title='Send Message', form=form, messages=messages)
