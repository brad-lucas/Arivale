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
  return render_profile(Customer, lambda customer: customer.appointments, None)