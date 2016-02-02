import sys

from datetime import datetime

from flask import Flask, render_template, redirect, url_for, session, jsonify
from flask.ext.api import status

from arivale_scheduling import app, current_datetime, appointment_slot_length_in_hours
from arivale_scheduling.forms import CoachSignupForm, CoachSigninForm
from arivale_scheduling.models import db, Coach, Customer, CoachAvailabilitySlot
from arivale_scheduling.views_base import *

#####################################################################################
# Web routes
#####################################################################################
@app.route('/coach')
def coach_landing():
  return render_landing(Coach)

@app.route('/coach/signup', methods=['GET', 'POST'])
def coach_signup():
  return render_signup(Coach, CoachSignupForm)

@app.route('/coach/signin', methods=['GET', 'POST'])
def coach_signin():
  return render_signin(Coach, CoachSigninForm)

@app.route('/coach/signout', methods=['GET', 'POST'])
def coach_signout():
  return render_signout(Coach)

@app.route('/coach/profile')
def coach_profile():
  if 'coach_email' not in session:
    return redirect(url_for('coach_signin'))
 
  coach = Coach.query.filter_by(email = session['coach_email']).first()

  if coach is None:
    return redirect(url_for('coach_signin'))

  slots_for_ux = get_coach_availability_slots_for_ux(coach.schedule)
        
  return render_template(
    'coach_profile.html',
    title='Coach Profile',
    year=get_current_year(),
    current_datetime = current_datetime,
    user = coach,
    time_slot_generator = get_timeslot_list_generator(range(8, 18)),
    slots_for_ux = slots_for_ux,
    existing_clients = coach.clients,
    potential_clients = Customer.query.filter_by(coach_id = None).all())

#####################################################################################
# API routes
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
        slot = CoachAvailabilitySlot(coach_id, availability_datetime_start)

        db.session.add(slot)
        db.session.commit()
        
        resp = jsonify({ 'id' : slot.slot_id, 'display_text': slot.get_window_display_text() });
        resp.status_code = 200
        return resp

      except:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR      

  return status_code_response(status_code)

def get_potential_availability_slot_overlap(availability_datetime, slots_by_coach):
  return slots_by_coach.filter(
    CoachAvailabilitySlot.window_start_utc <= availability_datetime, 
    (CoachAvailabilitySlot.window_start_utc + appointment_slot_length_in_hours) >= availability_datetime).first()