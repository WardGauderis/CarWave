from flask import redirect, render_template, url_for, abort, request, flash
from flask_login import current_user, login_required

from app.profile import bp
from app.crud import *
from app.auth.forms import CreateUserForm
from app.profile.forms import CreateCarForm


@bp.route('/car/update', methods=['GET', 'POST'])
@login_required
def car_edit():
    create = CreateCarForm()
    update = CreateCarForm()
    update.make_update_form()

    if create.validate_on_submit():
        create_car(create)
    elif update.validate_on_submit():
        car = read_car_from_plate(update.license_plate.data)
        update_car(car, update)

    return render_template('car-edit.html', title='update cars', create=create, update=update, cars=current_user.cars)


@bp.route('/user/<int:user_id>')
def user(user_id):
    temp_user = read_user_from_id(user_id)
    if temp_user is None:
        abort(404, 'User does not exist')
    return render_template('user.html', title=temp_user.username, user=temp_user)


@bp.route('/user/update', methods=['GET', 'POST'])
@login_required
def user_edit():
    form = CreateUserForm()
    form.make_update_form()
    if form.validate_on_submit():
        update_user(current_user, form)
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('profile.user', user_id=current_user.id))
    elif request.method == 'GET':
        form.from_database(current_user)
    return render_template('user-edit.html', title="Edit profile", form=form)