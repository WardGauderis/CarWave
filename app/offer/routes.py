from flask import render_template, request, url_for, redirect
from flask_login import current_user, login_required
from app.offer import bp
from app.models import Ride
from app.offer.forms import OfferForm


@bp.route('/offer', methods=['POST', 'GET'])
@login_required
def offer():
    form = OfferForm()
    if request.method == 'POST':
        user = current_user
        Ride.create(
            driver_id=user.id,
            passenger_places=request.form['passengers'],
            departure_address=[request.form['from_lat'], request.form['from_lon']],
            arrival_address=[request.form['to_lat'], request.form['to_lon']],
            arrival_time=request.form['arrival_time']
        )
        return redirect(url_for('main.index'))

    from_location = request.args.get('fl')
    to_location = request.args.get('tl')
    date = request.args.get('dt')
    return render_template('offer.html', title='Offer', form=form, fl=from_location, tl=to_location, dt=date)


@bp.route('/find')
def find():
    return render_template('find.html', title='Find', rides=Ride.search())
