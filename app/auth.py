from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from .forms import RegisterForm,  LoginForm
from .models import db
from .mail import send_msg

from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        check_user = db.session.query(User).filter(
            User.username==form.username.data 
            or User.email==form.email.data).first()
        
        if check_user is None:
            user = User(
                form.username.data,
                form.name.data,
                form.email.data, 
                generate_password_hash(form.password.data)
                )

            subject = 'Registration'
            mail_html = '<p>Welcome! Thanks for signing up. </p>'

            send_msg(subject, [form.email.data], mail_html)
                   
            db.session.add(user)
            db.session.commit()
        
            login_user(user)
            
            flash('Successfully registered!', 'success')
            return redirect(url_for('booking.home'))
        else:
            flash('Username and/or email is taken', 'error')
            
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter(User.username==form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('booking.home'))
        else:
            flash('Failed to login', 'error')      
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/<int:id>/delete')
@login_required
def delete(id):

    deletion_time =  datetime.now().strftime('%H:%M:%S')
    delete_html = render_template('mail/auth/delete.html', deletion_time=deletion_time)
    
    send_msg('Account Deleted', [current_user.email], delete_html)

    curr_user = db.session.query(User).filter(User.id == id).first()
    db.session.delete(curr_user)
    db.session.commit()

    return redirect(url_for('booking.home'))
