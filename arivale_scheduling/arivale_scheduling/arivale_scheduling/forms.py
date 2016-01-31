from flask.ext.wtf import Form
from wtforms import validators
from wtforms.fields import TextField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import ValidationError
from arivale_scheduling.models import db, Coach, User

class UserInfoFormBase(Form):
  email = TextField("Email", [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
   
  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)
    
  def getClass(self):
    raise NotImplementedError("Please Implement this method")
    
  def performValidate(self, user):
    raise NotImplementedError("Please Implement this method")

  def validate(self):
    if not Form.validate(self):
      return False
    
    user = self.getClass().query.filter_by(email = self.email.data.lower()).first()

    return self.performValidate(user)

class SignupFormBase(UserInfoFormBase):
  firstname = TextField("First name", [validators.Required("Please enter your first name.")])
  lastname = TextField("Last name", [validators.Required("Please enter your last name.")])
  submit = SubmitField("Create account")
   
  def __init__(self, *args, **kwargs):
    UserInfoFormBase.__init__(self, *args, **kwargs)
 
  def performValidate(self, user):
    if not user:
      return True
  
    self.email.errors.append("That email is already taken")
    return False

class CoachSignupForm(SignupFormBase):    
  def getClass(self):
    return Coach

class UserSignupForm(SignupFormBase): 
  def getClass(self):
    return User

class SignInFormBase(UserInfoFormBase):
  submit = SubmitField("Sign In")
   
  def __init__(self, *args, **kwargs):
    UserInfoFormBase.__init__(self, *args, **kwargs)
 
  def performValidate(self, user):
    if user and user.check_password(self.password.data):
      return True
    
    self.email.errors.append("Invalid e-mail or password")
    return False

class CoachSigninForm(SignInFormBase):   
  def getClass(self):
    return Coach

class UserSigninForm(SignInFormBase):
  def getClass(self):
    return User