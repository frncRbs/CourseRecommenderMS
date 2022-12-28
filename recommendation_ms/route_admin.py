from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, make_response, session
from flask_login import login_required, current_user
from .models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import delete
from sqlalchemy import select
import json

from .auth import send_link, send_link_disapproved # for email message

_route_admin = Blueprint('_route_admin', __name__)

@_route_admin.route('/admin_form', methods=['GET'])
def admin_form():
    auth_user=current_user
    if auth_user.is_authenticated:
        if auth_user.user_type == -1 or auth_user.user_type == 0:
            return redirect(url_for('.admin_form'))
        else:
            return redirect(url_for('_auth.index'))
            
    return render_template("Faculty/admin_form.html")