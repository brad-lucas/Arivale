"""
Routes and views for the flask application.
"""

from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask.ext.api import status

from arivale_scheduling import app
from arivale_scheduling.forms import CoachSignupForm, CustomerSignupForm, CoachSigninForm, CustomerSigninForm
from arivale_scheduling.models import db, Coach, Customer, CoachAvailabilitySlot

#####################################################################################
# helper methods
#####################################################################################

def emptyResponseWithStatusCode(status_code):
  return render_template('empty.html'), status_code

def getCurrentDatetime():
  return datetime.now()

def getCurrentYear():
  return getCurrentDatetime().year

#####################################################################################
# default routes
#####################################################################################

@app.route('/')
@app.route('/home')
def default_landing():
    """Renders the default landing page."""
    return render_template('default_landing.html',
        title='Home',
        year=getCurrentYear(),
        message='What an awesome page for Arivale!')

#####################################################################################
# Customer web routes
#####################################################################################

@app.route('/customer')
def customer_landing():
    """Renders the customer landing page."""
    return render_template('customer_landing.html',
        title='Customer',
        year=getCurrentYear(),
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
        year=getCurrentYear(), 
        form=form)

    newcustomer = Customer(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
    db.session.add(newcustomer)
    db.session.commit()

    session['customer_email'] = newcustomer.email;
    return redirect(url_for('customer_profile'))
   
  elif request.method == 'GET':
    return render_template('customer_signup.html',
        title='Customer Sign Up',
        year=getCurrentYear(), 
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
        year=getCurrentYear(), 
        form=form)

    session['customer_email'] = form.email.data
    return redirect(url_for('customer_profile'))
                 
  elif request.method == 'GET':
    return render_template('customer_signin.html', 
        title='Customer Sign In',
        year=getCurrentYear(), 
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
  
  return render_template('customer_profile.html',
      title='Customer Profile',
      year=getCurrentYear())

#####################################################################################
# Coach web routes
#####################################################################################

@app.route('/coach')
def coach_landing():
    """Renders the coach landing page."""
    return render_template('coach_landing.html',
        title='Coach',
        year=getCurrentYear(),
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
        year=getCurrentYear(), 
        form=form)

    newcustomer = Coach(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
    db.session.add(newcustomer)
    db.session.commit()

    session['coach_email'] = newcustomer.email;
    return redirect(url_for('coach_profile'))
   
  elif request.method == 'GET':
    return render_template('coach_signup.html',
        title='Coach Sign Up',
        year=getCurrentYear(), 
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
        year=getCurrentYear(), 
        form=form)

    session['coach_email'] = form.email.data
    return redirect(url_for('coach_profile'))
                 
  elif request.method == 'GET':
    return render_template('coach_signin.html', 
        title='Coach Sign In',
        year=getCurrentYear(), 
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

  past_slots_for_ux = []
  booked_slots_for_ux = []
  availability_slots_for_ux = []
  current_datetime = getCurrentDatetime()

  for availability_slot in coach.availability_slots:
      slot_datetime = availability_slot.window_start_utc
      
      slot_value_dictionary = {}
      slot_value_dictionary['id'] = availability_slot.slot_id
      slot_value_dictionary['start_timestamp_str'] = slot_datetime.strftime("%Y-%m-%d %H:%M:%S")
      
      if slot_datetime > current_datetime:
        if availability_slot.customer_id is None:
          availability_slots_for_ux.append(slot_value_dictionary)
        else:
          booked_slots_for_ux.append(slot_value_dictionary)
      else:
        past_slots_for_ux.append(slot_value_dictionary)
        
  return render_template('coach_profile.html',
      title='Coach Profile',
      year=getCurrentYear(),
      past_slots = past_slots_for_ux,
      booked_slots = booked_slots_for_ux,
      availability_slots = availability_slots_for_ux,
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
      customer.coach_id = Coach.query.filter_by(email = session['coach_email']).first().coach_id
      db.session.update(customer)
      db.session.commit()
      status_code = status.HTTP_200_OK

    except:
      status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

  else:
    # someone else added the client before this request
    status_code = status.HTTP_409_CONFLICT

  return emptyResponseWithStatusCode(status_code)

@app.route('/coach/availability/cancel/<int:availability_slot_id>', methods=['POST'])
def coach_cancel_appointment(availability_slot_id):  
  availability_slot = CoachAvailabilitySlot.query.filter_by(slot_id = availability_slot_id).first()

  status_code = None

  if availability_slot is None:
    status_code = status.HTTP_404_NOT_FOUND

  else:
    try:
      db.session.delete(availability_slot)
      db.session.commit()
      status_code = status.HTTP_200_OK
    
    except:
      status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

  return emptyResponseWithStatusCode(status_code)