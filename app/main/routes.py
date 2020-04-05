from flask import render_template, request, url_for, redirect
from app.main import bp
from app.main.forms import DriveForm


@bp.route('/', methods=['POST', 'GET'])
@bp.route('/index', methods=['POST', 'GET'])
def index():
    form = DriveForm()
    if request.method == 'POST':
        if "offer" in request.form:
            return redirect(url_for('offers.offers'))
        elif "find" in request.form:
            return redirect(url_for('offers.find'))
    return render_template('index.html', title='Home', form=form)

