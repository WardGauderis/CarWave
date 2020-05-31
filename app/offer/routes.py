import json

from flask import render_template, request, url_for, redirect, flash
from flask_login import current_user, login_required
import requests as req
from app.offer import bp
from app.offer.forms import *
from app.crud import *
from app.email.email import send_passenger_request_accept_email, send_passenger_request_reject_email, send_passenger_request_email


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
            send_passenger_request_reject_email(passenger, drive)
            update_passenger_request(read_passenger_request(passenger, drive), "reject")
            return redirect(url_for('offer.requests'))

    if 'button1' in request.form:
        if request.form['button1'] == "Edit ride":
            return redirect(url_for('offer.offer', rid=request.form['ride_id']))

        elif request.form['button1'] == "Request ride":
            drive = read_drive_from_id(request.form['ride_id'])
            try:
                create_passenger_request(current_user, drive)
                send_passenger_request_email(current_user, drive)
                flash('Congratulations, you successfully subscribed as passenger', 'success')
                return redirect(url_for('main.index'))
            except Exception as e:
                flash(e.description, 'danger')

        elif request.form['button1'] == "Accept request":
            drive = read_drive_from_id(request.form['ride_id'])
            passenger = read_user_from_id(request.form['user_id'])
            send_passenger_request_accept_email(passenger, drive)
            update_passenger_request(read_passenger_request(passenger, drive), "accept")
            return redirect(url_for('offer.driver_rides'))

    return None


def validate_time(time):
    if time == 'past' or time == 'future':
        return time
    else:
        return 'all'


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
                flash('Congratulations, you successfully updated your ride', 'success')
                return redirect(url_for('offer.driver_rides'))
            except Exception as e:
                flash(e.description, 'danger')

    if ride_id is None:
        arrival_time = request.args.get('at')
        return render_template('offer.html', title='Create ride', form=form, fl=from_location, tl=to_location,
                               at=arrival_time,
                               background=True)
    else:
        drive = read_drive_from_id(ride_id)
        form.from_database(drive)
        return render_template('offer.html', title='Edit ride', form=form, at=drive.arrival_time, background=True)


