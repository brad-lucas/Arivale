import sys

from arivale_scheduling import current_datetime, appointment_slot_length_in_hours
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr
from werkzeug import generate_password_hash, check_password_hash

db = SQLAlchemy()

class EntityBase(db.Model):
  __abstract__ = True

  @declared_attr 
  def __tablename__(cls):
    tablename = ''

    # we want to use title casing in object names, but table names should be
    # all lowercased
    # and names containing multiple words have said words separated by
    # underscores
    # - ex.: 'Coach' --> 'coach'
    # - ex.: 'CoachAvailabilitySlot' --> 'coach_availability_slot'
    for character in cls.__name__:
      if character.isupper() and len(tablename) > 0:
        tablename += '_'

      character = character.lower()
      
      tablename += character
        
    return tablename

class LoginBase(EntityBase):
  __abstract__ = True 
  
  first_name = db.Column(db.String(100))
  last_name = db.Column(db.String(100))
  email = db.Column(db.String(120), unique=True)
  pwd_hash = db.Column(db.String(54))
   
  def __init__(self, first_name, last_name, email, password):
    self.first_name = first_name.title()
    self.last_name = last_name.title()
    self.email = email.lower()
    self.set_password(password)
     
  def set_password(self, password):
    self.pwd_hash = generate_password_hash(password)
   
  def check_password(self, password):
    return check_password_hash(self.pwd_hash, password)

class Coach(LoginBase):
  coach_id = db.Column(db.Integer, primary_key=True)

  clients = db.relationship('Customer')
  schedule = db.relationship('CoachAvailabilitySlot', order_by = 'asc(CoachAvailabilitySlot.window_start_utc)', lazy='dynamic')

  def get_upcoming_availability(self):
    return self.schedule.filter_by(
      customer_id = None).filter(
        CoachAvailabilitySlot.window_start_utc > current_datetime).all()

class Customer(LoginBase):
  customer_id = db.Column(db.Integer, primary_key=True)

  coach = db.relationship('Coach')
  coach_id = db.Column(db.Integer, db.ForeignKey('coach.coach_id'))

  appointments = db.relationship('CoachAvailabilitySlot', order_by = 'asc(CoachAvailabilitySlot.window_start_utc)')

  def set_coach(self, email):     
    self.coach_id = Coach.query.filter_by(email = email).first().coach_id

class CoachAvailabilitySlot(EntityBase):
  slot_id = db.Column(db.Integer, primary_key=True)

  coach = db.relationship('Coach')
  coach_id = db.Column(db.Integer, db.ForeignKey('coach.coach_id'))
  window_start_utc = db.Column(db.DateTime, db.CheckConstraint('window_start_utc > now()', name = 'coach_availability_slot_window_start_utc_check'))
  customer = db.relationship('Customer')
  customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
  __table_args__ = (db.UniqueConstraint('coach_id', 'window_start_utc', name = 'coach_availability_slot_coach_id_window_start_utc_key'),)
   
  def __init__(self, coach_id, window_start_utc):
    self.coach_id = coach_id
    self.window_start_utc = window_start_utc

  def set_customer(self, customer_id):
    self.customer_id = customer_id

  def get_window_end(self):
    return self.window_start_utc + appointment_slot_length_in_hours
  
  def get_window_display_text(self):
    return self.__format_date__(self.window_start_utc) + ': ' + self.__format_time__(self.window_start_utc) + ' - ' + self.__format_time__(self.get_window_end())

  def __format_date__(self, datetime):
    return datetime.strftime("%m/%d/%Y")

  def __format_time__(self, datetime):
    return datetime.strftime("%I:%M%p")