import sys

from flask import Flask, render_template, redirect, url_for, session

from arivale_scheduling import app, current_datetime
from arivale_scheduling.forms import CustomerSignupForm, CustomerSigninForm
from arivale_scheduling.models import Customer
from arivale_scheduling.views_base import *

#####################################################################################
# Customer web routes
#####################################################################################
@app.route('/customer')
def customer_landing():
  return render_landing(Customer)

@app.route('/customer/signup', methods=['GET', 'POST'])
def customer_signup():
  return render_signup(Customer, CustomerSignupForm)

@app.route('/customer/signin', methods=['GET', 'POST'])
def customer_signin():
  return render_signin(Customer, CustomerSigninForm)

@app.route('/customer/signout', methods=['GET', 'POST'])
def customer_signout():
  return render_signout(Customer)

@app.route('/customer/profile')
def customer_profile():
  if 'customer_email' not in session:
    return redirect(url_for('customer_signin'))
 
  customer = Customer.query.filter_by(email = session['customer_email']).first()
 
  if customer is None:
    return redirect(url_for('customer_signin'))

  slots_for_ux = get_coach_availability_slots_for_ux(customer.appointments)
  
  return render_template(
    'customer_profile.html',
    title='Customer Profile',
    year=get_current_year(),
    current_datetime = current_datetime,
    user = customer,
    slots_for_ux = slots_for_ux)