from flask import jsonify, request
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)
from fork import app, bcrypt
import datetime


@app.route('/')
def index():
    return jsonify("hello"), 200


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username != 'test' or password != 'test':
        return jsonify({"msg": "Bad username or password"}), 401

    access_expiry = datetime.timedelta(minutes=1)
    reftesh_expiry = datetime.timedelta(days=200)
    response = {
        'access_token': create_access_token(identity=username, expires_delta=access_expiry),
        'refresh_token': create_refresh_token(identity=username, expires_delta=reftesh_expiry)
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
    username = get_jwt_identity()
    return jsonify(logged_in_as=username), 200
