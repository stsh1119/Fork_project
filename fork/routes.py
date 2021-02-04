from flask import jsonify, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)
import datetime
from fork import app, bcrypt, db
from fork.models import User
from fork.utils import validate_user_email


@app.route('/register', methods=['POST'])
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


@app.route('/login', methods=['POST'])
def login():
    login = request.json.get('login', None)
    password = request.json.get('password', None)
    if login != 'test' or password != 'test':
        return jsonify({"msg": "Bad login or password"}), 401

    access_expiry = datetime.timedelta(minutes=1)
    reftesh_expiry = datetime.timedelta(days=200)
    response = {
        'access_token': create_access_token(identity=login, expires_delta=access_expiry),
        'refresh_token': create_refresh_token(identity=login, expires_delta=reftesh_expiry)
    }
    return jsonify(response), 200


@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    access_expiry = datetime.timedelta(minutes=1)
    response = {
        'access_token': create_access_token(identity=current_user, expires_delta=access_expiry),
    }
    return jsonify(response), 200


@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    login = get_jwt_identity()
    return jsonify(logged_in_as=login), 200
