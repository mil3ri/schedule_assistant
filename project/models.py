from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), nullable=False)  # New field
    name = db.Column(db.String(200), nullable=False)
    day = db.Column(db.String(10))              # e.g., "Monday"
    start_time = db.Column(db.Time)             # e.g., "09:00"
    end_time = db.Column(db.Time)               # e.g., "10:15"
    instructor = db.Column(db.String(100))
    classroom = db.Column(db.String(50))
    requirements = db.Column(db.String(200))