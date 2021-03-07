from fork import bcrypt, db
from fork.models import User
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_refresh_token, create_access_token
import datetime

ACCESS_TOKEN_EXPIRY = datetime.timedelta(minutes=15)
REFRESH_TOKEN_EXPIRY = datetime.timedelta(days=1)


def register_service(login, email, password):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(email=email,
                login=login,
                password=hashed_password,
                )
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        raise Exception('That login or email is already taken.')


def login_service(login, password):
    try:
        user = User.query.filter_by(login=login).first()

        if not user:
            raise Exception('No such login.')
        if not bcrypt.check_password_hash(user.password, password):
            raise Exception("Error: either login or password is incorrect.")

        response = {
            'access_token': create_access_token(identity=login, expires_delta=ACCESS_TOKEN_EXPIRY),
            'refresh_token': create_refresh_token(identity=login, expires_delta=REFRESH_TOKEN_EXPIRY),
        }

        return response
    except Exception as e:
        return str(e)


def refresh_token_service(login):
    new_refresh_token = create_refresh_token(identity=login, expires_delta=REFRESH_TOKEN_EXPIRY)
    response = {
        'access_token': create_access_token(identity=login, expires_delta=ACCESS_TOKEN_EXPIRY),
        'refresh_token': new_refresh_token,
    }

    return response


def change_password_service(old_password, new_password, login):
    try:
        user = User.query.filter_by(login=login).first()

        if not bcrypt.check_password_hash(user.password, old_password):
            raise Exception("Incorrect old password provided.")

        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()

    except Exception as e:
        raise e
