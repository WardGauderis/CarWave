from flask import render_template, request, url_for, redirect, flash
from flask_login import current_user, login_required
from app.offer import bp
from app.offer.forms import *
from app.crud import *


@bp.route('/requests', methods=['POST', 'GET'])
@login_required
def requests():
    form = RequestChoiceForm()

    if request.method == 'POST':
        drive = read_drive_from_id(form.ride_id.data)
        passenger = read_user_from_id(form.user_id.data)
        req = read_passenger_request(passenger, drive)

        if "reject" in request.form:
            update_passenger_request(req, "reject")
        elif "accept" in request.form:
            update_passenger_request(req, "accept")

    pending = []
    for drive in current_user.driver_rides:
        pending += drive.pending_requests()

    return render_template('requests.html', title='Your Requests', choice=form, requests=pending, background=True)


@bp.route('/offer', methods=['POST', 'GET'])
@login_required
def offer():
    form = OfferForm(meta={'csrf': False})

    form.car_string.choices = [('None', 'None')]
    for car in current_user.cars:
        form.car_string.choices.append((car.license_plate, car.license_plate))

    from_location = request.args.get('fl')
    to_location = request.args.get('tl')

    ride_id = request.args.get('rid')

    if form.validate_on_submit():
        if ride_id is None:
            create_drive(form, current_user)
            flash('Congratulations, you successfully offered a ride', 'success')
        else:
            update_drive(read_drive_from_id(ride_id), form)
            flash('Congratulations, you successfully changed your ride', 'success')
        return redirect(url_for('offer.driver_rides'))
    print(form.get_errors())

    if ride_id is None:
        date = request.args.get('dt')
        return render_template('offer.html', title='Offer', form=form, fl=from_location, tl=to_location, dt=date,
                               background=True)
    else:
        drive = read_drive_from_id(ride_id)
        form.from_database(drive)
        return render_template('offer.html', title='Offer', form=form, dt=drive.arrival_time, background=True)


@bp.route('/find', methods=['POST', 'GET'])
def find():
    select = SelectForm(meta={'csrf': False})
    details = FilterForm()

    if select.request.data and select.validate_on_submit():
        drive = read_drive_from_id(select.ride_id.data)
        create_passenger_request(current_user, drive)
        flash('Congratulations, you successfully requested a ride', 'success')
        return redirect(url_for('main.index'))
    print(select.get_errors())
    if details.refresh.data and details.validate_on_submit():
        print('this should kinda filter stuff, but it don\'t')
        return render_template('find.html', title='Find', details=details, select=select,
                               rides=read_all_drives('future'), background=True)
    print(details.get_errors())

    return render_template('find.html', title='Find', details=details, select=select, rides=read_all_drives('future'),
                           background=True)


@bp.route('/rides/all')
def all_rides():
    return render_template('rides.html', title='Available Drives', rides=read_all_drives('future'), background=True)


@bp.route('/rides/passenger', methods=['POST', 'GET'])
def passenger_rides():
    form = DeleteRequestForm()

    if request.method == 'POST':
        drive = read_drive_from_id(form.ride_id.data)
        passenger = read_passenger_request(current_user, drive)
        delete_passenger_request(passenger)
        return redirect(url_for('offer.passenger_rides'))

    return render_template('requests.html', title='Passenger Drives',
                           requests=current_user.future_passenger_requests(),
                           delete_req=form, background=True)


@bp.route('/rides/driver', methods=['POST', 'GET'])
def driver_rides():
    form = DeleteOfferForm()

    if request.method == 'POST':
        if "delete" in request.form:
            drive = read_drive_from_id(form.ride_id.data)
            delete_drive(drive)
            return redirect(url_for('offer.driver_rides'))
        elif "edit" in request.form:
            return redirect(url_for('offer.offer', rid=form.ride_id.data))

    return render_template('rides.html', title='Your Drives', rides=read_drive_from_driver(current_user), delete=form,
                           background=True)
