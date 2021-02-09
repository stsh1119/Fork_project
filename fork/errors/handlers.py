from flask import Blueprint, jsonify

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    return jsonify(error="Couldn't find the page"), 404


@errors.app_errorhandler(405)
def error_405(error):
    return jsonify(error="The method is not allowed for the requested URL."), 405


@errors.app_errorhandler(500)
def error_500(error):
    return jsonify(error="Sorry, some server error occurred"), 500
