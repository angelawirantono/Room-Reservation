from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from datetime import datetime

from flask_login import login_required, current_user
from .forms import ReservationForm
from .models import db, Reservation

bp = Blueprint('booking', __name__, url_prefix='/booking')

@bp.route('/')
def index():
    reservation = Reservation.query.all()
    return render_template('booking/index.html', records=reservation)

@bp.route('/book', methods=('GET', 'POST'))
@login_required
def book():
    form = ReservationForm()
    if request.method == 'POST' and form.validate_on_submit():
        reservation = Reservation(
                current_user.id, 
                form.room_id.data, 
                datetime.now(), 
                form.booked_date.data, 
                form.time_start.data, 
                form.time_end.data
                )

        if check_availability(form.room_id.data, form.booked_date.data, form.time_start.data, form.time_end.data):
            
            db.session.add(reservation)
            db.session.commit()
            return redirect(url_for('booking.index'))

        flash(f'Room {form.room_id.data} is unavailable on {form.booked_date.data} at {form.time_start.data} - {form.time_end.data}')

    return render_template('booking/book.html', form=form)
    
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

def check_availability(room_id, booked_date, time_start,time_end):
    records = db.session.query(Reservation).filter_by(booked_date=booked_date).all()
    for rec in records:
        if rec.room_id == room_id \
             and (rec.time_start >= time_start and time_start <= rec.time_start) \
             and (rec.time_end >= time_end and time_end <= rec.time_end):
            return False
    return True

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit():    
            #return redirect(url_for('booking.index'))

    # return render_template('booking/edit.html', reservation=reservation)
    return render_template('booking/edit.html')

# @bp.route('/<int:id>/delete', methods=('POST',))
# @login_required
# def delete(id):
#     get_reservation(id)
#     db = get_db()
#     db.execute('DELETE FROM reservation WHERE id = ?', (id,))
#     db.commit()
#     return redirect(url_for('booking.index'))
