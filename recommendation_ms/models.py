from sqlalchemy.sql import func
from sqlalchemy import column, func
from . import db, marsh, app
from flask_login import UserMixin

from marshmallow import Schema, fields

class UserSchema(marsh.Schema):
    class Meta:
        fields = ('id', 'first_name', 'middle_name', 'last_name', 'email', 'password', 'is_approve', 'detail_no', 'predict_no', 'user_type')
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    middle_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_approve = db.Column(db.Boolean, nullable=False, default=0)
    detail_no = db.Column(db.Boolean, nullable=False, default=0)
    predict_no = db.Column(db.Boolean, nullable=False, default=0)
    user_type = db.Column(db.SmallInteger, nullable=False, default=1)# -1 Superadmin(Built-in), 0 - Admin, 1 - Personnel
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    pred_results = db.relationship('PredictionResult', backref='user', uselist=False)
    stud_details = db.relationship('StudentDetails', backref='user', uselist=False)

    def __init__(self, first_name, middle_name, last_name, email, password, is_approve, detail_no, predict_no, user_type):
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.is_approve = is_approve
        self.detail_no = detail_no
        self.predict_no = predict_no
        self.user_type = user_type


class PredictionResultSchema(marsh.Schema):
    class Meta:
        fields = ('result_id', 'main_rank', 'sub_rank1', 'sub_rank2', 'oapr', 'english', 'reading', 'science', 'math', 'logic', 'user_id', 'date_predicted')

class PredictionResult(db.Model):
    result_id = db.Column(db.Integer, primary_key=True)
    main_rank = db.Column(db.String(255), nullable=False)
    sub_rank1 = db.Column(db.String(255), nullable=False)
    sub_rank2 = db.Column(db.String(255), nullable=False)
    oapr = db.Column(db.String(255), nullable=False)
    english = db.Column(db.String(255), nullable=False)
    reading = db.Column(db.String(255), nullable=False)
    science = db.Column(db.String(255), nullable=False)
    math = db.Column(db.String(255), nullable=False)
    logic = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_predicted = db.Column(db.DateTime(timezone=True), default=func.now())

    def __init__(self, main_rank, sub_rank1, sub_rank2, oapr, english, reading, science, math, logic, user_id, date_predicted):
        self.main_rank = main_rank
        self.sub_rank1 = sub_rank1
        self.sub_rank2 = sub_rank2
        self.oapr = oapr
        self.english = english
        self.reading = reading
        self.science = science
        self.math = math
        self.logic = logic
        self.user_id = user_id
        self.date_predicted = date_predicted
        
class StudentDetailsSchema(marsh.Schema):
    class Meta:
        fields = ('student_id', 'gender', 'athlete', 'leader', 'track', 'school', 'gpa', 'user_id', 'date_registered')

class StudentDetails(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(255), nullable=False)
    athlete = db.Column(db.String(255), nullable=False)
    leader = db.Column(db.String(255), nullable=False)
    track = db.Column(db.String(255), nullable=False)
    school = db.Column(db.String(255), nullable=False)
    gpa = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_registered = db.Column(db.DateTime(timezone=True), default=func.now())

    def __init__(self, gender, athlete, leader, track, school, gpa, user_id, date_registered):
        self.gender = gender
        self.athlete = athlete
        self.leader = leader
        self.track = track
        self.school = school
        self.gpa = gpa
        self.user_id = user_id
        self.date_registered = date_registered