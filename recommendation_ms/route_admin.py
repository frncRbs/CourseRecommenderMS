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
        if auth_user.user_type == 1:
            return redirect(url_for('.admin_dashboard'))
        else:
            return redirect(url_for('_auth.index'))
    return render_template('Admin/admin_form.html')

@_route_admin.route('/admin_dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    if request.method == 'GET':
        
        male = StudentDetails.query.filter(StudentDetails.gender=='Male').count()
        female = StudentDetails.query.filter(StudentDetails.gender=='Female').count()
        
        # Current Logged User
        auth_user=current_user
        page = request.args.get('page', 1, type=int)

        # Data for search
        search = request.args.getlist('search')
        search = (','.join(search))
        
        gender = request.args.getlist('gender')
        gender = (','.join(gender))
        
        print(search, gender)
        # Data for filter department
        # Return Data for template
        if auth_user.user_type == 0:
            if search:
                students_record = db.session.query(User).filter(User.is_approve == 1)\
                    .filter((User.first_name.like('%' + search + '%'))      |
                    (User.middle_name.like('%' + search + '%'))     |
                    (User.last_name.like('%' + search + '%')))\
                    .paginate(page=page, per_page=5)# fetch user students only
            elif gender:
                students_record = db.session.query(User).filter(User.is_approve == 1)\
                    .filter((User.gender==gender))\
                    .paginate(page=page, per_page=5)# fetch sex only
            else:
                students_record = db.session.query(User, PredictionResult, StudentDetails).join(PredictionResult, StudentDetails).filter(User.is_approve == 1, User.user_type == 1).paginate(page=page, per_page=5)# fetch user students only

            auth_user=current_user
        else:
            return redirect(url_for('_auth.index'))
    
    return render_template("Admin/admin_page.html", auth_user=auth_user, students_record=students_record, search=search, gender=gender,
                           male = json.dumps(male), female = json.dumps(female))

    # if auth_user.user_type == 0:
    #     return render_template("Admin/admin_page.html", auth_user=auth_user)
    # else:
    #     return redirect(url_for('_auth.index'))

@_route_admin.route('/login_admin_form', methods=['GET'])
def login_admin_form():
    auth_user=current_user
    if auth_user.is_authenticated:
        if auth_user.user_type == 0:
            return redirect(url_for('.admin_form'))
        else:
            return redirect(url_for('_auth.index'))
    return render_template("Admin/admin_form.html")

@_route_admin.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    auth_user=current_user
    if auth_user.is_authenticated:
        if auth_user.user_type == 0:
            return redirect(url_for('.admin_dashboard'))
        else:
            flash('Only admin is permitted', category='error')
            return redirect(url_for('.admin_form'))
    else:
        if request.method == 'POST':
            user = User.query.filter_by(email=request.form['email'], user_type=0).first()
            if user:
                if user.is_approve == True:
                    if check_password_hash(user.password, request.form['password']):
                        login_user(user, remember=True)
                        return redirect(url_for('.admin_dashboard'))
                    else:
                        flash('Invalid or wrong password', category='error')
                else:
                    flash('Account is not approve yet, wait for further notice.', category='info')
            else:
                flash('No record found', category='error')
    return redirect(url_for('.register_form_admin'))

@_route_admin.route('/register_form_admin', methods=['GET'])
def register_form_admin():
     auth_user=current_user
     if auth_user.is_authenticated:
          if auth_user.user_type == 1:
               return redirect(url_for('.admin_dashboard'))
          else:
               return redirect(url_for('_auth.index'))
     return render_template("Admin/register_form_admin.html")

@_route_admin.route('/register_admin', methods=['POST'])
def register_admin():
     try:
        if request.form['code']=='admin123':
            new_user = User(request.form['first_name'], request.form['middle_name'], request.form['last_name'], request.form['email'],  (generate_password_hash(request.form['password'], method="sha256")), True, 0)
            db.session.add(new_user)
            db.session.commit()
            flash('Account successfully created', category='success_register')
            return redirect(url_for('.register_form_admin'))
        else:
            flash('Incorrect code', category='error')
            return redirect(url_for('.register_form_admin'))
     except:
          flash('Invalid credentials', category='error')
          return redirect(url_for('.register_form_admin'))   