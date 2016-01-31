from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr
from werkzeug import generate_password_hash, check_password_hash

db = SQLAlchemy()

class LoginBase(db.Model):
    __abstract__ = True

    @declared_attr 
    def __tablename__(cls):
        return cls.__name__.lower()    
    
    uid = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    pwdhash = db.Column(db.String(54))
     
    def __init__(self, firstname, lastname, email, password):
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.email = email.lower()
        self.set_password(password)
         
    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)
     
    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

class Coach(LoginBase):
    clients = db.relationship('User')

class User(LoginBase):
    coach = db.relationship('Coach')
    coachid = db.Column(db.Integer, db.ForeignKey('coach.uid'))