import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from fork.models import db, ma
from fork.tasks import mail
from fork.config import Config
from .celery_utils import init_celery

bcrypt = Bcrypt()
jwt = JWTManager()
PKG_NAME = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]


def create_app(app_name=PKG_NAME, config_class=Config, **kwargs):
    app = Flask(__name__)
    app.config.from_object(config_class)
    if kwargs.get("celery"):
        init_celery(kwargs.get("celery"), app)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    ma.init_app(app)

    from fork.main.routes import main
    from fork.auth.routes import auth
    from fork.errors.handlers import errors
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
