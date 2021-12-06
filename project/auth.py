from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flask_login import login_user, login_required, logout_user
from project.models import User
from project.forms import RegisterForm,  LoginForm
from project import db, login_manager

bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()

@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(
            form.username.data,
            form.name.data,
            form.email.data, 
            generate_password_hash(form.password.data)
            )

        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        
        flash('registered')
        return redirect(url_for('main.home'))

    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter(User.username==form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Failed to login')      
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))