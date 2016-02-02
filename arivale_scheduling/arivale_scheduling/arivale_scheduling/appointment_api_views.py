import sys

from flask import Flask, session
from flask.ext.api import status

from arivale_scheduling import app
from arivale_scheduling.models import db, Customer, CoachAvailabilitySlot
from arivale_scheduling.views_base import *

#####################################################################################
# Appointment API routes
#####################################################################################
@app.route('/appointments/book/<int:availability_slot_id>', methods=['POST'])
def book_appointment(availability_slot_id):
  return set_appointment_customer(availability_slot_id, Customer.query.filter_by(email = session['customer_email']).first().customer_id)

@app.route('/appointments/cancel/<int:availability_slot_id>', methods=['POST'])
def cancel_appointment(availability_slot_id):  
  return set_appointment_customer(availability_slot_id, None)

def set_appointment_customer(availability_slot_id, customer_id):  
  return perform_appointment_operation(
    availability_slot_id, 
    lambda availability_slot: availability_slot.set_customer(customer_id))

@app.route('/appointments/delete/<int:availability_slot_id>', methods=['POST'])
def delete_appointment(availability_slot_id):  
  return perform_appointment_operation(
    availability_slot_id, 
    lambda availability_slot: db.session.delete(availability_slot))

def perform_appointment_operation(availability_slot_id, operation):  
  availability_slot = CoachAvailabilitySlot.query.filter_by(slot_id = availability_slot_id).first()

  status_code = None

  if availability_slot is None:
    status_code = status.HTTP_404_NOT_FOUND

  else:
    try:
      operation(availability_slot)
      db.session.commit()
      status_code = status.HTTP_200_OK
    
    except:
      status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

  return status_code_response(status_code)