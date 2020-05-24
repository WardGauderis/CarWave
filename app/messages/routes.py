from flask import render_template, request, flash, redirect, url_for
from app.crud import create_message, read_messages_from_user_pair, read_user_from_id, read_messaged_users
from app.messages import bp
from flask_login import current_user, login_required
from app.messages.forms import MessageForm


@bp.route('/messages/send/<recipient_id>', methods=['GET', 'POST'])
@login_required
def send_message(recipient_id):
    recipient = read_user_from_id(recipient_id)
    form = MessageForm(meta={'csrf': False})

    if recipient is None:
        flash("trying to message a non existing user")
        return redirect(url_for('main.index'))

    if form.validate_on_submit():
        create_message(current_user, recipient, form.message.data)
        return redirect(url_for('messages.send_message', recipient_id=recipient_id))

    amount = request.args.get('amount', 20, type=int)
    messages = read_messages_from_user_pair(current_user, recipient, amount)
    load_more = (len(messages) == amount)
    loaded_new = (amount != 20)

    return render_template('messages.html', title='Send Message', form=form, messages=messages[::-1], background=True,
                           load_more=load_more, loaded_new=loaded_new, recipient_id=recipient_id)


@bp.route('/messages/view', methods=['GET', 'POST'])
@login_required
def view_messages():
    recipients = read_messaged_users(current_user)
    return render_template('overview.html', title='View Messages', recipients=recipients, background=True)
