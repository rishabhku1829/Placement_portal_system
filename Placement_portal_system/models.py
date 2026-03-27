from database import db
from datetime import date,datetime


#models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String(100) , nullable=False)
    email = db.Column(db.String(100) , nullable=False , unique=True)
    password = db.Column(db.String(100) , nullable=False , unique=True) 
    role = db.Column(db.String(100) , nullable=False)
    contact = db.Column(db.Integer , nullable=False , unique=True)
    is_active = db.Column(db.String(50),default=True)
    is_blacklist = db.Column(db.Boolean, default=False)


class Drive(db.Model):
    __tablename__ = 'drive'
    id = db.Column(db.Integer , primary_key=True)
    user_id = db.Column(db.Integer , db.ForeignKey('users.id') , nullable=False)
    drive_name = db.Column(db.String(100) , nullable=False)
    company_id = db.Column(db.Integer , nullable=False)
    job_title = db.Column(db.String(100) , nullable=False)
    job_description = db.Column(db.String(100) , nullable=True)
    eligibilty = db.Column(db.String(100) , nullable=False)
    deadline = db.Column(db.DateTime)
    status = db.Column(db.String , default="pending")

    #relationship
    user = db.relationship('User', backref='drives')


class Application(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer , primary_key=True)
    student_name = db.Column(db.String , nullable=False)
    student_id = db.Column(db.Integer , nullable=False)
    drive_id = db.Column(db.Integer , db.ForeignKey('drive.id') , nullable=False)
    date = db.Column(db.DateTime , default = datetime.utcnow)
    status = db.Column(db.String , default="applied")

    #relationships
    drive = db.relationship('Drive', backref='applications')


class Profile(db.Model):
    __tablename__ = 'profile'
    company_id = db.Column(db.Integer , db.ForeignKey('drive.company_id') , primary_key=True)
    user_id = db.Column(db.Integer , db.ForeignKey('users.id') , nullable=False)
    company_name = db.Column(db.String(100) , nullable=False, unique=True)
    Hr_contact = db.Column(db.Integer , nullable=False , unique=True)
    website = db.Column(db.String(100) , nullable=False , unique=True)
    Status = db.Column(db.String , default="pending")

    #relationships
    user = db.relationship('User', backref=db.backref('profile', uselist=False))
    drive = db.relationship('Drive', backref='profile')

