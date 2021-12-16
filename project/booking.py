from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from datetime import datetime

from flask_login import login_required, current_user
from .forms import ReservationForm
from .models import db, Reservation, User
from . import NO_OF_ROOMS, OPEN_HOURS
import json

booking_bp = Blueprint('booking', __name__, url_prefix='/booking')

@booking_bp.route('/')
def index():
    reservation = Reservation.query.all()
    return render_template('booking/index.html', records=reservation)

def get_participants():
    participants = db.session.query(User.username, User.name).all()
    return participants

def get_reservations():
    reservations = {}
    for r in db.session.query(Reservation).all():
        reservations[r.id] = {
            'room_id' : r.room_id,
            'username ':r.username ,
            'room_id':r.room_id,
            'booking_time':r.booking_time,
            'booked_date ':r.booked_date ,
            'time_start ':r.time_start,
            'time_end':r.time_end,
            'participants':r.participants
        }
    return reservations

@booking_bp.route('/book', methods=('GET', 'POST'))
@login_required
def book():
    form = ReservationForm()
    party_list = [p for p in get_participants() if (p[0] != current_user.username)]
    form.participants.choices = [p[1] for p in party_list]

    if request.method == 'POST' and form.validate_on_submit():
        party_username = []
        for p_form in form.participants.data:
            party_username.append(party_list[[p[1] for p in party_list].index(p_form)])

        print(party_username)

        reservation = Reservation(
                current_user.username, 
                form.room_id.data, 
                datetime.now(), 
                form.booked_date.data, 
                form.time_start.data, 
                form.time_end.data, 
                party_username
                )

        if check_availability(form.room_id.data, form.booked_date.data, form.time_start.data, form.time_end.data):
            db.session.add(reservation)
            db.session.commit()
            return redirect(url_for('booking.index'))

        flash(f'Room {form.room_id.data} is unavailable on {form.booked_date.data} at {form.time_start.data} - {form.time_end.data}')
    # else:
    #     form.booked_date.default = record.booked_date
    #     form.time_start.default = record.time_start
    #     form.time_end.default = record.time_end
    #     form.process()

    return render_template('booking/book.html', form=form, participants=party_list, hours=OPEN_HOURS, no_of_rooms=NO_OF_ROOMS)
    
# def get_reservation(id, check_author=True):
#     reservation = get_db().execute(
#         'SELECT r.id, room_id, time_begin, time_end, book_time, user_id, username'
#         ' FROM reservation r JOIN user u ON r.user_id = u.id'
#         ' WHERE r.id = ?',
#         (id,)
#     ).fetchone()

#     if reservation is None:
#         abort(404, f"Reservation id {id} doesn't exist.")

#     if check_author and reservation['user_id'] != g.user['id']:
#         abort(403)

#     return reservation

def check_availability(room_id, booked_date, time_start,time_end, edit_id=None):
    # records = db.session.query(Reservation).filter_by(booked_date=booked_date).all()
    records = db.session.query(Reservation).filter(Reservation.booked_date==booked_date).all()

    if edit_id != None:
        records = db.session.query(Reservation).filter(Reservation.id!=edit_id, Reservation.booked_date==booked_date).all()

    for rec in records:
        if rec.room_id == room_id \
             and (rec.time_start >= time_start and time_start <= rec.time_end) \
             and (rec.time_start >= time_end and time_end <= rec.time_end):
            return False
    return True

@booking_bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    record = db.session.query(Reservation).filter(Reservation.id==id).first()
    
    form = ReservationForm()
    

    if request.method == 'POST' and form.is_submitted():

        if check_availability(form.room_id.data, form.booked_date.data, form.time_start.data, form.time_end.data, id):
            db.session.query(Reservation).filter(Reservation.id==id).update(
                dict(room_id=form.room_id.data,
                    booked_date=form.booked_date.data,
                    time_start=form.time_start.data,
                    time_end=form.time_end.data))
            db.session.commit()
            return redirect(url_for('booking.index'))
        else:
            flash(f'Room {form.room_id.data} is unavailable on {form.booked_date.data} at {form.time_start.data} - {form.time_end.data}')

            
        return redirect(url_for('booking.index'))
    else:
        form.room_id.default = record.room_id
        form.booked_date.default = record.booked_date
        form.time_start.default = record.time_start
        form.time_end.default = record.time_end
        form.process()

    # return render_template('booking/edit.html', reservation=reservation)
    return render_template('booking/edit.html', record=record, form=form)

@booking_bp.route('/<int:id>/cancel', methods=('POST','GET'))
@login_required
def cancel(id):
    db.session.query(Reservation).filter(Reservation.id==id).delete()
    db.session.commit()

    return redirect(url_for('booking.index'))


@booking_bp.route('status', methods=('GET', ))
def status():
    records = get_reservations()
    return render_template('status.html', hours=OPEN_HOURS, no_of_rooms=NO_OF_ROOMS, records=json.dumps(records, default=str))