from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
from datetime import datetime, time, timedelta

from flask_login import login_required, current_user
from .forms import ReservationForm
from .models import db, Reservation, User
from config import NO_OF_ROOMS, OPEN_HOURS
from .mail import send_msg

booking_bp = Blueprint('booking', __name__)

# Routes
@booking_bp.route('/')
def home():
    return render_template('booking/home.html')

@booking_bp.route('/profile')
@login_required
def profile():
    update_records()
    records = {}
    reservations = db.session.query(Reservation).all()

    for r in reservations:
        if r.username == current_user.username:
            records.setdefault('own', []).append(r)
        elif str(f'{current_user.username}, {current_user.name}') in r.party:
            records.setdefault('partied', []).append(r)

    return render_template('booking/profile.html', records=records)

@booking_bp.route('/index')
@login_required
def index():
    update_records()
    if current_user.is_authenticated and current_user.admin:
        reservations = db.session.query(Reservation).all()
    else:
        reservations = db.session.query(Reservation).filter(Reservation.status==0).all()
    return render_template('booking/index.html', records=reservations)

@booking_bp.route('/book', methods=('GET', 'POST'))
@login_required
def book():
    form = ReservationForm()
    # get party list to be listed out as choices, exclude current_user
    party_list = [p for p in get_party() if (p[0] != current_user.username)]
    form.party.choices = [(p[0], p[1]) for p in party_list]

    if request.method == 'POST' and form.validate_on_submit():
        party_list_form = []

        for party in form.party.data:
            party_list_form.append(party_list[[p[0] for p in party_list].index(party)])

        # include current_user in meeting
        party_list_form.append((current_user.username, current_user.name))

        # parse time object from given hour integer
        time_start = time(int(form.time_start.data),0,0,0)
        time_end = time(int(form.time_end.data),0,0,0)

        reservation = Reservation(
                current_user.username, 
                form.room_id.data, 
                datetime.now(), 
                form.booked_date.data, 
                time_start, 
                time_end, 
                party_list_form
                )
        error = check_availability(form.room_id.data, form.booked_date.data, time_start, time_end)
        error = check_party_availability(form.booked_date.data, time_start, time_end, party_list_form)
        if error == '':
            db.session.add(reservation)
            db.session.commit()

            party_list_form.remove((current_user.username, current_user.name))
            emails = get_party_email(party_list_form)

            meeting_info = {
                        'date':form.booked_date.data,
                        'time_start':form.time_start.data,
                        'time_end':form.time_end.data,
                        'party':party_list_form,
                        'booking_time': datetime.now().strftime('%H:%M:%S'),
                        'host': (current_user.name, current_user.username)
                        }

            if party_list_form:
                party_msg_html = render_template('mail/invite.html', info=meeting_info, notes=form.message.data)
                send_msg('Meeting Invitation', emails, party_msg_html)
            user_msg_html = render_template('mail/success.html', info=meeting_info)
            send_msg('Reservation Booked', [current_user.email], user_msg_html)
            
            return redirect(url_for('booking.index'))
    
        flash(error)
    else:
        # Pre-populate form with current datetime
        form.time_start.default = datetime.now().strftime("%H")
        form.time_end.default = (datetime.now()+timedelta(hours=1)).strftime("%H")
        form.process()
    
    return render_template('booking/book.html', form=form, party=party_list, hours=OPEN_HOURS, no_of_rooms=NO_OF_ROOMS)

@booking_bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    prev_record = db.session.query(Reservation).filter(Reservation.id==id).first()
    print(prev_record, "EDIT ID")
    form = ReservationForm()
    party_list = [p for p in get_party() if (p[0] != current_user.username)]
    form.party.choices = [(p[0], p[1]) for p in party_list]

    if request.method == 'POST' and form.is_submitted():
        party_list_form = []

        for party in form.party.data:
            party_list_form.append(party_list[[p[0] for p in party_list].index(party)])

        # include current_user in meeting
        party_list_form.append((current_user.username, current_user.name))
        # parse time object from given hour integer
        time_start = time(int(form.time_start.data),0,0,0)
        time_end = time(int(form.time_end.data),0,0,0)

        error = check_availability(form.room_id.data, form.booked_date.data,  time_start, time_end, id)
        error = check_party_availability(form.booked_date.data, time_start, time_end, party_list_form)

        if error == '':
            db.session.query(Reservation).filter(Reservation.id==id).update(
                dict(room_id=form.room_id.data,
                    booked_date=form.booked_date.data,
                    time_start=time_start,
                    time_end=time_end))
            db.session.commit()

            # Notify party about changes made to this reservation
            party_list_form.remove((current_user.username, current_user.name))
            emails = get_party_email(party_list_form)

            meeting_info = {
                        'date':form.booked_date.data,
                        'time_start':form.time_start.data,
                        'time_end':form.time_end.data,
                        'party':party_list_form,
                        'booking_time': datetime.now().strftime('%H:%M:%S'),
                        'invitee': (current_user.name, current_user.username)
                        }

            if party_list_form:
                party_msg_html = render_template('mail/invite.html', info=meeting_info, notes=form.message.data)
                send_msg('Meeting Invitation', emails, party_msg_html)
            user_msg_html = render_template('mail/success.html', info=meeting_info)
            send_msg('Reservation Booked', [current_user.email], user_msg_html)

            return redirect(url_for('booking.index'))
        else:
            flash(f'Room {form.room_id.data} is unavailable on {form.booked_date.data} at {form.time_start.data} - {form.time_end.data}')
            
    else:
        # Pre-populate form with record's current data
        # print('PREVIOUS', prev_record.party)
        form.room_id.default = prev_record.room_id
        form.booked_date.default = prev_record.booked_date
        form.time_start.default = prev_record.time_start
        form.time_end.default = prev_record.time_end
        form.process()

        form.party.data = [p.split(',')[0] for p in prev_record.party]
        # print('\n\n\n', form.party.choices, form.party.data, form.party.name)

    # return render_template('booking/edit.html', reservation=reservation)
    return render_template('booking/edit.html', record=prev_record, form=form, party=party_list, no_of_rooms=NO_OF_ROOMS, hours=OPEN_HOURS)

