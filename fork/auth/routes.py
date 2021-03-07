from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt
from fork import jwt
from .valdators import register_validator, login_validator, change_password_validator
from .auth_service import register_service, login_service, refresh_token_service, change_password_service

auth = Blueprint('auth', __name__)
blacklist = set()


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


@auth.route('/register', methods=['POST'])
def register():
    if not request.json:
        return jsonify(error="Missing request body."), 400
    try:
        login, email, password = register_validator(request.json)
        register_service(login, email, password)
        return jsonify('Success'), 201
    except Exception as e:
        return jsonify(str(e)), 400


@auth.route('/login', methods=['POST'])
def login():
    if not request.json:
        return jsonify(error="Missing request body."), 400
    try:
        login, password = login_validator(request.json)
        return jsonify(login_service(login, password)), 200
    except Exception as e:
        return jsonify(str(e)), 400


@auth.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    return jsonify(refresh_token_service(current_user)), 200


@auth.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200


@auth.route('/change_password', methods=['POST'])
@jwt_required
def change_password():
    if not request.json:
        return jsonify(error="Missing request body."), 400
    try:
        old_password, new_password, confirm_new_password = change_password_validator(request.json)
        change_password_service(old_password, new_password, get_jwt_identity())
        return jsonify(msg="Password was changed.")
    except Exception as e:
        return jsonify(str(e)), 400
