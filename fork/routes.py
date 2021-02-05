from flask import jsonify, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, get_raw_jwt
)
import datetime
from fork import app, bcrypt, db, jwt
from fork.models import User, Fork
from fork.utils import validate_user_email

blacklist = set()


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


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
    user = User.query.filter_by(login=login).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_expiry = datetime.timedelta(minutes=15)
        reftesh_expiry = datetime.timedelta(days=1)
        refresh_token = create_refresh_token(identity=login, expires_delta=reftesh_expiry)
        response = {
            'access_token': create_access_token(identity=login, expires_delta=access_expiry),
            'refresh_token': refresh_token,
        }
        user.refresh_token = refresh_token
        db.session.commit()
        return jsonify(response), 200
    return jsonify({"msg": "Bad login or password"}), 401


@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    access_expiry = datetime.timedelta(minutes=15)
    response = {
        'access_token': create_access_token(identity=current_user, expires_delta=access_expiry),
    }
    return jsonify(response), 200


@app.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200


@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    login = get_jwt_identity()
    return jsonify(logged_in_as=login), 200


@app.route('/forks/all')
@jwt_required
def get_all_forks():
    page = request.args.get('page', default=1, type=int)  # 1 will be default
    forks = Fork.query.order_by(Fork.creation_date.desc()).paginate(page=page, per_page=10)
    return jsonify(fork.items for fork in forks)
