from flask import Flask, render_template, request, jsonify
from models import db, Lesson
from datetime import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lessons.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables (run once)
with app.app_context():
    db.create_all()
    print("Database tables created")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/lessons', methods=['GET'])
def get_lessons():
    query = Lesson.query
    # All filters
    filters = {
        'course_code': request.args.get('course_code'),
        'name': request.args.get('name'),
        'day': request.args.get('day'),
        'instructor': request.args.get('instructor'),
        'classroom': request.args.get('classroom')
    }
    
    for key, value in filters.items():
        if value:
            query = query.filter(getattr(Lesson, key).ilike(f'%{value}%'))
    
    lessons = query.all()
    return jsonify([{
        'course_code': lesson.course_code,
        'name': lesson.name,
        'day': lesson.days,
        'time': f"{lesson.start_time.strftime('%H:%M')} - {lesson.end_time.strftime('%H:%M')}",
        'instructor': lesson.instructor,
        'classroom': lesson.classroom
    } for lesson in lessons])

if __name__ == '__main__':
    app.run(debug=True)