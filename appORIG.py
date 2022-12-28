import numpy as np
import pandas as pd
import pickle
from tkinter import Y
from pandas import DataFrame
from flask import Flask, request, jsonify, render_template,redirect,url_for, session
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import OrdinalEncoder
from scipy.stats import spearmanr
import json
import plotly
import plotly.express as px
import random
import math
from flask_mysqldb import MySQL,MySQLdb
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField , PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
import mysql.connector as sql_db
from hashlib import md5
# from flask_ngrok import run_with_ngrok



dataset = pd.read_csv("model/remove_outliers.csv")

model = pickle.load(open("model/TrainedModel_Forest.pkl", "rb"))
model1 = pickle.load(open("model/TrainedModel_Forest.pkl", "rb"))
model2 = pickle.load(open("model/TrainedModel_Forest.pkl", "rb"))

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

# Create flask app
flask_app = Flask(__name__)
# run_with_ngrok(flask_app)
flask_app.config['SECRET_KEY'] = 'PapasaKameSaThesis'

flask_app.config['MYSQL_HOST'] = 'localhost'
flask_app.config['MYSQL_USER'] = 'root'
flask_app.config['MYSQL_PASSWORD'] = ''
flask_app.config['MYSQL_DB'] = 'user_db'
flask_app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(flask_app)

class LoginForm(FlaskForm):
     email=StringField('email', validators=[InputRequired()])
     password=PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

@flask_app.route("/")
def Home():
     cur =mysql.connection.cursor()
     cur.execute('SELECT * FROM user_form') 
     fetch_data= cur.fetchall()
     cur.close()

     pop = "model/populations.csv"
     pops = pd.read_csv(pop)

     fig1 = px.line(pops, x='School Year', y='Populations', title='1st year students enrolled from year 2018-2022')
     graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)


     return render_template("index.php" , d = fetch_data, graph1JSON=graph1JSON)


@flask_app.route("/admin")
def admin():
     cur =mysql.connection.cursor()
     cur.execute('SELECT * FROM student_details')
     fetch_data= cur.fetchall()
     cur.close()


     pop = "model/populations.csv"
     pops = pd.read_csv(pop)

     fig1 = px.line(pops, x='School Year', y='Populations', title='1st year students enrolled from year 2018-2022')
     graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)


     return render_template("admin_page.php" , d = fetch_data, graph1JSON=graph1JSON)


    

#Student Login
@flask_app.route("/stud_log",methods=['GET','POST'])
def stud_log_view():
     # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_form WHERE email = %s AND password = %s', (email, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
          #   session['loggedin'] = True
          #   session['first'] = account['first_name']
          #   session['middle'] = account['middle_name']
          #   session['last'] = account['last_name']


            
            # Redirect to home page
            return render_template('student_page.php', user=account)
        else:
            # Account doesnt exist or username/password incorrect
            return 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login_form.php')

     # mydb=sql_db.connect(
     #      host='localhost',
     #      user='root',
     #      password='',
     #      database='user_db'
     # )
     # mycursor=mydb.cursor()
     
     # if request.method=='POST':
     #      signup=request.form
     #      email=signup['email']
     #      password=signup['password']
     #      mycursor.execute("SELECT * FROM user_form WHERE email='"+email+"'and password='"+password+"' and user_type='Student'")
     #      user=mycursor.fetchall()
     #      count=mycursor.rowcount
     #      if count==1:
     #           return render_template('student_page.php', user=user)
     #      else:
     #           return 'wrong email/password'

     # return render_template("login_form.php")



@flask_app.route("/logout", methods=['GET','POST'])
def logout():
     session.clear()
     return redirect(url_for('Home'))




#Admin Login
@flask_app.route("/admin_log", methods=['GET','POST'])
def admin_log_view():

     mydb=sql_db.connect(
          host='localhost',
          user='root',
          password='',
          database='user_db'
     )
     mycursor=mydb.cursor()
     if request.method=='POST':
          signup=request.form
          email=signup['email']
          password=signup['password']
          mycursor.execute("SELECT * FROM user_form WHERE email='"+email+"'and password='"+password+"' and user_type='Admin'"  )
          r=mycursor.fetchall()
          count=mycursor.rowcount
          if count==1:
               return redirect(url_for('admin'))
          else:
               message='Wrong Email/Password'

     return render_template("admin_form.php")

#Student Registration
@flask_app.route("/reg", methods=['GET','POST'])
def register_view():

     mydb=sql_db.connect(
          host='localhost',
          user='root',
          password='',
          database='user_db'
     )


     message=''
     mycursor=mydb.cursor()
     if request.method=='POST':
          signup=request.form
          fisrt_name=signup['first_name']
          middle_name=signup['middle_name']
          last_name=signup['last_name']
          email=signup['email']
          password=signup['password']
          # password=md5(password.encode()).hexdigest()
          cpassword=signup['cpassword']
          user_type=signup['user_type']
          mycursor.execute('SELECT * FROM user_form WHERE email = %s',(email, ))
          account= mycursor.fetchone()
          if account:
               message='Email already exists!'

          elif password!=cpassword:
               message='Passwords do not match'

          else:
               mycursor.execute('INSERT INTO user_form (first_name, middle_name, last_name, email, password,user_type) VALUES(%s,%s,%s,%s,%s,%s)',(fisrt_name,middle_name,last_name,email,password,user_type))
               mydb.commit()
               mycursor.close()
               return render_template("login_form.php", message=message)

     return render_template("register_form.php", message=message)


