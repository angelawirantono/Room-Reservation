from flask_wtf import FlaskForm
from wtforms import Field, StringField, PasswordField, RadioField, SelectField, BooleanField, SelectMultipleField
import wtforms
from wtforms.fields.datetime import DateField, TimeField
from wtforms.fields.list import FieldList
from wtforms.validators import DataRequired, Email
from wtforms.widgets.core import ListWidget, TextInput, CheckboxInput
from datetime import datetime

class RegisterForm(FlaskForm):
    username = StringField(u'username', validators=[DataRequired()])
    name = StringField(u'name', validators=[DataRequired()])
    email = StringField(u'email', validators=[DataRequired(), Email()])
    password = PasswordField(u'password', validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField(u'username', validators=[DataRequired()])
    password = PasswordField(u'password', validators=[DataRequired()])

class ReservationForm(FlaskForm):
    room_id = RadioField(u'room', choices=[('1', 'room1'), ('2', 'room2'), ('3', 'room3')], validators=[DataRequired()], widget=ListWidget())
    booked_date = DateField(u'current_date', default=datetime.today, validators=[DataRequired()])
    time_start = TimeField(u'start_time', default=datetime.now(), validators=[DataRequired()])
    time_end = TimeField(u'start_time', default=datetime.now(), validators=[DataRequired()])
    participants = SelectMultipleField(u'participants', widget=ListWidget(prefix_label=True), option_widget=CheckboxInput())
    
