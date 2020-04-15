from flask import render_template, request, url_for, redirect
from flask_login import current_user, login_required
from app.offer import bp
from app.offer.forms import OfferForm
from app.crud import create_drive, read_all_drives


@bp.route('/offer', methods=['POST', 'GET'])
@login_required
def offer():
    form = OfferForm()
    if form.validate_on_submit():
        user = current_user
        create_drive(form, user)
        return redirect(url_for('main.index'))
    from_location = request.args.get('fl')
    to_location = request.args.get('tl')
    date = request.args.get('dt')
    return render_template('offer.html', title='Offer', form=form, fl=from_location, tl=to_location, dt=date)


@bp.route('/find')
def find():
    return render_template('find.html', title='Find', rides=Ride.get_all())
