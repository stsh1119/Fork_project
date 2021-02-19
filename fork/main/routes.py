from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from fork.models import Fork, User, ForkCategory, Subscription, db
from fork.utils import prettify_forks, prettify_categories, prepare_creation_data, send_notification_email
from sqlalchemy import exc

ITEMS_PER_PAGE = 10

main = Blueprint('main', __name__)


@main.route('/forks/all')
@jwt_required
def get_all_forks():
    page = request.args.get('page', default=1, type=int)
    forks = Fork.query.order_by(Fork.fork_id.desc()).paginate(page=page, per_page=ITEMS_PER_PAGE).items
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
        return jsonify(error='There is no fork with such id'), 404


@main.route('/forks/categories')
@jwt_required
def get_fork_catagories():
    page = request.args.get('page', default=1, type=int)
    categories = ForkCategory.query.paginate(page=page, per_page=ITEMS_PER_PAGE).items
    categories = prettify_categories(categories)
    return jsonify(categories)


@main.route('/forks/category/<string:category_name>')
@main.route('/forks/category/', defaults={'category_name': 'Uncategorized'})
@jwt_required
def get_fork_from_category(category_name):
    page = request.args.get('page', default=1, type=int)
    forks = Fork.query.filter_by(fork_category=category_name).paginate(page=page, per_page=ITEMS_PER_PAGE).items
    forks = prettify_forks(forks)
    return jsonify(forks)


@main.route('/forks/create', methods=['POST'])
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
        if users_to_notify:
            send_notification_email(users_list=users_to_notify, fork_category=results.get('category'))
        return jsonify(result='Fork successfully created'), 201
    return jsonify(error='One or several parameters are invalid'), 400


@main.route('/forks/delete', methods=['DELETE'])
@jwt_required
def delete_fork():
    user = User.query.filter_by(login=get_jwt_identity()).first()
    fork_name = request.args.get('name')
    fork = Fork.query.filter_by(name=fork_name).first_or_404()
    if fork.user == user.email:
        db.session.delete(fork)
        db.session.commit()
        return jsonify(result='Fork successfully deleted'), 201
    return jsonify(error='You cannot delete this fork'), 400


@main.route('/forks/my_forks')
@jwt_required
def show_your_forks():
    user = User.query.filter_by(login=get_jwt_identity()).first()
    my_forks = prettify_forks(Fork.query.filter_by(user=user.email).all())
    return jsonify(my_forks), 200


@main.route('/forks/<string:email>')
@jwt_required
def show_forks_owned_by_user(email):
    user = User.query.filter_by(email=email).first()
    if user:
        user_forks = prettify_forks(Fork.query.filter_by(user=user.email).all())
        return jsonify(user_forks), 200
    return jsonify(error='Couldn\'t find that user'), 400


@main.route('/forks/sign_up', methods=['POST'])
@jwt_required
def sign_up_for_notifications():
    request_category = request.args.get('category')
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


@main.route('/forks/remove_subscription', methods=['DELETE'])
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


@main.route('/forks/view_subscriptions')
@jwt_required
def view_subscriptions():
    user_email = User.query.filter_by(login=get_jwt_identity()).first().email
    subscriptions = Subscription.query.filter_by(user_email=user_email).all()
    if subscriptions:
        result = [subscriptions.subscription_category for subscriptions in subscriptions]
        return jsonify(result)
    return jsonify(f'{user_email} does not have any subscriptions')
