from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from fork.main.service import (view_all_forks, view_certain_fork_by_id, view_fork_catagories, view_my_forks,
                               view_forks_from_category, create_fork, delete_fork_by_name,
                               view_forks_owned_by_user, sign_up_for_email_notifications,
                               unsubscribe_from_email_notifications, view_my_subscriptions)
ITEMS_PER_PAGE = 10

main = Blueprint('main', __name__, url_prefix='/forks')


@main.route('/all')
@jwt_required
def get_all_forks():
    page = request.args.get('page', default=1, type=int)
    return jsonify(view_all_forks(page)), 200


@main.route('/<int:fork_id>')
@jwt_required
def get_fork_by_id(fork_id):
    return jsonify(view_certain_fork_by_id(fork_id)), 200


@main.route('/categories')
@jwt_required
def get_fork_catagories():
    page = request.args.get('page', default=1, type=int)
    return jsonify(view_fork_catagories(page)), 200


@main.route('/category/<string:category_name>')
@main.route('/category/', defaults={'category_name': 'Uncategorized'})
@jwt_required
def get_forks_from_category(category_name):
    page = request.args.get('page', default=1, type=int)
    return jsonify(view_forks_from_category(category_name, page)), 200


@main.route('/create', methods=['POST'])
@jwt_required
def create_new_fork():
    if not request.json:
        return jsonify(error="Missing request body."), 400
    try:
        return jsonify(create_fork(request.json, get_jwt_identity())), 200
    except Exception as e:
        return jsonify(e), 400


@main.route('/delete', methods=['DELETE'])
@jwt_required
def delete_fork():
    fork_name = request.args.get('name', None, type=str)
    return jsonify(delete_fork_by_name(fork_name, get_jwt_identity())), 200


@main.route('/my_forks')
@jwt_required
def show_your_forks():
    return jsonify(view_my_forks(get_jwt_identity())), 200


@main.route('/<string:email>')
@jwt_required
def show_forks_owned_by_user(email):
    return jsonify(view_forks_owned_by_user(email)), 200


@main.route('/sign_up', methods=['POST'])
@jwt_required
def sign_up_for_notifications():
    request_category = request.args.get('category', None)
    try:
        return jsonify(sign_up_for_email_notifications(request_category, get_jwt_identity()))
    except Exception as e:
        return jsonify(e), 400


@main.route('/remove_subscription', methods=['DELETE'])
@jwt_required
def remove_email_notifications():
    request_category = request.args.get('category', None)
    return jsonify(unsubscribe_from_email_notifications(request_category, get_jwt_identity())), 200


@main.route('/view_subscriptions')
@jwt_required
def view_subscriptions():
    return jsonify(view_my_subscriptions(get_jwt_identity())), 200
