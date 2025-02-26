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

    # Get filter values
    course_code = request.args.get('course_code')
    name = request.args.get('name')
    day = request.args.get('day')
    instructor = request.args.get('instructor')
    classroom = request.args.get('classroom')

    # Apply filters
    if course_code:
        query = query.filter(Lesson.course_code.ilike(f'%{course_code}%'))
    if name:
        query = query.filter(Lesson.name.ilike(f'%{name}%'))
    if day:
        query = query.filter(Lesson.days.ilike(f'%{day}%'))
    if instructor:
        query = query.filter(Lesson.instructor.ilike(f'%{instructor}%'))
    if classroom:
        query = query.filter(Lesson.classroom.ilike(f'%{classroom}%'))

    lessons = query.all()

    lesson_data = []
    for lesson in lessons:
        if lesson.days != "" and lesson.hours != "":
            days_list = []
            hours_list = []
            lesson_count = 0
            lesson.hours = str(lesson.hours) if isinstance(lesson.hours, int) else lesson.hours
            for i in range(len(lesson.days)):
                if lesson.days[i].isupper():
                    lesson_count += 1
                    if i != len(lesson.days) - 1 and lesson.days[i+1].islower():
                        if lesson.days[i] + lesson.days[i+1] == "Th": days_list.append("Thursday")
                        if lesson.days[i] + lesson.days[i+1] == "St": days_list.append("Saturday")
                    elif lesson.days[i] == "M": days_list.append("Monday")
                    elif lesson.days[i] == "T": days_list.append("Tuesday")
                    elif lesson.days[i] == "W": days_list.append("Wednesday")
                    elif lesson.days[i] == "F": days_list.append("Friday")

            if len(lesson.hours) == lesson_count:
                for i in range(len(lesson.hours)):
                    hours_list.append(f"{(int(lesson.hours[i]) + 8):02d}.00 - {(int(lesson.hours[i]) + 8):02d}.50")
            else:
                skip_next = False
                for i in range(len(lesson.hours)):
                    hour = 0
                    if skip_next:
                        skip_next = False
                        continue
                    if lesson.hours[i] == "1":
                        if i < len(lesson.hours) - 1 and lesson.hours[i + 1] == "0":
                            hour = 18
                            skip_next = True
                        elif i != len(lesson.hours) - 1 and lesson.hours[i + 1] == "1":
                            hour = 19
                            skip_next = True
                        else:
                            hour = 9
                    else:
                        hour = int(lesson.hours[i]) + 8
                    hours_list.append(f"{hour:02d}.00 - {hour:02d}.50")
        processed_times = [f" {days_list[i]} {hours_list[i]}" for i in range(lesson_count)]
    
        lesson_data.append({
            'course_code': lesson.course_code,
            'name': lesson.name,
            'days': lesson.days,
            'hours': lesson.hours,
            'processedtimes': processed_times if lesson.days != "" else "",
            'instructor': lesson.instructor,
        })

    return jsonify(lesson_data)

if __name__ == '__main__':
    app.run(debug=True)