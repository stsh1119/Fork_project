from email_validator import validate_email, EmailNotValidError
from fork.models import ForkCategory
from flask_mail import Mail, Message

mail = Mail()


def validate_user_email(email):
    try:
        valid = validate_email(email)
        email = valid.email
        return email
    except EmailNotValidError:
        email = ''
        return email


def prettify_forks(forks: list) -> list:
    forks_list = []
    for fork in forks:
        fork = {
            'id': fork.fork_id,
            'name': fork.name,
            'description': fork.description,
            'creation_date': fork.creation_date,
            'category': fork.fork_category,
            'owner': fork.user,
        }
        forks_list.append(fork)
    return forks_list


def prettify_categories(categories: list) -> list:
    categories_list = []
    for category in categories:
        category = {
            'name': category.category,
            'description': category.description,
        }
        categories_list.append(category)
    return categories_list


def prepare_creation_data(raw_data):
    """"Categories  are going to be predefined, so that users can only choose from suggested ones,
        this will be marked as 'Uncategorized' otherwise.

        If all([name, description, creation_date, category in [category.category for category in ForkCategory.query.all()]]):
        checks whether all needed parameters are present in json body AND that provided category is within already existing ones
    """
    name = raw_data.get('name', None)
    description = raw_data.get('description', None)
    creation_date = raw_data.get('creation_date', None)
    category = raw_data.get('category', 'Uncategorized')
    if all([name, description, creation_date, category in [category.category for category in ForkCategory.query.all()]]):
        result = {'name': name,
                  'description': description,
                  'creation_date': creation_date,
                  'category': category
                  }
        return result
    return False  # False means that given data is invalid in some way


def send_notification_email(users_list, fork_category):
    for user in users_list:
        msg = Message('New fork added!',
                      sender='fork_project@gmail.com',
                      recipients=[user.user_email])
        msg.body = f"""Hello, {user.user_email},
New fork was added to {fork_category}
"""
    mail.send(msg)
