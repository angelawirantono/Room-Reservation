from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flask_login import login_user, login_required, logout_user
from .models import User
from .forms import RegisterForm,  LoginForm
from .models import db
from .mail import send_msg

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
            mail_html = '<p>Welcome! Thanks for signing up. Please follow this link to activate your account:</p><br><p>Cheers!</p>'

            send_msg(subject, [form.email.data], mail_html)
                   
            db.session.add(user)
            db.session.commit()
        
            login_user(user)
            
            flash('registered')
            return redirect(url_for('booking.home'))
        else:
            flash('Username and/or email is taken')
            
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
            flash('Failed to login')      
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
