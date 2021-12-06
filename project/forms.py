from flask_wtf import FlaskForm
from sqlalchemy.orm import defaultload
from wtforms import StringField, PasswordField, RadioField
from wtforms.fields.datetime import DateField, DateTimeField, TimeField
from wtforms.validators import DataRequired, Email
import datetime

class RegisterForm(FlaskForm):
    username = StringField(u'username', validators=[DataRequired()])
    name = StringField(u'name', validators=[DataRequired()])
    email = StringField(u'email', validators=[DataRequired(), Email()])
    password = PasswordField(u'password', validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField(u'username', validators=[DataRequired()])
    password = PasswordField(u'password', validators=[DataRequired()])

class ReservationForm(FlaskForm):
    room_id = RadioField(u'room', choices=[('1', 'room1'), ('2', 'room2'), ('3', 'room3')], validators=[DataRequired()])
    booked_date = DateField(u'current_date', validators=[DataRequired()])
    time_start = TimeField(u'start_time', validators=[DataRequired()])
    time_end = TimeField(u'start_time', validators=[DataRequired()])
