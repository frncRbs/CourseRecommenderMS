from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, make_response, session
from flask_login import login_required, current_user
from .models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import delete
from sqlalchemy import select
import datetime
from datetime import datetime
import json
import numpy as np
import pandas as pd
import pickle
from tkinter import Y
from pandas import DataFrame
from flask import Flask, request, jsonify, render_template
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import OrdinalEncoder
from scipy.stats import spearmanr
# import matplotlib.pyplot as plt
import json
# import plotly
# import plotly.express as px
import random
import math
from os import path
import os

from .auth import send_link, send_link_disapproved # for email message

_route_student = Blueprint('_route_student', __name__)

@_route_student.route('/index')
@login_required
def dashboard():
    return '1'

dataset = os.path.join(os.path.abspath(os.path.dirname(__file__)),"model/remove_outliers.csv")

model = os.path.join(os.path.abspath(os.path.dirname(__file__)),"model/TrainedModel_Forest.pkl")
model1 = os.path.join(os.path.abspath(os.path.dirname(__file__)),"model/TrainedModel_Forest.pkl")
model2 = os.path.join(os.path.abspath(os.path.dirname(__file__)),"model/TrainedModel_Forest.pkl")

dataset = pd.read_csv(dataset)

FEATURES = [
     'Pr1',
     'Pr2',
     'Pr3',
     'Pr4',
     'Pr5',
     'Oapr'
]

TARGET = 'Course'

Y = dataset[TARGET]
X = dataset[FEATURES]

X = X.replace(np.nan, 0)

model_stud = pickle.load(open(model, "rb"))

flask_app = Flask(__name__) #Initialize flask_app

@flask_app.route("/")
def Home():
    return render_template("index.html")

@_route_student.route('/student_page', methods=['GET'])
@login_required
def student_page():
    auth_user=current_user
    if auth_user.user_type == 1:
        return render_template("Student/student_page.html", auth_user=auth_user)
    else:
        return redirect(url_for('_auth.index'))
    
@_route_student.route('/prediction_result', methods=['GET'])
@login_required
def prediction_result():
    auth_user=current_user
    if auth_user.user_type == 1:
        return render_template("Student/result.html", auth_user=auth_user)
    else:
        return redirect(url_for('_auth.index'))
   
@_route_student.route('/login_form', methods=['GET'])
def login_form():
    auth_user=current_user
    if auth_user.is_authenticated:
        if auth_user.user_type == 1:
            return redirect(url_for('.student_page'))
        else:
            return redirect(url_for('_auth.index'))
    return render_template("Student/login_form.html")

@_route_student.route('/register_form', methods=['GET'])
def register_form():
     auth_user=current_user
     if auth_user.is_authenticated:
          if auth_user.user_type == 1:
               return redirect(url_for('.student_page'))
          else:
               return redirect(url_for('_auth.index'))
     return render_template("Student/register_form.html")

@_route_student.route('/register_student', methods=['POST'])
def register_student():
     try:
        new_user = User(request.form['first_name'], request.form['middle_name'], request.form['last_name'], request.form['email'],  (generate_password_hash(request.form['password'], method="sha256")), False, 1)
        db.session.add(new_user)
        db.session.commit()
        flash('Account successfully created', category='success_register')
        return redirect(url_for('.register_form'))
     except:
          flash('Invalid credentials', category='error')
          return redirect(url_for('.register_form'))     
      
@_route_student.route('/register_student_details', methods=['POST'])
def register_student_details():
     try:
        date_pred = datetime.now()
        new_user = StudentDetails(request.form['stud_gender'], request.form['stud_athlete'], request.form['stud_leader'], request.form['stud_school'],  request.form['stud_gpa'], current_user.id, date_registered=date_pred)
        db.session.add(new_user)
        db.session.commit()
        # flash('Account successfully created', category='success_register')
        return redirect(url_for('.prediction_result'))
     except:
          flash('Invalid credentials', category='error')
          return redirect(url_for('.student_page'))     



@_route_student.route('/login_student', methods=['GET', 'POST'])
def login_student():
    auth_user=current_user
    if auth_user.is_authenticated:
        if auth_user.user_type == 1:
            return redirect(url_for('.student_page'))
        else:
            return redirect(url_for('_auth.index'))
    else:
        if request.method == 'POST':
            user = User.query.filter_by(email=request.form['email'], user_type=1).first()
            if user:
                if user.is_approve == True:
                    if check_password_hash(user.password, request.form['password']):
                        login_user(user, remember=True)
                        return redirect(url_for('.student_page'))
                    else:
                        flash('Invalid or wrong password', category='error')
                else:
                    flash('Account is not approve yet, wait for further notice.', category='info')
            else:
                flash('No record found', category='error')
    return redirect(url_for('.login_form'))


