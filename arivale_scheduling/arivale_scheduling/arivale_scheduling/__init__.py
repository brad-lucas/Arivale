"""
The flask application package.
"""

from flask import Flask
import os

app = Flask(__name__)

app.secret_key = 'development key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:admin@localhost/arivale_scheduling_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

from datetime import datetime, timedelta
current_datetime = datetime.now()
appointment_slot_length_in_hours = timedelta(hours=1)

from arivale_scheduling.models import db
db.init_app(app)

import arivale_scheduling.views