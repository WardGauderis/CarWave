from flask import render_template, request, flash, redirect, url_for
from app.crud import create_message, read_messages_from_user_pair, read_user_from_id, read_messaged_users
from app.messages import bp
from flask_login import current_user, login_required
from app.messages.forms import MessageForm


@bp.route('/messages/send/<recipient_id>', methods=['GET', 'POST'])
@login_required
def send_message(recipient_id):
    recipient = read_user_from_id(recipient_id)
    form = MessageForm()

    if recipient is None:
        flash("trying to message a non existing user")
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        create_message(current_user, recipient, form.message.data)
        return redirect(url_for('messages.send_message', recipient_id=recipient_id))

    messages = read_messages_from_user_pair(current_user, recipient)

    return render_template('messages.html', title='Send Message', form=form, messages=messages, background=True)


@bp.route('/messages/view', methods=['GET', 'POST'])
@login_required
def view_messages():
    recipients = read_messaged_users(current_user)
    return render_template('overview.html', title='View Messages', recipients=recipients, background=True)
