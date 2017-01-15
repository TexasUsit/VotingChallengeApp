from datetime import datetime
from VotingApp import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from flask_security import RoleMixin


ticker_identifier = db.Table('student_identifier',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('ticker_id', db.Integer, db.ForeignKey('tickers.id'))
)
#required for Flask-Security, could be useful later for admin screen
roles_users = db.Table('roles_users',
		db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
		db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(80))
    lastName = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String)
    active = db.Column(db.Boolean)
    stocks = db.relationship('Tickers', secondary=ticker_identifier, backref='user')
    transactions = db.relationship('Transactions', backref='user')
    #required for Flask-Security
    roles =  db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    def __repr__(self):
        return "<User '{}'>".format(self.email)


class Tickers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(5), unique=True)
    startingPrice = db.Column(db.Float)
    transactions = db.relationship('Transactions', backref='tickers')
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __repr__(self):
        return "<Ticker '{}'>".format(self.ticker)

class Transactions(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticker = db.Column(db.Integer, db.ForeignKey('tickers.id'), nullable=False)
    date = db.Column(db.String)
    end_price = db.Column(db.Integer)

# Flask Security
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.String(80))
