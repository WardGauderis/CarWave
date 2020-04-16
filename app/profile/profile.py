from flask import redirect, render_template, url_for, abort, request, flash
from flask_login import current_user, login_required

from app.profile import bp
from app.crud import update_user, read_user_from_id
from app.profile.forms import UpdateUserForm


@bp.route('/user/<int:user_id>')
def user(user_id):
    user = read_user_from_id(user_id)
    if user is None:
        abort(404, 'User does not exist')
    return render_template('profile.html', user=user)


@bp.route('/user/update', methods=['GET', 'POST'])
@login_required
def edit():
    form = UpdateUserForm()
    if form.validate_on_submit():
        update_user(current_user, form)
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('profile.user', user_id=current_user.id))
    elif request.method == 'GET':
        form.from_database(current_user)
    return render_template('edit_profile.html', form=form)
