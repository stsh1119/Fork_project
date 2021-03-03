from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()


class User(db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(50), nullable=False, primary_key=True)
    login = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    refresh_token = db.Column(db.String(257), default=None)
    forks = db.relationship('Fork', backref='users', lazy=True)

    def __repr__(self):
        return f"User('{self.email}', '{self.login}', '{self.password}')"


class Fork(db.Model):
    __tablename__ = 'forks'
    fork_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.Integer, nullable=False)
    fork_category = db.Column(db.String(50), db.ForeignKey('fork_categories.category'),
                              nullable=False, default='Uncategorized')
    user = db.Column(db.String(50), db.ForeignKey('users.email'), nullable=False)

    def __repr__(self):
        return f"Fork('{self.fork_id}', '{self.name}', '{self.description}', '{self.creation_date}', '{self.user}')"


class ForkCategory(db.Model):
    __tablename__ = 'fork_categories'
    category = db.Column(db.String(50), primary_key=True)
    description = db.Column(db.String(50), nullable=False)
    forks = db.relationship('Fork', backref='fork_categories', lazy=True)

    def __repr__(self):
        return f"Fork_category('{self.category}', '{self.description}')"


class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(50), db.ForeignKey('users.email'), nullable=False)
    subscription_category = db.Column(db.String(50), db.ForeignKey('fork_categories.category'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_email', 'subscription_category'), )

    def __repr__(self):
        return f"Subscription('{self.user_email}', '{self.subscription_category}')"


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
    email = ma.auto_field()
    login = ma.auto_field()


class ForkSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Fork
    fork_id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    creation_date = ma.auto_field()
    fork_category = ma.auto_field()
    user = ma.auto_field()


class ForkCategorySchema(ma.SQLAlchemySchema):
    class Meta:
        model = ForkCategory
    category = ma.auto_field()
    description = ma.auto_field()


class SubscriptionSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Subscription
    user_email = ma.auto_field()
    subscription_category = ma.auto_field()


user_schema = UserSchema()
forks_schema = ForkSchema(many=True)
fork_category_schema = ForkCategorySchema(many=True)
subscription_schema = SubscriptionSchema(many=True)
