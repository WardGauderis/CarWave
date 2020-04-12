from flask import flash, g, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.profile import bp
from app import db
from app.models import User
from app.auth.forms import EditProfileForm


@bp.route('/user/<username>')
@login_required
def user(username):
    #TODO check user == currentuser
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('User %s not found.' % username, 'error')
        return redirect(url_for('index'))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('profile.html',
                           user=user,
                           posts=posts)


@bp.route('/user/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit(username):
    #TODO check user == currentuser
    #TODO python functie
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.firstname = form.first_name.data
        current_user.lastname = form.last_name.data
        # current_user.email = form.email
        # current_user.phone_number = form.phone_number
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('auth.user', username=username))
    else:
        form.first_name.data = current_user.firstname
        form.last_name.data = current_user.lastname
        # form.email = current_user.email
        # form.phone_number = current_user.phone_number
    return render_template('edit_profile.html', form=form)
