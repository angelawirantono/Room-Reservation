import os
from project import app

class Config(object):
    TESTING = False
    MAIL_SERVER = '127.0.0.1'
    DEFAULT_MAIL_SENDER = 'admin@admin.com'
    MAIL_USERNAME = 'Reservation System Admink '
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.instance_path, 'project.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = 'dev'
    

class TestingConfig(Config):
    DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True