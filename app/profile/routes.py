from flask import redirect, render_template, url_for, abort, request, flash
from flask_login import current_user, login_required

from app.profile import bp
from app.crud import *
from app.auth.forms import CreateUserForm
from app.profile.forms import CreateCarForm


@bp.route('/car/update', methods=['GET', 'POST'])
@login_required
def car_edit():

    forms = []
    size = len(current_user.cars)

    for i in range(size):
        temp = CreateCarForm()
        temp.make_update_form()
        forms.append(temp)

    forms.append(CreateCarForm())

    for i in range(size+1):
        if forms[i].validate_on_submit():
            if forms[i].update:
                update_car(current_user.cars[i], forms[i])
                print('update')
            else:
                create_car(forms[i])
                forms[-1].make_update_form()
                forms.append(CreateCarForm())
                print('create')

    if request.method == 'GET':
        for i in range(size):
            forms[i].from_database(current_user.cars[i])

    return render_template('car-edit.html', title='update cars', forms=forms)


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
