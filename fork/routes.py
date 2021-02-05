# from flask import jsonify, request
# from flask_jwt_extended import jwt_required
# from fork import app
# from fork.models import Fork


# @app.route('/forks/all')
# @jwt_required
# def get_all_forks():
#     page = request.args.get('page', default=1, type=int)  # 1 will be default
#     forks = Fork.query.order_by(Fork.creation_date.desc()).paginate(page=page, per_page=10)
#     return jsonify(fork.items for fork in forks)
