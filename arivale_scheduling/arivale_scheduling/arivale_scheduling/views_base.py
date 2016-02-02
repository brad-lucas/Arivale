import sys

from datetime import datetime, timedelta

from flask import Flask, render_template, redirect, url_for, request, session
from flask.ext.api import status

from arivale_scheduling import app, current_datetime, appointment_slot_length_in_hours
from arivale_scheduling.models import db

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
# Base route methods
#####################################################################################
def render_landing(model_class):
  model_class_type = model_class.__name__
  model_class_type_lower = model_class_type.lower()

  return render_template(
    model_class_type_lower + '_landing.html',
    title=model_class_type,
    year=get_current_year(),
    message='What an awesome page for an Arivale ' + model_class_type_lower + ' to land!')

def render_signup(model_class, form_class):
  model_class_type = model_class.__name__
  model_class_type_lower = model_class_type.lower()

  if model_class_type_lower + '_email' in session:
    return redirect(url_for(model_class_type_lower + '_profile'))
     
  form = form_class()

  render_signup_template = lambda: render_template(
    model_class_type_lower + '_signup.html',
    title= model_class_type + ' Sign Up',
    year=get_current_year(), 
    form=form)
   
  if request.method == 'POST':
    if form.validate() == False:
      return render_signup_template()

    signed_up = model_class(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
    db.session.add(signed_up)
    db.session.commit()

    session[model_class_type_lower + '_email'] = signed_up.email
    return redirect(url_for(model_class_type_lower + '_profile'))
   
  elif request.method == 'GET':
    return render_signup_template()

def render_signin(model_class, form_class):
  model_class_type = model_class.__name__
  model_class_type_lower = model_class_type.lower()

  if model_class_type_lower + '_email' in session:
    return redirect(url_for(model_class_type_lower + '_profile'))

  form = form_class() 

  render_signin_template = lambda: render_template(
    model_class_type_lower + '_signin.html',
    title= model_class_type + ' Sign In',
    year=get_current_year(), 
    form=form)
   
  if request.method == 'POST':
    if form.validate() == False:
      return render_signin_template()

    session[model_class_type_lower + '_email'] = form.email.data
    return redirect(url_for(model_class_type_lower + '_profile'))
                 
  elif request.method == 'GET':
    return render_signin_template()

def render_signout(model_class):
  model_class_type_lower = model_class.__name__.lower()

  if model_class_type_lower + '_email' not in session:
    return redirect(url_for('_signin'))

  session.pop(model_class_type_lower + '_email', None)
  return redirect(url_for(model_class_type_lower + '_landing'))