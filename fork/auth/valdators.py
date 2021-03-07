from email_validator import validate_email, EmailNotValidError


def register_validator(request):
    login = request.get('login', None)
    email = request.get('email', None)
    password = request.get('password', None)
    if not all([login, email, password]):
        raise Exception("One of the following parameters is missing: login, email, password.")
    try:
        validate_email(email)
    except EmailNotValidError:
        raise Exception("Email is invalid.")

    return login, email, password


def login_validator(request):
    login = request.get('login', None)
    password = request.get('password', None)

    if not all([login, password]):
        raise Exception("One of the following parameters is missing: login or password.")

    return login, password


def change_password_validator(request):
    old_password = request.get('old_password', None)
    new_password = request.get('new_password', None)
    confirm_new_password = request.get('confirm_new_password', None)

    if not all([old_password, new_password, confirm_new_password]):
        raise Exception("One of parameters is missing: old_password, new_password, confirm_new_password.")
    if new_password != confirm_new_password:
        raise Exception("New password should be the same as confirm_new_password.")
    if old_password == new_password:
        raise Exception("Old password cannot be the same as new one.")

    return old_password, new_password, confirm_new_password
