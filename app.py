from flask import Flask,render_template,request , url_for , redirect , session , flash
from werkzeug.security import generate_password_hash
from functools import wraps 
from sqlalchemy.orm import aliased
from datetime import datetime


app = Flask(__name__)
#Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portal.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Initialize database 
from database import db

db.init_app(app)

from models import User,Drive,Application,Profile



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the 'role' key (or 'logged_in') exists in the session
        if 'role' not in session:
            flash('Please log in to access this page.')
            # Redirect to the login page if not authenticated
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

#---------------------------------------------------------------------------------------------#
#creating routes
@app.route('/')
def index():
    if 'role' not in session:
        pass
    return render_template('index.html')

#login for all users
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            return redirect(url_for('login'))
        
        #finding user
        user = User.query.filter_by(email=email,password=password).first()
        profile = Profile.query.filter_by(company_id=user.id).first()

        #redirect user on their role
        if not user.is_blacklist:
            if user and user.role == "admin":
                session['name'] = user.name
                session['id'] = user.id
                session['role'] = user.role
                return redirect(url_for('admin_dash'))
            
            elif user and user.role == "company" and user.is_blacklist == False:
                session['name'] = user.name
                session['id'] = user.id
                session['role'] = user.role
                return redirect(url_for('company_dash',comp_id=user.id))
            
            elif user and user.role == "student":
                session['name'] = user.name
                session['id'] = user.id
                session['role'] = user.role
                return redirect(url_for('student_dash',id=user.id))
            
            else:
                return redirect(url_for('login'))
        else:
            return redirect(url_for("login"))
    return render_template('login.html')


#For logout
@app.route('/logout')
@login_required
def logout():
    session.pop('name',None)
    session.pop('id',None)
    session.pop('role',None)
    return redirect(url_for('index'))


