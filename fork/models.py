from fork import db


class User(db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(50), nullable=False, primary_key=True)
    login = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    forks = db.relationship('Fork', backref='users', lazy=True)

    def __repr__(self):
        return f"User('{self.email}', '{self.login}', '{self.password}')"


class Fork(db.Model):
    __tablename__ = 'forks'
    fork_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.Integer, nullable=False)
    fork_category = db.Column(db.String(50), nullable=False, default='Uncategorized')
    user = db.Column(db.String(50), db.ForeignKey('users.email'), nullable=False)

    def __repr__(self):
        return f"Fork('{self.fork_id}', '{self.name}', '{self.description}', '{self.creation_date}', '{self.user}')"


class ForkCategory(db.Model):
    __tablename__ = 'fork_categories'
    category = db.Column(db.String(50), primary_key=True)
    description = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"Fork_category('{self.category}', '{self.description}')"
