# Home Services

A simple Flask web app for booking home and auto care services, with user registration, login, profile management, booking requests, and an admin dashboard.

## Features

- User registration and login
- Service booking form for customers
- Profile address updates
- Admin dashboard to view all booking requests
- SQLite database with Flask-SQLAlchemy
- Password hashing with Werkzeug

## Requirements

- Python 3.10+
- Flask 3.0.2
- Flask-SQLAlchemy 3.1.1
- Flask-Login 0.6.3
- Werkzeug 3.0.1

## Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. Open your browser at `http://127.0.0.1:5000`

## Notes

- The first user to register becomes the admin automatically.
- Admin users can view all booking requests at `/admin/dashboard`.
