from flask import render_template, request, url_for, redirect
from app.main import bp
from app.main.forms import DriveForm


@bp.route('/', methods=['POST', 'GET'])
@bp.route('/index', methods=['POST', 'GET'])
def index():
    form = DriveForm()

    if request.method == 'POST':
        if "offer" in request.form:
            return redirect(url_for('offer.offer',
                                    fl=request.form['from_location'],
                                    tl=request.form['to_location'],
                                    at=request.form['arrival_time']))
        elif "find" in request.form:
            return redirect(url_for('offer.find',
                                    fl=request.form['from_location'],
                                    tl=request.form['to_location'],
                                    at=request.form['arrival_time']))

    return render_template('index.html', title='Home', form=form, no_random=True)
