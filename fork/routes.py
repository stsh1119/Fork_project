from flask import jsonify
from fork import app
from fork.models import Fork


@app.route('/')
def index():
    return jsonify("hello"), 200