@booking_bp.route('/<int:id>/cancel', methods= ('POST','GET'))
@login_required
def cancel(id):
    # party_list = db.session.query(Reservation.party).filter(Reservation.id==id).first()



    db.session.query(Reservation).filter(Reservation.id==id).delete()
    db.session.commit()

    return redirect(url_for('booking.index'))

# Route used for ajax dynamic(kinda) schedule table update
@booking_bp.route('/_get_status')
def get_status():
    date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    record = get_booked(date)
    return jsonify(record)

@booking_bp.route('/status', methods=('GET','POST'))
def status():
    update_records()
    return render_template('booking/status.html', hours=OPEN_HOURS, no_of_rooms=NO_OF_ROOMS)

# Functions to get data from DB
def get_party():
    party = db.session.query(User.username, User.name).all()
    return party

def check_availability(room_id, booked_date, time_start,time_end, edit_id=None):
    if db.session.query(Reservation).first():
        
        records = db.session.query(Reservation).filter(Reservation.booked_date==booked_date).all()

        if edit_id != None:
            records = db.session.query(Reservation).filter(Reservation.id!=edit_id, Reservation.booked_date==booked_date).all()

        for rec in records:
            if rec.room_id == room_id \
                and (rec.time_start <= time_start and time_start <= rec.time_end) \
                and (rec.time_start <= time_end and time_end <= rec.time_end):
                return f'Room {room_id} is unavailable on {booked_date} at {time_start} - {time_end}'
    return ''

def check_party_availability(booked_date, time_start, time_end, party_list):
    if db.session.query(Reservation).first():
        records = db.session.query(Reservation._party, Reservation.time_start, Reservation.time_end).filter(Reservation.booked_date==booked_date).all()
    
        for rec in records:
            for party in party_list:
                if (party[0] in rec._party) \
                    and (rec.time_start <= time_start and time_start <= rec.time_end) \
                    and (rec.time_start <= time_end and time_end <= rec.time_end):
                    
                    if party[0] is current_user.username:
                        return f'{current_user.name}(current) is unavailable on {booked_date} at {time_start} - {time_end}'
                    return f'{party[1]} is unavailable on {booked_date} at {time_start} - {time_end}'
    return ''

def get_party_email(party_list):
    party_usernames = [p[0] for p in party_list]
    emails = db.session.query(User.username, User.email).filter(User.username.in_(party_usernames)).all()
    return emails
    
def get_reservations():
    reservations = {}

    for r in db.session.query(Reservation).all():
        date = r.booked_date.strftime('%y-%m-%d')
        reservations.setdefault(date, []).append(
            {
            'id' : r.id,
            'username ':r.username ,
            'booking_time':r.booking_time,
            'time_start': int(r.time_start.strftime('%H')),
            'time_end':r.time_end,
            'party':r.party
            }
        )
    return reservations
    
def get_booked(date):
    booked = {}
    for i in range(1,NO_OF_ROOMS+1):
        booked[i] = []
    for r in db.session.query(Reservation.room_id, Reservation.time_start, Reservation.time_end).filter(Reservation.booked_date==date).all():
        booked[r.room_id].append(
            (int(r.time_start.strftime('%H')), int(r.time_end.strftime('%H')))
        )
    return booked

def check_time_passed(date1, te):
    d1 = str(date1).split('-')
    d2 = datetime.today().strftime('%Y-%m-%d').split('-')
    d1 = [int(i)for i in d1]
    d2 = [int(i)for i in d2]
    print(d1, d2)
    # fix date checking, mabok oi kalo 2022 < 2021, jan < dec

    check = [i <= j for i, j in zip(d1, d2)]
    print(check)
    for c in check:
        if c is False:
            return False

    if d1[2] == d2[2]:        
        hour_now = int(datetime.now().strftime('%H'))
        time_end = int(te.strftime('%H'))
        print(time_end, hour_now)
        if(time_end > hour_now):
            return False

    return True

    

def update_records():
    past_records = db.session.query(Reservation.id, Reservation.booked_date, Reservation.time_end).all()

    if past_records:
        print('====RECORDs====')
        for r in past_records:
            print(f'ID{r.id} Date: {r.booked_date}\t{r.time_end}', end='')
            if check_time_passed(r.booked_date, r.time_end):
                print('\tPassed')
                db.session.query(Reservation).filter(Reservation.id==r.id).update(
                    dict(
                        status=1))
            # else:
            #     print('\tnot Passed')

            #     db.session.query(Reservation).filter(Reservation.id==r.id).update(
            #         dict(
            #             status=0))
            db.session.commit()
        print('====RECORDs====')
        
