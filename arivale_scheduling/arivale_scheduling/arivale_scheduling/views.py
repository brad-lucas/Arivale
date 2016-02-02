import sys

from flask import Flask, render_template

from arivale_scheduling import app
from arivale_scheduling.views_base import *

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

# break up into separate files for easier modification
import arivale_scheduling.customer_views
import arivale_scheduling.coach_views
import arivale_scheduling.appointment_api_views