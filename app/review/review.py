from app.review import bp
from flask import jsonify, request
from app.crud import read_tags

@bp.route('/tags')
def tags():
    q = request.args.get('q', None, type=str)
    tags = read_tags(q)
    return jsonify([tag[0] for tag in tags])
