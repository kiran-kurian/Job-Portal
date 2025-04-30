from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobportal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    salary = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        email = request.form['email']
        role = request.form['role']

        if User.query.filter_by(username=username, is_active=True).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        new_user = User(username=username, password=password, email=email, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, is_active=True).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'danger')
        return redirect(url_for('login'))
    role = session['role']
    if role == 'employer':
        jobs = Job.query.filter_by(employer_id=session['user_id'], is_active=True).all()
    elif role == 'job_seeker':
        jobs = db.session.query(Job).join(Application).filter(Application.user_id == session['user_id']).all()
    elif role == 'admin':
        return redirect(url_for('admin_home'))
    return render_template('dashboard.html',role=role, jobs=jobs)

@app.route('/admin/home')
def admin_home():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    user_count = User.query.filter_by(is_active=True).count()
    job_count = Job.query.filter_by(is_active=True).count()
    application_count = Application.query.count()
    return render_template('admin_home.html',
                           user_count=user_count,
                           job_count=job_count,
                           application_count=application_count)

@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if 'user_id' not in session or session['role'] != 'employer':
        flash('You do not have permission to post a job.', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        salary = request.form['salary']
        new_job = Job(title=title, description=description, location=location, salary=salary, employer_id=session['user_id'])
        db.session.add(new_job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('post_job.html')

@app.route('/jobs')
def jobs():
    location = request.args.get('location')
    query = Job.query
    if location:
        query = query.filter(Job.location.contains(location))
    jobs = query.filter_by(is_active=True).all()
    return render_template('job_list.html', jobs=jobs)

@app.route('/apply/<int:job_id>', methods=['GET', 'POST'])
def apply(job_id):
    if 'user_id' not in session or session['role'] != 'job_seeker':
        flash('You do not have permission to apply for a job.', 'danger')
        return redirect(url_for('login'))
    existing = Application.query.filter_by(user_id=session['user_id'], job_id=job_id).first()
    if existing:
        flash('You already applied to this job.')
    else:
        application = Application(user_id=session['user_id'], job_id=job_id)
        db.session.add(application)
        db.session.commit()
        flash('Application submitted.')
    return redirect(url_for('jobs'))

@app.route('/applications')
def applications():
    if 'user_id' not in session or session['role'] != 'employer':
        flash('You do not have permission to view applications.', 'danger')
        return redirect(url_for('login'))
    applications = db.session.query(Application, User, Job)\
        .join(User, Application.user_id == User.id)\
        .join(Job, Application.job_id == Job.id)\
        .filter(Job.employer_id == session['user_id'])\
        .all()
    return render_template('applications.html', applications=applications)

@app.route('/delete_job/<int:job_id>')
def delete_job(job_id):
    if 'user_id' not in session or session['role'] != 'employer':
        flash('You do not have permission to delete a job.', 'danger')
        return redirect(url_for('login'))
    job = Job.query.get_or_404(job_id)
    job.is_active = False
    db.session.commit()
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/manage_users')
def manage_users():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('You do not have permission to manage users.', 'danger')
        return redirect(url_for('login'))
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('You do not have permission to delete a user.', 'danger')
        return redirect(url_for('login'))
    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)