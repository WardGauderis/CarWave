from flask import render_template, request, url_for, redirect, flash
from flask_login import current_user, login_required
import requests as req
import pytz
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

    from_address = request.args.get('fl')
    to_address = request.args.get('tl')
    unaware_time = dateutil.parser.parse(request.args.get('dt'))
    time = pytz.utc.localize(unaware_time)

    def address_to_location(address):
        url = "https://nominatim.openstreetmap.org/search/" + address
        params = {"format": "json"}
        r = req.get(url=url, params=params)
        data = r.json()
        return data[0]['lat'], data[0]['lon']

    from_location = address_to_location(from_address)
    to_location = address_to_location(to_address)

    if details.refresh.data and details.validate_on_submit():
        age = details.age
        consumption = details.cons
        gender = details.gender

        rides = search_drives(departure=from_location, arrival=to_location, arrival_time=time, departure_distance=5000,
                              arrival_distance=5000,
                              arrival_delta=timedelta(minutes=30),
                              age_range=(age - 10, age + 10),
                              consumption_range=(None, consumption), sex=gender)
    else:
        rides = search_drives(departure=from_location, arrival=to_location, arrival_time=time, departure_distance=5000,
                              arrival_distance=5000,
                              arrival_delta=timedelta(minutes=30))

    return render_template('find.html', title='Find', details=details, select=select,
                           rides=rides, background=True)


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

    return render_template('requests.html', title='Passenger Drives', requests=current_user.future_passenger_requests(),
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