@bp.route('/requests', methods=['POST', 'GET'])
@login_required
def requests():
    form = RideDataForm(meta={'csrf': False})

    if form.validate_on_submit():
        res = crud_logic()
        if res is not None:
            return res

    pending = []
    page = read_drive_from_driver(current_user, "future", 1)
    while page.items:
        for drive in page.items:
            pending += drive.pending_requests()
        page = page.next()
    pending = pending[:10]

    return render_template('rides.html', none_found='No pending requests found', title='My Requests',
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

    def address_to_location(address):
        try:
            url = "https://nominatim.openstreetmap.org/search/" + address
            params = {"format": "json"}
            r = req.get(url=url, params=params)
            data = r.json()
            return [data[0]['lat'], data[0]['lon']]
        except:
            abort(503, "nominatim server error")

    from_location = address_to_location(from_address)
    to_location = address_to_location(to_address)

    age_range = None
    consumption_range = None
    sex = None
    rating_range = None
    tags = None

    if details.refresh.data and details.validate_on_submit():
        if details.age.data:
            age_range = (details.age.data - 10, details.age.data + 10)
        if details.usage.data:
            consumption_range = (None, details.usage.data)
        if details.gender.data != 'any':
            sex = details.gender.data

    try:
        min_rating = request.form.get('rating', -1, int)
        rating_range = [min_rating, 10] if 0 <= min_rating < 10 else None
        tags = list(filter(None, request.form.get('tags', '', str).split(',')))
        tags = set(tags) if tags else None
    except:
        abort(400, 'Invalid filter form data. Please use the form on the search page.')

    try:
        # Currently disregards optional features
        external_rides = req.get(
            f"http://team4.ppdb.me/api/drives/search?limit=10&arrive_by={utc_string[:22]}&to={','.join(to_location)}&from={','.join(from_location)}",
            headers= {"Content-Type": "application/json"},
        )
        external_rides: List[dict] = json.loads(external_rides.text)
        for ride in external_rides:
            ride["arrival_time"] = dateutil.parser.parse(ride.pop("arrive-by"))
            ride["driver"] = f"http://team4.ppdb.me/profile/{ride.pop('driver-id')}"
            ride["num_passengers"] = len(ride.pop("passenger-ids"))
            ride["url"] = f"http://team4.ppdb.me/ride_specification/{ride['id']}"
    except Exception as e:
        print(e)
        external_rides = None


    rides = search_drives(page_index=request.args.get('page', 1, type=int),
                          departure=from_location,
                          arrival=to_location,
                          arrival_time=utc_time,
                          departure_distance=5000,
                          arrival_distance=5000,
                          arrival_delta=timedelta(minutes=120),
                          age_range=age_range,
                          consumption_range=consumption_range,
                          sex=sex,
                          driver_rating=rating_range,
                          exclude_past_rides=True,
                          tags=tags)

    prev_url = url_for("offer.find", fl=from_address, tl=to_address, at=utc_string,
                       page=rides.prev_num) if rides.has_prev else None

    next_url = url_for("offer.find", fl=from_address, tl=to_address, at=utc_string,
                       page=rides.next_num) if rides.has_next else None

    return render_template('rides.html', title='Find', none_found='No suitable future rides found', details=details,
                           form=form, rides=rides.items, external_rides=external_rides, prev_url=prev_url,
                           next_url=next_url, background=True)


@bp.route('/ride/<int:ride_id>', methods=['POST', 'GET'])
def ride(ride_id):
    form = RideDataForm(meta={'csrf': False})

    if form.validate_on_submit():
        res = crud_logic()
        if res is not None:
            return res

    drive = read_drive_from_id(ride_id)

    if drive is None:
        abort(400, "This ride does not exist")

    return render_template('ride.html', ride=drive, form=form, background=True)


@bp.route('/rides', defaults={'time': 'all'}, methods=['POST', 'GET'])
@bp.route('/rides/<string:time>', methods=['POST', 'GET'])
def all_rides(time):
    form = RideDataForm(meta={'csrf': False})

    if form.validate_on_submit():
        res = crud_logic()
        if res is not None:
            return res

    time = validate_time(time)

    title = time + " drives"
    title.capitalize()

    page = request.args.get('page', 1, type=int)
    rides = read_all_drives(time, page)

    prev_url = url_for("offer.all_rides", page=rides.prev_num) if rides.has_prev else None
    next_url = url_for("offer.all_rides", page=rides.next_num) if rides.has_next else None

    return render_template('rides.html', title=title, none_found="no rides found", form=form,
                           time=time, rides=rides.items, prev_url=prev_url, next_url=next_url, background=True)


@bp.route('/passenger_rides', defaults={'time': 'all'}, methods=['POST', 'GET'])
@bp.route('/passenger_rides/<string:time>', methods=['POST', 'GET'])
@login_required
def passenger_rides(time):
    form = RideDataForm(meta={'csrf': False})

    if form.validate_on_submit():
        res = crud_logic()
        if res is not None:
            return res

    time = validate_time(time)

    title = time + " passenger drives"
    title.capitalize()

    page = request.args.get('page', 1, type=int)
    rides = current_user.future_or_past_passenger_requests(time, page)

    prev_url = url_for("offer.passenger_rides", page=rides.prev_num) if rides.has_prev else None
    next_url = url_for("offer.passenger_rides", page=rides.next_num) if rides.has_next else None

    return render_template('rides.html', title=title,
                           none_found='No drives with you as passenger found',
                           requests=rides.items, time=time, prev_url=prev_url, next_url=next_url,
                           form=form, background=True)


@bp.route('/driver_rides', defaults={'time': 'all'}, methods=['POST', 'GET'])
@bp.route('/driver_rides/<string:time>', methods=['POST', 'GET'])
@login_required
def driver_rides(time):
    form = RideDataForm(meta={'csrf': False})

    time = validate_time(time)

    title = "my " + time + " drives"
    if time == 'all':
        title = "all my rides"

    title.capitalize()

    if form.validate_on_submit():
        res = crud_logic()
        if res is not None:
            return res

    page = request.args.get('page', 1, type=int)
    rides = read_drive_from_driver(current_user, time, page)

    prev_url = url_for("offer.driver_rides", page=rides.prev_num) if rides.has_prev else None
    next_url = url_for("offer.driver_rides", page=rides.next_num) if rides.has_next else None

    return render_template('rides.html', title=title, none_found='No drives organised by you found',
                           rides=rides.items, form=form, time=time, prev_url=prev_url, next_url=next_url,
                           background=True)