#register for user
@app.route('/register' , methods= ['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        contact = request.form['contact']
        role = request.form['role']

        #validations
        if not all([name, email, password , contact , role]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))
        
        existing_user = User.query.filter_by(email = email).first()
        if existing_user:
            flash('Email already regestered!', 'danger')
            return redirect(url_for('register'))
        
        #creating new student
        new_user = User(name=name , email=email , password=password , role=role , contact=contact , is_active=True)

        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

#-----------------------------------------ADMIN DASHBOARD ROUTES---------------------------------------#
@app.route('/admin_dash' , methods=['GET','POST'])
def admin_dash():
    if session.get('role') != "admin":
        return redirect(url_for('index'))
    
    #filter companies
    query = User.query.filter_by(role='company')
    companies = query.distinct().all()

    #filter students
    students = User.query.filter_by(role='student').distinct().all()

    #filter company applications
    applications = Profile.query.filter_by(Status='pending').distinct().all()

    #filter ongoing drives
    drives = Drive.query.distinct().all()

    drive=aliased(Drive)
    profile=aliased(Profile)

    details = db.session.query(
        Application.id,
        Application.student_name,
        Application.date,  
        drive.job_description.label('job_description'),
        drive.job_title.label('job_title'),
        drive.drive_name.label('drive_name'),
        profile.company_name
    ).select_from(Application).join(drive,Application.drive_id==drive.id).join(profile,profile.user_id==drive.user_id).all()

    stu_applications = []

    for detail in details:
        stu_applications.append({
            'id':detail.id,
            'student_name':detail.student_name,
            'department':detail.job_description,
            'job_title':detail.job_title,
            'drive_name':detail.drive_name,
            'company_name':detail.company_name,
            'date':detail.date
        })

    return render_template('admin_dash.html' , companies=companies , students=students, applications=applications, drives=drives, stu_applications=stu_applications)



@app.route('/stu_application/<int:app_id>/<job>' , methods=['GET','POST'])
def stu_application(app_id,job):
    #filter companies
    drive = Drive.query.filter_by(job_title=job).first()
    drive_apply=aliased(Drive)
    
    application = db.session.query(
        Application.id,
        Application.student_name,  
        drive_apply.job_description.label('job_description'),
        drive_apply.job_title.label('job_title'),
        drive_apply.drive_name.label('drive_name')
    ).select_from(Application).join(drive_apply,Application.drive_id==drive_apply.id).filter(drive_apply.job_title==job,Application.id==app_id).first()

    # applications = []

    # for detail in details:
    #     applications.append({
    #         'id':detail.id,
    #         'student_name':detail.student_name,
    #         'department':detail.job_description,
    #         'job_title':detail.job_title,
    #         'drive_name':detail.drive_name
    #     })

    return render_template('stu_application.html' , drive=drive, application=application)


#company blacklist routes
@app.route('/companies/blacklist/<int:id>')
def blacklist_company(id):
    company = User.query.filter_by(id=id).first()
    company.is_blacklist = True
    db.session.commit()

    return redirect(url_for('admin_dash'))

@app.route('/companies/un_blacklist/<int:id>')
def un_blacklist_company(id):
    company = User.query.filter_by(id=id).first()
    company.is_blacklist = False
    db.session.commit()

    return redirect(url_for('admin_dash'))

#student blacklist routes
@app.route('/students/blacklist/<int:id>')
def blacklist_student(id):
    student = User.query.filter_by(id=id).first()
    student.is_blacklist = True
    db.session.commit()

    return redirect(url_for('admin_dash'))

@app.route('/students/un_blacklist/<int:id>')
def un_blacklist_student(id):
    student = User.query.filter_by(id=id).first()
    student.is_blacklist = False
    db.session.commit()

    return redirect(url_for('admin_dash'))


# Admin search of students and companies
@app.route('/admin/search')
def search_students():
    search_query = request.args.get('search_query','').strip()

    students = []
    if search_query:
        students = User.query.filter(
            db.or_(User.name.ilike(f"%{search_query}%"),
                   User.role.ilike(f"%{search_query}%"))
                ).all()
        
    return render_template('admin_dash.html',search_query=search_query,students=students)

#approve companies applications
@app.route('/companies/application/<int:id>')
def approve_company(id):
    profile = Profile.query.filter_by(company_id=id).first()
    profile.Status = "Approve"
    db.session.commit()

    return redirect(url_for('admin_dash'))


@app.route('/view_details/<int:id>',methods=['GET','POST'])
def view_details(id):
    drive = Drive.query.filter_by(id=id).first()
    company = Profile.query.filter_by(company_id=id).first()

    return render_template('view_details.html',drive=drive,company=company)

@app.route('/drive_approve/<int:id>')
def drive_approve(id):
    drive = Drive.query.filter_by(id=id).first()
    drive.status = "Approve"
    db.session.commit()

    return redirect(url_for('admin_dash'))




#----------------------------------------COMPANY DASHBOARD ROUTES----------------------------------#
#Company dashboard routes
@app.route('/company_dash/<int:comp_id>')
def company_dash(comp_id):
    company = User.query.filter_by(id=comp_id).first()
    drives = Drive.query.filter_by(user_id=comp_id).all()

    return render_template('company_dash.html',company=company,drives=drives,comp_id=comp_id)


#complete profile route
@app.route('/update_profile/<int:id>',methods=['GET','POST'])
def update_profile(id):
    company = User.query.filter_by(id=id).first()

    if request.method == 'POST':
        comp_name = request.form['company_name']
        hr_contact = request.form['hr_contact']
        website = request.form['website']

        if not all([comp_name,hr_contact,website]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('update_profile'))
        
        new_profile = Profile(
            company_id = id,
            user_id = id,
            company_name = comp_name,
            Hr_contact = hr_contact,
            website = website,
            Status = 'pending'
        )
        db.session.add(new_profile)
        db.session.commit()

    return render_template('update_profile.html',company=company)


@app.route('/student_application_details/<int:app_id>/<int:comp_id>/<job>',methods=['GET','POST'])
def student_application_details(app_id,comp_id,job):
    #filter companies
    # company = User.query.filter_by(id=comp_id).first()
    drive = Drive.query.filter_by(id=app_id,company_id=comp_id).first()
    drive_apply=aliased(Drive)
    
    application = db.session.query(
        Application.id,
        Application.student_name,
        drive_apply.job_description.label('job_description'),
        drive_apply.job_title.label('job_title'),
        drive_apply.drive_name.label('drive_name')
    ).select_from(Application).join(drive_apply,Application.drive_id==drive_apply.id).filter(drive_apply.company_id==comp_id,drive_apply.job_title==job).first()

    #Perform some actions on student applications
    if request.method == "POST":
        new_status = request.form.get('actions')

        app = Application.query.filter_by(drive_id=drive.id).first()

        app.status = new_status
        db.session.commit()
        return redirect(url_for('drive_student',id=drive.id, comp_id=drive.company_id, job=drive.job_title))


    return render_template('student_application_details.html' , drive=drive, application=application)



#create drive
@app.route('/create_drive/<comp_id>' ,methods=['GET','POST'])
def create_drive(comp_id):
    if request.method == "POST":
        name = request.form['drivename']
        title = request.form['title']
        description = request.form['description']
        eligibilty = request.form['eligibilty']
        deadline = request.form['deadline']

        if not all([name,title,description,eligibilty,deadline]):
            return redirect(url_for('create_drive',comp_id=comp_id))
        
        deadline_date = datetime.strptime(deadline,'%Y-%m-%d').date()
        
        new_drive = Drive(
            drive_name = name,
            user_id = comp_id,
            company_id = comp_id,
            job_title = title,
            job_description = description,
            eligibilty = eligibilty,
            deadline = deadline_date,
        )

        db.session.add(new_drive)
        db.session.commit()
        return redirect(url_for('company_dash', comp_id=comp_id))
    
    return render_template('create_drive.html',comp_id=comp_id)


@app.route('/drive_student/<int:id>/<int:comp_id>/<job>',methods=['GET','POST'])
def drive_student(id,comp_id,job):
    company = User.query.filter_by(id=comp_id).first()
    drive = Drive.query.filter_by(id=id).first()
    
    details = db.session.query(
        Application.id,
        Application.student_name,     
    ).select_from(Application).join(Drive,Application.drive_id==Drive.id).filter(Drive.company_id==company.id,Drive.job_title==job).all()

    applications = []

    for detail in details:
        applications.append({
            'id':detail.id,
            'student_name':detail.student_name,
        })

    return render_template('drive_student.html' , drive=drive, applications=applications ,company=company)

#----------------------------------------STUDENT DASHBOARD ROUTES-------------------------------------#
#Student Dash routes
@app.route('/student_dash/<int:id>',methods=['GET','POST'])
def student_dash(id):
    student = User.query.filter_by(id=id).first()

    profiles = Profile.query.all()

    #join tables 
    drive = aliased(Drive)
    profile = aliased(Profile)

    details = db.session.query(
        Application.id,
        drive.drive_name,  
        profile.company_name,
        Application.date
    ).select_from(Application).join(drive,Application.drive_id==drive.id).join(profile,drive.company_id==profile.company_id).filter(Application.student_id==id).all()

    applications = []

    for detail in details:
        applications.append({
            'id':detail.id,
            'drive_name':detail.drive_name,
            'company_name':detail.company_name,
            'date':detail.date,
        })

    return render_template('student_dash.html',profiles=profiles,student=student,applications=applications)


@app.route('/student_history/<int:id>',methods=['GET','POST'])
def student_history(id):
    student = User.query.filter_by(id=id).first()

    #join tables
    drive=aliased(Drive)

    details = db.session.query(
        Application.student_name,
        Application.status,
        drive.job_title,
        drive.id
    ).select_from(Application).join(drive,Application.student_id==drive.user_id).all()

    applications = []

    for detail in details:
        applications.append({
            'student_name':detail.student_name,
            'status':detail.status,
            'drive':detail.id,
            'job_title':detail.job_title
        })

    return render_template('student_history.html',student=student,applications=applications)


@app.route('/drive_apply/<int:id>/<int:stu_id>',methods=['GET','POST'])
def drive_apply(id,stu_id):
    student = User.query.filter_by(id=stu_id).first()
    drive = Drive.query.filter_by(id=id).first()
    company = Profile.query.filter_by(company_id=drive.company_id).first()

    #add data in application
    if request.method == 'POST':
        student_name = request.form['student']
        student_id = request.form['user_id']
        drive_id = request.form['drive_id']

        new_apply = Application(
            student_name = student_name,
            student_id = student_id,
            drive_id = drive_id,
            status = 'pending'
        )
        db.session.add(new_apply)
        db.session.commit()

    return render_template('drive_apply.html',drive=drive,company=company,student=student)



@app.route('/company_drives_details/<int:comp_id>/<int:stu_id>',methods=['GET','POST'])
def company_drives_details(comp_id,stu_id):
    student = User.query.filter_by(id=stu_id).first()
    company = Profile.query.filter_by(company_id=comp_id).first()
    drives = Drive.query.filter_by(company_id=comp_id).all()

    return render_template('company_drives_details.html',drives=drives,company=company,student=student)





#---------------------------------------END ROUTE--------------------------------------------#
# Run the app and create database
if __name__ == "__main__":
    with app.app_context():
        # db.session.query(Application).delete()
        # db.session.commit()

        existing_admin =  User.query.filter_by(email='admin@portal.com',role='admin').first()
        #create admin if not exist
        if not existing_admin:
            admin_user = User(
                name = 'Admin',
                email = 'admin@portal.com',
                password = 'admin123',
                role = 'admin',
                contact = 1234567890
                )
            db.session.add(admin_user)
            db.session.commit()

        db.create_all()
    app.run(debug=True)


