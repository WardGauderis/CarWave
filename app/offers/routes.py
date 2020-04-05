from flask import render_template
from app.offers import bp
from app.api.api import search_drive


@bp.route('/offers')
def offers():

    return render_template('offers.html', title='Offers')


@bp.route('/find')
def find():
    print(search_drive())
    return render_template('find.html', title='Find')
