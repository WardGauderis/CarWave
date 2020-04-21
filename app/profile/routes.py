from flask import redirect, render_template, url_for, request, flash
from flask_login import current_user, login_required

from app.profile import bp
from app.crud import *
from app.auth.forms import CreateUserForm, DeleteUserForm
from app.profile.forms import CreateCarForm


@bp.route('/car/update/<string:license_plate>', methods=['GET', 'POST'])
@login_required
def car_edit(license_plate):
    update = CreateCarForm()
    update.make_update_form()
    car = read_car_from_plate(license_plate)

    if update.validate_on_submit():
        try:
            if "submit" in request.form:
                update_car(car, update)
                return redirect(url_for('profile.car_create'))
        except Exception as e:
            flash(e.description, 'danger')

        if "delete" in request.form:
            delete_car(car)
        return redirect(url_for('profile.car_create'))

    if request.method == 'GET':
        update.from_database(car)

    return render_template('car-edit.html', title='Edit Car', update=update, background=True)


@bp.route('/car/create', methods=['GET', 'POST'])
@login_required
def car_create():
    create = CreateCarForm()
    create.make_create_form()

    if create.validate_on_submit():
        create_car(create, current_user)

    return render_template('car-create.html', title='My Cars', create=create, cars=current_user.cars, background=True)


@bp.route('/user/<int:user_id>')
def user(user_id):
    temp_user = read_user_from_id(user_id)
    if temp_user is None:
        abort(404, 'User does not exist')
    return render_template('user.html', title=temp_user.username, user=temp_user, background=True)


@bp.route('/user/update', methods=['GET', 'POST'])
@login_required
def user_edit():
    form = CreateUserForm()
    delete = DeleteUserForm()
    form.make_update_form()
    if form.submit.data and form.validate():
        update_user(current_user, form)
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('profile.user', user_id=current_user.id))
    if delete.delete.data and delete.validate():
        user = current_user
        delete_user(user)
        flash('Your account has successfully been removed.', 'success')
        return redirect(url_for('auth.logout'))
    elif request.method == 'GET':
        form.from_database(current_user)
    return render_template('user-edit.html', title="Edit profile", form=form, delete=delete, background=True)
