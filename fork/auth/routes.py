from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, get_raw_jwt
)
import datetime
from fork import bcrypt, db, jwt
from fork.models import User
from fork.utils import validate_user_email

auth = Blueprint('auth', __name__)
blacklist = set()

ACCESS_TOKEN_EXPIRY = datetime.timedelta(minutes=15)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


@auth.route('/register', methods=['POST'])
def register():
    login = request.json.get('login', None)
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    email = validate_user_email(email)
    if all([login, email, password]):
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(email=email,
                    login=login,
                    password=hashed_password,
                    )
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify('Success'), 201
        except IntegrityError:
            return jsonify({'error': 'That login or email is already taken.'})
    else:
        return jsonify({'error': 'Missing data'})


@auth.route('/login', methods=['POST'])
def login():
    login = request.json.get('login', None)
    password = request.json.get('password', None)
    user = User.query.filter_by(login=login).first()
    if user and bcrypt.check_password_hash(user.password, password):
        reftesh_expiry = datetime.timedelta(days=1)
        refresh_token = create_refresh_token(identity=login, expires_delta=reftesh_expiry)
        response = {
            'access_token': create_access_token(identity=login, expires_delta=ACCESS_TOKEN_EXPIRY),
            'refresh_token': refresh_token,
        }
        user.refresh_token = refresh_token
        db.session.commit()
        return jsonify(response), 200
    return jsonify({"msg": "Bad login or password"}), 401


@auth.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    response = {
        'access_token': create_access_token(identity=current_user, expires_delta=ACCESS_TOKEN_EXPIRY),
    }
    return jsonify(response), 200


@auth.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200