@_route_student.route("/start_pred", methods=["GET", "POST"])
def start_pred():

     # cur =mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     # cur.execute('SELECT * FROM course_des')
     # fetch_data= cur.fetchall()
    auth_user=current_user
    if request.method== 'GET':
        return render_template("Student/student_page.html")
    else:
        float_features = [float(x) for x in request.form.values()]
        features = [np.array(float_features)]
        x_data = X.sample(4)
        y_data = Y[x_data.index.values]
        prediction = model_stud.predict(features)
        
        def recall(y_data, prediction, K):
                act_set = set(y_data)
                pred_set = set(prediction[:K])
                result = round(len(act_set & pred_set) / float(len(act_set)), 2)
                return result
        
        # res = str(prediction)[1:-1]
        # prediction=res
        for K in range(0, 3):
            
            pred = prediction[0]
            actual = y_data
            prediction = ["BS NURSING",
                        "BS ARCHITECTURE", 
                        "BS CRIMINOLOGY",
                        "BS BIOLOGY",
                        "BACHELOR OF ELEMENTARY EDUCATION",
                        "BA POLITICAL SCIENCE",
                        "BS ACCOUNTANCY",
                        "BS CIVIL ENGINEERING",
                        "BS ECONOMICS",
                        "BS COMPUTER SCIENCE",
                        "BS INFORMATION TECHNOLOGY",
                        "BS PSYCHOLOGY",
                        "BACHELOR OF PHYSICAL EDUCATION",
                        "BS MECHANICAL ENGINEERING",
                        "BA ENGLISH",
                        "BACHELOR OF SECONDARY EDUCATION",
                        "BS SOCIAL WORK",
                        "BA HISTORY",
                        "BS ELECTRICAL ENGINEERING",
                        "BA FILIPINO",
                        "BS COMMUNITY DEVELOPMENT",
                        "BACHELOR OF SPECIAL NEEDS EDUCATION",
                        "BS NUTRITION AND DIETETICS",
                        "BS HOSPITALITY MANAGEMENT",
                        "BS HOME ECONOMICS",
                        "BA MASS COMMUNICATION MAJOR IN BROADCASTING",
                        "BS CHEMISTRY","BS COMPUTER ENGINEERING",
                        "BS INDUSTRIAL ENGINEERING",
                        "BS SOFTWARE ENGINEERING",
                        "BA JOURNALISM",
                        "BS GEODETIC ENGINEERING",
                        "BS MATHEMATICS",
                        "BS ENERGY ENGINEERING",
                        "BS ELECTRONICS AND COMMUNICATIONS ENGINEERING",
                        "BS STATISTICS",
                        "BS AGRICULTURE",
                        "BS PHYSICS",
                        "BS AGRICULTURAL AND BIOSYSTEMS ENGINEERING",
                        "BA MASS COMMUNICATION MAJOR IN JOURNALISM",
                        "BS INTERDISIPLINARY STUDIES",
                        "BACHELOR OF SECONDARY EDUCATION MAJOR IN SOCIAL STUDIES",
                        "BSED VEDUC",
                        "BS FORESTRY"]
            
            random.shuffle(prediction)
            prediction = [prediction.replace(pred, pred)for prediction in prediction]
            prediction.append(pred)
            
            fetch1 = recall(actual, prediction, K) 
            fetch2 = recall(actual, prediction, K-1) 
            fetch3 = recall(actual, prediction, K-2)  
                
            fetchPred1 = prediction[0]
            fetchPred2 = prediction[-1]
            fetchPred3 = prediction[-2]


            # pop = "model/populations.csv"
            # pops = pd.read_csv(pop)
            
            # REGISTERING PREDICTION
            
            pred1 = "{}".format(f"{prediction[K]}")
            pred2 = "{}".format(f"{prediction[K-1]}")
            pred3 = "{}".format(f"{prediction[K-2]}")
            
            date_pred = datetime.now()
        
            new_pred = PredictionResult(fetchPred2, pred2, pred3, pred1, request.form['Oapr'], request.form['Pr1'], request.form['Pr2'], request.form['Pr3'], request.form['Pr4'],  request.form['Pr5'], current_user.id, date_predicted=date_pred)
            db.session.add(new_pred)
            db.session.commit()
            

            # fig1 = px.line(pops, x='School Year', y='Populations', title='1st year students enrolled from year 2018-2022')
            # graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder) // graph1JSON=graph1JSON,
            
            return render_template("Student/result.html", des1=fetchPred2,des2=fetchPred1,des3=fetchPred3,
                                prediction_text1 = "{}".format(f"{prediction[K]}"),  
                                prediction_text2 = "{}".format(f"{prediction[K-1]}"),
                                prediction_text3 = "{}".format(f"{prediction[K-2]}"), auth_user=auth_user
                                )