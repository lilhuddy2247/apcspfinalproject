import os

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='client', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(50), nullable=False)
    scheduled_date = db.Column(db.String(50), nullable=False)
    scheduled_time = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')

        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash('Username or Email already registered.', 'danger')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        is_admin = False
        if 'admin' in username.lower() or User.query.count() == 0:
            is_admin = True

        new_user = User(username=username, email=email, password=hashed_pw, address=address, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))

        flash('Login unsuccessful. Please check email and password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        service_type = request.form.get('service_type')
        scheduled_date = request.form.get('scheduled_date')
        scheduled_time = request.form.get('scheduled_time')
        notes = request.form.get('notes')

        new_booking = Booking(
            service_type=service_type,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            notes=notes,
            user_id=current_user.id
        )
        db.session.add(new_booking)
        db.session.commit()
        flash('Your booking request has been submitted!', 'success')
        return redirect(url_for('dashboard'))

    user_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('dashboard.html', bookings=user_bookings)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.address = request.form.get('address')
        db.session.commit()
        flash('Address updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('profile.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Administrators only.', 'danger')
        return redirect(url_for('dashboard'))

    all_bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('admin_dashboard.html', bookings=all_bookings)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
