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
