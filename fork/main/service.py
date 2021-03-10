from fork.models import (Fork, User, ForkCategory, Subscription, db,
                         fork_category_schema, forks_schema, subscription_schema, fork_schema)
from fork.main.utils import prepare_creation_data
from fork.tasks import send_notification_email
from sqlalchemy import exc

ITEMS_PER_PAGE = 10


def view_all_forks(page):
    forks = Fork.query.order_by(Fork.fork_id.desc()).paginate(page=page, per_page=ITEMS_PER_PAGE).items
    serialized_forks = forks_schema.dump(forks)
    return serialized_forks


def view_certain_fork_by_id(fork_id):
    fork = Fork.query.filter_by(fork_id=fork_id).first()
    serialized_fork = fork_schema.dump(fork)
    return serialized_fork


def view_fork_catagories(page):
    categories = ForkCategory.query.paginate(page=page, per_page=ITEMS_PER_PAGE).items
    serialized_categories = fork_category_schema.dump(categories)
    return serialized_categories


def view_forks_from_category(category_name, page):
    forks = Fork.query.filter_by(fork_category=category_name).paginate(page=page, per_page=ITEMS_PER_PAGE).items
    serialized_forks = forks_schema.dump(forks)
    return serialized_forks


def create_fork(request, login):
    try:
        user = User.query.filter_by(login=login).first()
        results = prepare_creation_data(request)

        if not results:
            raise Exception('One or several parameters are invalid')
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
            return 'Fork successfully created'

        return 'Fork successfully created'

    except Exception as e:
        return str(e)


def delete_fork_by_name(name, login):
    user = User.query.filter_by(login=login).first()
    fork = Fork.query.filter_by(name=name).first_or_404()

    if fork.user == user.email:
        db.session.delete(fork)
        db.session.commit()
        return 'Fork successfully deleted'

    return 'You cannot delete this fork'


def view_my_forks(login):
    user = User.query.filter_by(login=login).first()
    my_forks = forks_schema.dump(Fork.query.filter_by(user=user.email).all())
    return my_forks


def view_forks_owned_by_user(email):
    user = User.query.filter_by(email=email).first()
    if user:
        user_forks = forks_schema.dump(Fork.query.filter_by(user=user.email).all())
        return user_forks

    return 'Couldn\'t find that user'


def sign_up_for_email_notifications(category, login):
    try:
        existing_categories = [category.category for category in ForkCategory.query.all()]

        if category not in existing_categories:
            raise Exception('This category doesn\'t exist.')
        user_email = User.query.filter_by(login=login).first().email
        subscription = Subscription(user_email=user_email, subscription_category=category)

        try:
            db.session.add(subscription)
            db.session.commit()
            return f'{user_email} has signed up for {category}'

        except exc.IntegrityError:
            raise Exception(f'{user_email} is already signed up for {category}')

    except Exception as e:
        return str(e)


def unsubscribe_from_email_notifications(category, login):
    user_email = User.query.filter_by(login=login).first().email
    subscription = Subscription.query.filter_by(user_email=user_email, subscription_category=category).first()
    if subscription:
        db.session.delete(subscription)
        db.session.commit()
        return f'Subscription for {category} was cancelled'
    return f'{user_email} is not signed up for {category}'


def view_my_subscriptions(login):
    user_email = User.query.filter_by(login=login).first().email
    subscriptions = Subscription.query.filter_by(user_email=user_email).all()
    if subscriptions:
        result = [subscriptions.subscription_category for subscriptions in subscriptions]
        return result
    return f'{user_email} does not have any subscriptions'
