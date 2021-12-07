from project import mail
from flask_mail import Message

from flask import Blueprint

bp = Blueprint('mail', __name__, url_prefix='/mail')

@bp.route('/')
def index():
    msg = Message("Hello",
                recipients=["zegryu@gmail.com"])