#Admin Registration
@flask_app.route("/reg_admin", methods=['GET','POST'])
def register_admin_view():
     mydb=sql_db.connect(
     host='localhost',
     user='root',
     password='',
     database='user_db'
     )
     message=''
     mycursor=mydb.cursor()
     if request.method=='POST':
          signup=request.form
          fisrt_name=signup['first_name']
          middle_name=signup['middle_name']
          last_name=signup['last_name']
          email=signup['email']
          password=signup['password']
          cpassword=signup['cpassword']
          user_type=signup['user_type']
          code=signup['code']
          if code=='admin123':
               mycursor.execute('SELECT * FROM user_form WHERE email = %s',(email, ))
               account= mycursor.fetchone()
               if account:
                    message='Email already exists!'
               
               elif password!=cpassword:
                    message='Passwords do not match'

               else:
                    mycursor.execute('INSERT INTO user_form (first_name, middle_name, last_name, email, password,user_type) VALUES(%s,%s,%s,%s,%s,%s)',(fisrt_name,middle_name,last_name,email,password,user_type))
                    mydb.commit()
                    mycursor.close()
                    return render_template("admin_form.php", message=message)
          else:
               return 'Invalid Code'
    
     return render_template("register_form_admin.php")


#Student Page
@flask_app.route("/student_page", methods=['GET','POST'])
def stud_page_view():
     mydb=sql_db.connect(
          host='localhost',
          user='root',
          password='',
          database='user_db'
     )
     cur=mydb.cursor()
     if request.method=='POST':
          signup=request.form
          gender=signup['gender']
          athlete=signup['athlete']
          leader=signup['leader']
          track=signup['track']
          school=signup['school']
          gpa=signup['gpa']
          Oapr=signup['Oapr']
          Pr1=signup['Pr1']
          Pr2=signup['Pr2']
          Pr3=signup['Pr3']
          Pr4=signup['Pr4']
          Pr5=signup['Pr5']
          #,Oapr,Pr1,Pr2,Pr3,Pr4,Pr5
          cur.execute('INSERT INTO student_details ( gender, athlete, leader, track, school,gpa,Oapr,english,reading,science,math,logic) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (gender, athlete, leader, track, school,gpa,Oapr,Pr1,Pr2,Pr3,Pr4,Pr5))
          mydb.commit()
          cur.close()
          return 'kapuy'
     return render_template("student_page.php")


#Admin Page
@flask_app.route("/admin_page")
def admin_page():
     cur =mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     cur.execute('SELECT * FROM student_details')
     fetch_data= cur.fetchall()
    
     return render_template("admin_page.php" , student = fetch_data)


@flask_app.route("/start")
def start_view():
    return render_template("start.php")

@flask_app.route("/end")
def end_view():
     rate = "model/graduated_list_rate.csv"
     return render_template("end.php")


@flask_app.route("/result")
def result():
     rate = "model/graduated_list_rate.csv"
     return render_template("result.php")

@flask_app.route("/details")
def details():

     mydb=sql_db.connect(
     host='localhost',
     user='root',
     password='',
     database='user_db'
     )
     message=''
     cur=mydb.cursor()
     if request.method=='POST':
          signup=request.form
          gender=signup['gender']
          athlete=signup['athlete']
          leader=signup['leader']
          track=signup['track']
          school=signup['school']
          gpa=signup['gpa']
          Oapr=signup['Oapr']
          Pr1=signup['Pr1']
          Pr2=signup['Pr2']
          Pr3=signup['Pr3']
          Pr4=signup['Pr4']
          Pr5=signup['Pr5']

          account= cur.fetchone()
          cur.execute('INSERT INTO student_details ( gender, athlete, leader, track, school,gpa,Oapr,Pr1,Pr2,Pr3,Pr4,Pr5) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(gender, athlete, leader, track, school,gpa,Oapr,Pr1,Pr2,Pr3,Pr4,Pr5))
          mydb.commit()
          cur.close()
          return 'kapuy'
     

@flask_app.route("/start_pred", methods = ["POST"])
def start_pred():


     # cur =mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     # cur.execute('SELECT * FROM course_des')
     # fetch_data= cur.fetchall()

     float_features = [float(x) for x in request.form.values()]
     features = [np.array(float_features)]
     x_data = X.sample(4)
     y_data = Y[x_data.index.values]
     prediction = model.predict(features)
     
     def recall(y_data, predict, K):
            act_set = set(y_data)
            pred_set = set(predict[:K])
            result = round(len(act_set & pred_set) / float(len(act_set)), 2)
            return result
     
     # res = str(prediction)[1:-1]
     # prediction=res
     for K in range(0, 3):
        
        pred = prediction[0]
        actual = y_data
        prediction = [ "BS NURSING",
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


        pop = "model/populations.csv"
        pops = pd.read_csv(pop)

        fig1 = px.line(pops, x='School Year', y='Populations', title='1st year students enrolled from year 2018-2022')
        graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
        
        return render_template("result.php", des1=fetchPred2,des2=fetchPred1,des3=fetchPred3,graph1JSON=graph1JSON,
                               prediction_text1 = "{}".format(f"{prediction[K]}"),  
                               prediction_text2 = "{}".format(f"{prediction[K-1]}"),
                               prediction_text3 = "{}".format(f"{prediction[K-2]}"),
                               )

                               #: {fetch1}%
                               #: {fetch2}%
                               #: {fetch3}%

if __name__ == "__main__":
    flask_app.run(debug=True)