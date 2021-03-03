from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from fork.models import db, ma
from fork.utils import mail
from fork.config import Config

bcrypt = Bcrypt()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

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
