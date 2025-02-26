from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    credits = db.Column(db.Integer)             # Added field for credits
    ects = db.Column(db.Integer)                # Added field for ects
    days = db.Column(db.String(10))              # e.g., "Monday"
    hours = db.Column(db.Integer)              # e.g., "10:15"
    instructor = db.Column(db.String(100))
    classroom = db.Column(db.String(50))
    requirements = db.Column(db.String(200))