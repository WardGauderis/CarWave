from app.review import bp
from flask_login import login_required

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
