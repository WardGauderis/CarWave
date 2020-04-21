from flask import render_template, request, url_for, redirect, flash
from flask_login import current_user, login_required
import requests as req
import pytz
from app.offer import bp
from app.offer.forms import *
from app.crud import *


def crud_logic():
    if 'button2' in request.form:
        if request.form['button2'] == "Delete ride":
            drive = read_drive_from_id(request.form['ride_id'])
            delete_drive(drive)
            return redirect(url_for('offer.driver_rides'))

        elif request.form['button2'] == "Delete request":
            drive = read_drive_from_id(request.form['ride_id'])
            passenger = read_passenger_request(current_user, drive)
            delete_passenger_request(passenger)
            return redirect(url_for('offer.requests'))

        elif request.form['button2'] == "Reject request":
            drive = read_drive_from_id(request.form['ride_id'])
            passenger = read_user_from_id(request.form['user_id'])
            update_passenger_request(read_passenger_request(passenger, drive), "reject")
            return redirect(url_for('offer.requests'))

    if 'button1' in request.form:
        if request.form['button1'] == "Edit ride":
            return redirect(url_for('offer.offer', rid=request.form['ride_id']))

        elif request.form['button1'] == "Request ride":
            drive = read_drive_from_id(request.form['ride_id'])
            try:
                create_passenger_request(current_user, drive)
                flash('Congratulations, you successfully subscribed as passenger', 'success')
                return redirect(url_for('main.index'))
            except Exception as e:
                flash(e.description, 'danger')

        elif request.form['button1'] == "Accept request":
            drive = read_drive_from_id(request.form['ride_id'])
            passenger = read_user_from_id(request.form['user_id'])
            update_passenger_request(read_passenger_request(passenger, drive), "accept")
            return redirect(url_for('offer.driver_rides'))

    return None


@bp.route('/offer', methods=['POST', 'GET'])
@login_required
def offer():
    form = OfferForm(meta={'csrf': False})

    form.license_plate.choices = [('None', 'None')]
    for car in current_user.cars:
        form.license_plate.choices.append((car.license_plate, car.license_plate))

    from_location = request.args.get('fl')
    to_location = request.args.get('tl')

    ride_id = request.args.get('rid')

    if form.validate_on_submit():
        if ride_id is None:
            create_drive(form, current_user)
            flash('Congratulations, you successfully offered a ride', 'success')
            return redirect(url_for('offer.driver_rides'))
        else:
            try:
                update_drive(read_drive_from_id(ride_id), form)
                flash('Congratulations, you successfully offered a ride', 'success')
                return redirect(url_for('offer.driver_rides'))
            except Exception as e:
                flash(e.description, 'danger')

    if ride_id is None:
        arrival_time = request.args.get('at')
        return render_template('offer.html', title='Offer', form=form, fl=from_location, tl=to_location,
                               at=arrival_time,
                               background=True)
    else:
        drive = read_drive_from_id(ride_id)
        form.from_database(drive)
        return render_template('offer.html', title='Offer', form=form, at=drive.arrival_time, background=True)


@bp.route('/requests', methods=['POST', 'GET'])
@login_required
def requests():
    form = RideDataForm(meta={'csrf': False})

    if form.validate_on_submit():
        res = crud_logic()
        if res is not None:
            return res

    pending = []
    for drive in read_drive_from_driver(current_user, True):
        pending += drive.pending_requests()

    return render_template('rides.html', none_found='No future pending requests found', title='Your Requests',
                           form=form, requests=pending, background=True)


@bp.route('/find', methods=['POST', 'GET'])
def find():
    form = RideDataForm(meta={'csrf': False})
    details = FilterForm()

    if (form.button1 or form.button2) and form.validate_on_submit():
        res = crud_logic()
        if res is not None:
            return res

    from_address = request.args.get('fl')
    to_address = request.args.get('tl')
    utc_string = request.args.get('at')
    utc_time = dateutil.parser.parse(utc_string)
    print(utc_time)

    def address_to_location(address):
        url = "https://nominatim.openstreetmap.org/search/" + address
        params = {"format": "json"}
        r = req.get(url=url, params=params)
        data = r.json()
        return [data[0]['lat'], data[0]['lon']]

    from_location = address_to_location(from_address)
    to_location = address_to_location(to_address)

    age_range = None
    consumption_range = None
    sex = None

    if details.refresh.data and details.validate_on_submit():
        if details.age.data:
            age_range = (details.age.data - 10, details.age.data + 10)
        if details.usage.data:
            consumption_range = (None, details.usage.data)
        if details.gender.data != 'Any':
            sex = details.gender.data

    rides = search_drives(departure=from_location,
                          arrival=to_location,
                          arrival_time=utc_time,
                          departure_distance=5000,
                          arrival_distance=5000,
                          arrival_delta=timedelta(minutes=119),
                          age_range=age_range,
                          consumption_range=consumption_range,
                          sex=sex)

    return render_template('rides.html', title='Find', none_found='No suitable future rides found', details=details,
                           form=form, rides=rides, background=True)


@bp.route('/rides/all', methods=['POST', 'GET'])
def all_rides():
    form = RideDataForm(meta={'csrf': False})

    if form.validate_on_submit():
        res = crud_logic()
        if res is not None:
            return res

    return render_template('rides.html', title='Available Drives', none_found='No future rides found', form=form,
                           rides=read_all_drives('future'),
                           background=True)


@bp.route('/rides/passenger', methods=['POST', 'GET'])
@login_required
def passenger_rides():
    form = RideDataForm(meta={'csrf': False})

    if form.validate_on_submit():
        res = crud_logic()
        if res is not None:
            return res

    else:
        return render_template('rides.html', title='Passenger Drives',
                               none_found='No future drives with you as passenger found',
                               requests=current_user.future_passenger_requests(),
                               form=form, background=True)


@bp.route('/rides/driver', methods=['POST', 'GET'])
@login_required
def driver_rides():
    form = RideDataForm(meta={'csrf': False})

    if form.validate_on_submit():
        res = crud_logic()
        if res is not None:
            return res
    else:
        return render_template('rides.html', title='Your Drives', none_found='No Future drives organised by you found',
                               rides=read_drive_from_driver(current_user, True), form=form,
                               background=True)
