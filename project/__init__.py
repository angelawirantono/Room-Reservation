import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# create and configure the app
app = Flask(__name__)
# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'project.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['SECRET_KEY'] = 'dev'

login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)

login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

import manage
manage.init_app(app)

# Blueprint order is apparently important...
from . import main
app.register_blueprint(main.bp)
app.add_url_rule('/', endpoint='index')


from . import auth
app.register_blueprint(auth.bp)

from . import booking
app.register_blueprint(booking.bp)

# from . import user
# app.register_blueprint(user.bp)

