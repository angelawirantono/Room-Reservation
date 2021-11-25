from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from reservation_sys.auth import login_required
from reservation_sys.db import get_db

bp = Blueprint('booking', __name__)

@bp.route('/')
def index():
    db = get_db()
    reservation = db.execute(
        'SELECT r.id, room_id, time_begin, time_end, book_time, user_id, username'
        ' FROM reservation r JOIN user u ON r.user_id = u.id'
        ' ORDER BY book_time DESC'
    ).fetchall()
    return render_template('booking/index.html', records=reservation)

@bp.route('/book', methods=('GET', 'POST'))
@login_required
def book():
    if request.method == 'POST':
        time_begin = request.form['time_begin']
        time_end = request.form['time_end']
        booked_date = request.form['booked_date']
        room_id = request.form['optionsRadios']
        error = None

        if not room_id:
            error = 'Room option is required'
        elif not booked_date:
            error = 'Date is required.'
        elif not time_begin:
            error = 'Starting time is required.'
        elif not time_end:
            error = 'Ending time is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO reservation (room_id, booked_date, time_begin, time_end, user_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (room_id, booked_date, time_begin, time_end, g.user['id'])
            )
            db.commit()
            return redirect(url_for('booking.index'))

    return render_template('booking/book.html')

def get_reservation(id, check_author=True):
    reservation = get_db().execute(
        'SELECT r.id, room_id, time_begin, time_end, book_time, user_id, username'
        ' FROM reservation r JOIN user u ON r.user_id = u.id'
        ' WHERE r.id = ?',
        (id,)
    ).fetchone()

    if reservation is None:
        abort(404, f"Reservation id {id} doesn't exist.")

    if check_author and reservation['user_id'] != g.user['id']:
        abort(403)

    return reservation

def check_availability():
    to_check = get_db().execute(
        'SELECT room_id, time_begin, time_end'
        ' FROM '
    )
    pass

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(user_id):    

    db = get_db()
    db.execute(
        'SELECT room_id, time_begin, time_end, book_time'
        ' FROM reservation r'
        ' WHERE user_id = ?'
        (user_id,)
    ).fetchall()

    if request.method == 'POST':
        time_begin = request.form['time_begin']
        time_end = request.form['time_end']
        room_id = request.form['room_id']
        error = None

        if not room_id:
            error = 'Room ID is required.'
        elif not time_begin:
            error = 'Starting time is required.'
        elif not time_end:
            error = 'Ending time is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE reservation SET room_id = ?, time_begin = ?,  time_end = ?'
                ' WHERE id = ?',
                (room_id, time_begin, time_end, id)
            )
            db.commit()
            return redirect(url_for('booking.index'))

    return render_template('booking/edit.html', reservation=reservation)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_reservation(id)
    db = get_db()
    db.execute('DELETE FROM reservation WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('booking.index'))
