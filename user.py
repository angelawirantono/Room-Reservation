from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db

from reservation_sys.auth import login_required

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('user/profile.html')