import os
from flask import Flask, Blueprint
from flask_login import LoginManager
from config import DevelopmentConfig
from .models import db, User

app = Flask(__name__)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'project.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# app.config['SECRET_KEY'] = 'dev'

app.config.from_object(DevelopmentConfig)
app.config.from_pyfile('../acc.cfg')

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

import manage
manage.init_app(app)

from . import main
app.register_blueprint(main.main_bp)
app.add_url_rule('/', endpoint='index')

from . import auth
app.register_blueprint(auth.auth_bp)

from . import booking
app.register_blueprint(booking.booking_bp)

from . import mail
mail.mail.init_app(app)

login_manager.login_view = "auth_bp.login"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()