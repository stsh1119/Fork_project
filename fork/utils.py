from email_validator import validate_email, EmailNotValidError
# from models import User


def validate_user_email(email):
    try:
        valid = validate_email(email)
        email = valid.email
        return email
    except EmailNotValidError:
        email = ''
        return email


def prettify_fork(forks: list):
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
