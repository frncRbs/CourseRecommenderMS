from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import *
from . import mail
from flask_mail import Message

_auth = Blueprint('_auth', __name__)

@_auth.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@_auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))

def send_link(user_email, user_department):
    msg = Message('The account registration has been accepted.', sender='support@wetechsupport.online', recipients=[user_email])
    msg.body = f'''Account already approved!, visit following link
    { url_for('_route_cs.login_CS', _external=True) if user_department == 'computer science' else url_for('_route_it.login_IT', _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made
    '''
    mail.send(msg)
    
def send_link_disapproved(user_email):
    msg = Message('The account registration has been rejected.', sender='support@wetechsupport.online', recipients=[user_email])
    msg.body = f'''Account registration has been rejected!, Please contact your advisor for further details.
    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)