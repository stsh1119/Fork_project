from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required
from fork.models import Fork

main = Blueprint('main', __name__)


@main.route('/forks/all')
@jwt_required
def get_all_forks():
    page = request.args.get('page', default=1, type=int)
    forks = Fork.query.order_by(Fork.creation_date.desc()).paginate(page=page, per_page=10)
    return jsonify(fork.items for fork in forks)