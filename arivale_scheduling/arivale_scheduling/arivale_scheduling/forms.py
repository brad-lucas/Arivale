from flask.ext.wtf import Form
from wtforms import validators
from wtforms.fields import TextField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import ValidationError
from arivale_scheduling.models import db, Coach, Customer

class CustomerInfoFormBase(Form):
  email = TextField("Email", [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
   
  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)
    
  def getClass(self):
    raise NotImplementedError("Please Implement this method")
    
  def performValidate(self, customer):
    raise NotImplementedError("Please Implement this method")

  def validate(self):
    if not Form.validate(self):
      return False
    
    customer = self.getClass().query.filter_by(email = self.email.data.lower()).first()

    return self.performValidate(customer)

class SignupFormBase(CustomerInfoFormBase):
  first_name = TextField("First name", [validators.Required("Please enter your first name.")])
  last_name = TextField("Last name", [validators.Required("Please enter your last name.")])
  submit = SubmitField("Create account")
   
  def __init__(self, *args, **kwargs):
    CustomerInfoFormBase.__init__(self, *args, **kwargs)
 
  def performValidate(self, customer):
    if not customer:
      return True
  
    self.email.errors.append("That email is already taken")
    return False

class CoachSignupForm(SignupFormBase):    
  def getClass(self):
    return Coach

class CustomerSignupForm(SignupFormBase): 
  def getClass(self):
    return Customer

class SignInFormBase(CustomerInfoFormBase):
  submit = SubmitField("Sign In")
   
  def __init__(self, *args, **kwargs):
    CustomerInfoFormBase.__init__(self, *args, **kwargs)
 
  def performValidate(self, customer):
    if customer and customer.check_password(self.password.data):
      return True
    
    self.email.errors.append("Invalid e-mail or password")
    return False

class CoachSigninForm(SignInFormBase):   
  def getClass(self):
    return Coach

class CustomerSigninForm(SignInFormBase):
  def getClass(self):
    return Customer