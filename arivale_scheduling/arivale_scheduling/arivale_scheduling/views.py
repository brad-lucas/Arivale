"""
Routes and views for the flask application.
"""

from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask.ext.api import status

from arivale_scheduling import app
from arivale_scheduling.forms import CoachSignupForm, UserSignupForm, CoachSigninForm, UserSigninForm
from arivale_scheduling.models import db, Coach, User

def getCurrentYear():
    return datetime.now().year

@app.route('/')
@app.route('/home')
def default_landing():
    """Renders the default landing page."""
    return render_template('default_landing.html',
        title='Home',
        year=getCurrentYear(),
        message='What an awesome page for Arivale!')

@app.route('/user')
def user_landing():
    """Renders the user landing page."""
    return render_template('user_landing.html',
        title='User',
        year=getCurrentYear(),
        message='What an awesome page for Arivale users!')

@app.route('/user/signup', methods=['GET', 'POST'])
def user_signup():
  if 'user_email' in session:
    return redirect(url_for('user_profile'))
     
  form = UserSignupForm()
   
  if request.method == 'POST':
    if form.validate() == False:
      return render_template('user_signup.html',
        title='User Sign Up',
        year=getCurrentYear(), 
        form=form)

    else:   
      newuser = User(form.firstname.data, form.lastname.data, form.email.data, form.password.data)
      db.session.add(newuser)
      db.session.commit()

      session['user_email'] = newuser.email;
      return redirect(url_for('user_profile'))
   
  elif request.method == 'GET':
    return render_template('user_signup.html',
        title='User Sign Up',
        year=getCurrentYear(), 
        form=form)

@app.route('/user/signin', methods=['GET', 'POST'])
def user_signin():
  if 'user_email' in session:
    return redirect(url_for('user_profile'))

  form = UserSigninForm()
   
  if request.method == 'POST':
    if form.validate() == False:
      return render_template('user_signin.html', 
        title='User Sign In',
        year=getCurrentYear(), 
        form=form)

    else:
      session['user_email'] = form.email.data
      return redirect(url_for('user_profile'))
                 
  elif request.method == 'GET':
    return render_template('user_signin.html', 
        title='User Sign In',
        year=getCurrentYear(), 
        form=form)

@app.route('/user/signout', methods=['GET', 'POST'])
def user_signout():
    if 'user_email' not in session:
        return redirect(url_for('user_signin'))

    session.pop('user_email', None)
    return redirect(url_for('user_landing'))

@app.route('/user/profile')
def user_profile():
  if 'user_email' not in session:
    return redirect(url_for('user_signin'))
 
  user = User.query.filter_by(email = session['user_email']).first()
 
  if user is None:
    return redirect(url_for('user_signin'))
  else:
    return render_template('user_profile.html',
        title='User Profile',
        year=getCurrentYear())

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

    else:   
      newuser = Coach(form.firstname.data, form.lastname.data, form.email.data, form.password.data)
      db.session.add(newuser)
      db.session.commit()

      session['coach_email'] = newuser.email;
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

    else:
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

  else:
    potential_clients = User.query.filter_by(coachid = None)

    return render_template('coach_profile.html',
        title='Coach Profile',
        year=getCurrentYear(),
        existing_clients=coach.clients,
        potential_clients=potential_clients)

@app.route('/coach/add_client/<int:client_id>', methods=['POST'])
def coach_add_client(client_id):  
  user = User.query.filter_by(uid = client_id).first()

  if user.coachid is None:
    try:
      coach = Coach.query.filter_by(email = session['coach_email']).first()
      user.coachid = coach.uid
      db.session.add(user)
      db.session.commit()
      return status.HTTP_200_OK
    
    except:
      return status.HTTP_500_INTERNAL_SERVER_ERROR
  else:
    return status.HTTP_409_CONFLICT