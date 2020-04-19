from flask import render_template, request, url_for, redirect
from flask_login import current_user, login_required
from app.offer import bp
from app.offer.forms import *
from app.crud import *


# @bp.route('/request', methods=['POST', 'GET'])
# @login_required
# def request():
#     return


@bp.route('/offer', methods=['POST', 'GET'])
@login_required
def offer():
    form = OfferForm(meta={'csrf': False})

    form.car_string.choices = [('None', 'None')]
    for car in current_user.cars:
        form.car_string.choices.append((car.license_plate, car.license_plate))

    if form.validate_on_submit():
        create_drive(form, current_user)
        return redirect(url_for('main.index'))

    from_location = request.args.get('fl')
    to_location = request.args.get('tl')
    date = request.args.get('dt')
    return render_template('offer.html', title='Offer', form=form, fl=from_location, tl=to_location, dt=date)


@bp.route('/find', methods=['POST', 'GET'])
def find():
    select = SelectForm()
    details = FilterForm()

    if details.validate_on_submit():
        print('this should kinda filter stuff, but it don\'t')
        return render_template('find.html', title='Find', details=details, select=select, rides=read_all_drives())

    elif select.validate_on_submit():
        drive = read_drive_from_id(select.ride_id.data)
        create_passenger_request(current_user, drive)
        return redirect(url_for('main.index'))  # TODO: wahoo you requested your ride successfully

    return render_template('find.html', title='Find', details=details, select=select, rides=read_all_drives())


@bp.route('/rides/all')
def all_rides():
    return render_template('rides.html', title='Available Rides', rides=read_all_drives())


@bp.route('/rides/passenger', methods=['POST', 'GET'])
def passenger_rides():
    form = DeleteRequestForm()

    if request.method == 'POST':
        drive = read_drive_from_id(form.ride_id.data)
        passenger = read_passenger_request(current_user, drive)
        delete_passenger_request(passenger)
        return redirect(url_for('offer.passenger_rides'))

    # TODO: ik heb hier nog een read_drive_from_passenger nodig,
    #  deze gaat alle drives die voor hem nog moeten komen tonen
    return render_template('rides.html', title='Available Rides', rides=read_all_drives(), form=form)


@bp.route('/rides/driver', methods=['POST', 'GET'])
def driver_rides():
    form = DeleteOfferForm()

    if request.method == 'POST':
        drive = read_drive_from_id(form.ride_id.data)
        delete_drive(drive)
        return redirect(url_for('offer.driver_rides'))

    return render_template('rides.html', title='Available Rides', rides=read_drive_from_driver(current_user), form=form)
