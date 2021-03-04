from email_validator import validate_email, EmailNotValidError
from fork.models import ForkCategory


def validate_user_email(email):
    """"Using third party library validates user's email and in case email is invalid - returns falsey value"""
    try:
        valid = validate_email(email)
        email = valid.email
        return email
    except EmailNotValidError:
        email = ''
        return email


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
