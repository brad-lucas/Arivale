"""
Routes and views for the flask application.
"""

import sys

from datetime import datetime, timedelta

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask.ext.api import status

from flask_sqlalchemy import get_debug_queries

from arivale_scheduling import app, current_datetime, appointment_slot_length_in_hours
from arivale_scheduling.forms import CoachSignupForm, CustomerSignupForm, CoachSigninForm, CustomerSigninForm
from arivale_scheduling.models import db, Coach, Customer, CoachAvailabilitySlot

#####################################################################################
# helper methods
#####################################################################################

def status_code_response(status_code):
  return render_template('empty.html'), status_code

def get_current_year():
  return current_datetime.year

def get_timeslot_list_generator(range_of_hours):
  for hour in range_of_hours:
    zero_padded_hour = str(hour).zfill(2)
    yield zero_padded_hour + ':00:00'
    yield zero_padded_hour + ':30:00'

def get_coach_availability_slots_for_ux(coach_availability_slots):  
  past = []
  booked = []
  upcoming = []

  for slot in coach_availability_slots:
      slot_datetime_start = slot.window_start_utc
      
      slot_value_dictionary = {}
      slot_value_dictionary['id'] = slot.slot_id
      slot_value_dictionary['display_text'] = slot.get_window_display_text()
      
      if slot_datetime_start > current_datetime:
        if slot.customer_id is None:
          upcoming.append(slot_value_dictionary)
        else:
          booked.append(slot_value_dictionary)
      else:
        past.append(slot_value_dictionary)

  timeslots_for_ux = {}
  timeslots_for_ux['past'] = past
  timeslots_for_ux['booked'] = booked
  timeslots_for_ux['upcoming'] = upcoming

  return timeslots_for_ux

#####################################################################################
# default routes
#####################################################################################
@app.route('/')
@app.route('/home')
def default_landing():
    """Renders the default landing page."""
    return render_template('default_landing.html',
        title='Home',
        year=get_current_year(),
        message='What an awesome page for Arivale!')

#####################################################################################
# Customer web routes
#####################################################################################
@app.route('/customer')
def customer_landing():
    """Renders the customer landing page."""
    return render_template('customer_landing.html',
        title='Customer',
        year=get_current_year(),
        message='What an awesome page for Arivale customers!')

