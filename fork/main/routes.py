from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from fork.models import (Fork, User, ForkCategory, Subscription, db,
                         fork_category_schema, forks_schema, subscription_schema, fork_schema)
from fork.utils import prepare_creation_data
from sqlalchemy import exc
from fork.tasks import send_notification_email

ITEMS_PER_PAGE = 10

main = Blueprint('main', __name__, url_prefix='/forks')


@main.route('/all')
@jwt_required
def get_all_forks():
    page = request.args.get('page', default=1, type=int)
    forks = Fork.query.order_by(Fork.fork_id.desc()).paginate(page=page, per_page=ITEMS_PER_PAGE).items
    serialized_forks = forks_schema.dump(forks)
    return jsonify(serialized_forks)


@main.route('/<int:fork_id>')
@jwt_required
def get_fork_by_id(fork_id):
    fork = Fork.query.filter_by(fork_id=fork_id).first()
    serialized_fork = fork_schema.dump(fork)
    return jsonify(serialized_fork)


@main.route('/categories')
@jwt_required
def get_fork_catagories():
    page = request.args.get('page', default=1, type=int)
    categories = ForkCategory.query.paginate(page=page, per_page=ITEMS_PER_PAGE).items
    serialized_categories = fork_category_schema.dump(categories)
    return jsonify(serialized_categories)


@main.route('/category/<string:category_name>')
@main.route('/category/', defaults={'category_name': 'Uncategorized'})
@jwt_required
def get_forks_from_category(category_name):
    page = request.args.get('page', default=1, type=int)
    forks = Fork.query.filter_by(fork_category=category_name).paginate(page=page, per_page=ITEMS_PER_PAGE).items
    serialized_forks = forks_schema.dump(forks)
    return jsonify(serialized_forks)


@main.route('/create', methods=['POST'])
@jwt_required
def create_new_fork():
    user = User.query.filter_by(login=get_jwt_identity()).first()
    results = prepare_creation_data(request.json)
    if results:
        fork = Fork(name=results.get('name'),
                    description=results.get('description'),
                    creation_date=results.get('creation_date'),
                    fork_category=results.get('category'),
                    user=user.email)
        db.session.add(fork)
        db.session.commit()
        users_to_notify = Subscription.query.filter_by(subscription_category=results.get('category')).all()
        serialized_users_to_notify = subscription_schema.dump(users_to_notify)
        if serialized_users_to_notify:
            send_notification_email.delay(users_list=serialized_users_to_notify, fork_category=results.get('category'))
            return jsonify(result='Fork successfully created'), 201
        return jsonify(result='Fork successfully created'), 201
    return jsonify(error='One or several parameters are invalid'), 400


@main.route('/delete', methods=['DELETE'])
@jwt_required
def delete_fork():
    user = User.query.filter_by(login=get_jwt_identity()).first()
    fork_name = request.args.get('name', None)
    fork = Fork.query.filter_by(name=fork_name).first_or_404()
    if fork.user == user.email:
        db.session.delete(fork)
        db.session.commit()
        return jsonify(result='Fork successfully deleted'), 201
    return jsonify(error='You cannot delete this fork'), 400


@main.route('/my_forks')
@jwt_required
def show_your_forks():
    user = User.query.filter_by(login=get_jwt_identity()).first()
    my_forks = forks_schema.dump(Fork.query.filter_by(user=user.email).all())
    return jsonify(my_forks), 200


@main.route('/<string:email>')
@jwt_required
def show_forks_owned_by_user(email):
    user = User.query.filter_by(email=email).first()
    if user:
        user_forks = forks_schema.dump(Fork.query.filter_by(user=user.email).all())
        return jsonify(user_forks), 200
    return jsonify(error='Couldn\'t find that user'), 400


@main.route('/sign_up', methods=['POST'])
@jwt_required
def sign_up_for_notifications():
    request_category = request.args.get('category', None)
    existing_categories = [category.category for category in ForkCategory.query.all()]
    if request_category not in existing_categories:
        return jsonify(error='This category doesn\'t exist.'), 404
    user_email = User.query.filter_by(login=get_jwt_identity()).first().email
    subscription = Subscription(user_email=user_email, subscription_category=request_category)
    try:
        db.session.add(subscription)
        db.session.commit()
        return jsonify(status=f'{user_email} has signed up for {request_category}'), 200
    except exc.IntegrityError:
        return jsonify(status=f'{user_email} is already signed up for {request_category}'), 409


@main.route('/remove_subscription', methods=['DELETE'])
@jwt_required
def remove_email_notifications():
    request_category = request.args.get('category')
    user_email = User.query.filter_by(login=get_jwt_identity()).first().email
    subscription = Subscription.query.filter_by(user_email=user_email, subscription_category=request_category).first()
    if subscription:
        db.session.delete(subscription)
        db.session.commit()
        return jsonify(f'Subscription for {request_category} was cancelled'), 200
    return jsonify(f'{user_email} is not signed up for {request_category}')


@main.route('/view_subscriptions')
@jwt_required
def view_subscriptions():
    user_email = User.query.filter_by(login=get_jwt_identity()).first().email
    subscriptions = Subscription.query.filter_by(user_email=user_email).all()
    if subscriptions:
        result = [subscriptions.subscription_category for subscriptions in subscriptions]
        return jsonify(result)
    return jsonify(f'{user_email} does not have any subscriptions')
