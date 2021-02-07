from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required
from fork.models import Fork
from fork.utils import prettify_forks

main = Blueprint('main', __name__)


@main.route('/forks/all')
@jwt_required
def get_all_forks():
    page = request.args.get('page', default=1, type=int)
    forks = Fork.query.order_by(Fork.creation_date.desc()).paginate(page=page, per_page=10).items
    forks = prettify_forks(forks)
    return jsonify(forks)


@main.route('/forks/<int:fork_id>')
@jwt_required
def get_fork_by_id(fork_id):
    forks = Fork.query.filter_by(fork_id=fork_id).all()
    forks = prettify_forks(forks)
    try:
        return jsonify(forks[0])  # If no item is found, IndexError will be raised
    except IndexError:
        return jsonify(error='There is no fork with such id')