@app.route('/customer/signup', methods=['GET', 'POST'])
def customer_signup():
  if 'customer_email' in session:
    return redirect(url_for('customer_profile'))
     
  form = CustomerSignupForm()
   
  if request.method == 'POST':
    if form.validate() == False:
      return render_template('customer_signup.html',
        title='Customer Sign Up',
        year=get_current_year(), 
        form=form)

    newcustomer = Customer(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
    db.session.add(newcustomer)
    db.session.commit()

    session['customer_email'] = newcustomer.email
    return redirect(url_for('customer_profile'))
   
  elif request.method == 'GET':
    return render_template('customer_signup.html',
        title='Customer Sign Up',
        year=get_current_year(), 
        form=form)

@app.route('/customer/signin', methods=['GET', 'POST'])
def customer_signin():
  if 'customer_email' in session:
    return redirect(url_for('customer_profile'))

  form = CustomerSigninForm()
   
  if request.method == 'POST':
    if form.validate() == False:
      return render_template('customer_signin.html', 
        title='Customer Sign In',
        year=get_current_year(), 
        form=form)

    session['customer_email'] = form.email.data
    return redirect(url_for('customer_profile'))
                 
  elif request.method == 'GET':
    return render_template('customer_signin.html', 
        title='Customer Sign In',
        year=get_current_year(), 
        form=form)

@app.route('/customer/signout', methods=['GET', 'POST'])
def customer_signout():
    if 'customer_email' not in session:
        return redirect(url_for('customer_signin'))

    session.pop('customer_email', None)
    return redirect(url_for('customer_landing'))

@app.route('/customer/profile')
def customer_profile():
  if 'customer_email' not in session:
    return redirect(url_for('customer_signin'))
 
  customer = Customer.query.filter_by(email = session['customer_email']).first()
 
  if customer is None:
    return redirect(url_for('customer_signin'))

  slots_for_ux = get_coach_availability_slots_for_ux(customer.appointments)
  
  return render_template('customer_profile.html',
      title='Customer Profile',
      year=get_current_year(),
      current_datetime = current_datetime,
      customer = customer,
      slots_for_ux = slots_for_ux)

#####################################################################################
# Coach web routes
#####################################################################################
@app.route('/coach')
def coach_landing():
    """Renders the coach landing page."""
    return render_template('coach_landing.html',
        title='Coach',
        year=get_current_year(),
        message='What an awesome page for Arivale coaches!')

@app.route('/coach/signup', methods=['GET', 'POST'])
def coach_signup():
  if 'coach_email' in session:
    return redirect(url_for('coach_profile'))
     
  form = CoachSignupForm()
   
  if request.method == 'POST':
    if form.validate() == False:
      return render_template('coach_signup.html',
        title='Coach Sign Up',
        year=get_current_year(), 
        form=form)

    newcustomer = Coach(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
    db.session.add(newcustomer)
    db.session.commit()

    session['coach_email'] = newcustomer.email
    return redirect(url_for('coach_profile'))
   
  elif request.method == 'GET':
    return render_template('coach_signup.html',
        title='Coach Sign Up',
        year=get_current_year(), 
        form=form)

@app.route('/coach/signin', methods=['GET', 'POST'])
def coach_signin():
  if 'coach_email' in session:
    return redirect(url_for('coach_profile'))

  form = CoachSigninForm()
   
  if request.method == 'POST':
    if form.validate() == False:
      return render_template('coach_signin.html', 
        title='Coach Sign In',
        year=get_current_year(), 
        form=form)

    session['coach_email'] = form.email.data
    return redirect(url_for('coach_profile'))
                 
  elif request.method == 'GET':
    return render_template('coach_signin.html', 
        title='Coach Sign In',
        year=get_current_year(), 
        form=form)

@app.route('/coach/signout', methods=['GET', 'POST'])
def coach_signout():
    if 'coach_email' not in session:
        return redirect(url_for('coach_signin'))

    session.pop('coach_email', None)
    return redirect(url_for('coach_landing'))

@app.route('/coach/profile')
def coach_profile():
  if 'coach_email' not in session:
    return redirect(url_for('coach_signin'))
 
  coach = Coach.query.filter_by(email = session['coach_email']).first()

  if coach is None:
    return redirect(url_for('coach_signin'))

  slots_for_ux = get_coach_availability_slots_for_ux(coach.schedule)
        
  return render_template('coach_profile.html',
      title='Coach Profile',
      year=get_current_year(),
      current_datetime = current_datetime,
      time_slot_generator = get_timeslot_list_generator(range(8, 18)),
      slots_for_ux = slots_for_ux,
      existing_clients = coach.clients,
      potential_clients = Customer.query.filter_by(coach_id = None).all())

#####################################################################################
# Coach API routes
#####################################################################################
@app.route('/coach/clients/add/<int:client_id>', methods=['POST'])
def coach_add_client(client_id):  
  customer = Customer.query.filter_by(customer_id = client_id).first()

  status_code = None

  if customer is None:
    status_code = status.HTTP_404_NOT_FOUND

  elif customer.coach_id is None:
    try:
      customer.set_coach(session['coach_email'])
      db.session.commit()
      status_code = status.HTTP_200_OK

    except:
      status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

  else:
    # someone else added the client before this request
    status_code = status.HTTP_409_CONFLICT

  return status_code_response(status_code)

@app.route('/coach/availability/add/<datetime_str>', methods=['POST'])
def coach_add_availability(datetime_str):
  availability_datetime_start = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
  availability_datetime_end = availability_datetime_start + appointment_slot_length_in_hours

  coach_id = Coach.query.filter_by(email = session['coach_email']).first().coach_id

  slots_by_coach = CoachAvailabilitySlot.query.filter_by(coach_id = coach_id)

  status_code = status.HTTP_409_CONFLICT
  
  availability_slot_overlap_start = get_potential_availability_slot_overlap(availability_datetime_start, slots_by_coach)  
  if availability_slot_overlap_start is None:
    availability_slot_overlap_end = get_potential_availability_slot_overlap(availability_datetime_end, slots_by_coach)
    if availability_slot_overlap_end is None:
      try:
        db.session.add(CoachAvailabilitySlot(coach_id, availability_datetime_start))
        db.session.commit()
        status_code = status.HTTP_200_OK
    
      except:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR      

  return status_code_response(status_code)

def get_potential_availability_slot_overlap(availability_datetime, slots_by_coach):
  return slots_by_coach.filter(
    CoachAvailabilitySlot.window_start_utc <= availability_datetime, 
    (CoachAvailabilitySlot.window_start_utc + appointment_slot_length_in_hours) >= availability_datetime).first()

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