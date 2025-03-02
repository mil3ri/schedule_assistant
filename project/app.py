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

    # Existing filters
    course_code = request.args.get('course_code')
    name = request.args.get('name')
    max_grade = request.args.get('max_grade')
    min_credits = request.args.get('min_credits')
    selected_times = request.args.get('selected_times', '').split(',')
    elasticity = int(request.args.get('elasticity', 0))


    if course_code:
        query = query.filter(Lesson.course_code.ilike(f'%{course_code}%'))
    if name:
        query = query.filter(Lesson.name.ilike(f'%{name}%'))
    if min_credits:
        query = query.filter(Lesson.credits >= int(min_credits))

    lessons = query.all()
    filtered_lessons = []


    for lesson in lessons:
        if max_grade:
            grade = None
            for char in lesson.course_code:
                if char.isdigit():
                    grade = int(char)
                    break
            if grade is None or grade > int(max_grade):
                continue  # Skip this lesson

        if lesson.days != "" and lesson.hours != "":
            days_list = []
            hours_list = []
            check_hours_list = []
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
                    check_hours_list.append(f"{(int(lesson.hours[i]) + 8):02d}.00")
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
                    check_hours_list.append(f"{hour:02d}.00")
        processed_times = [f" {days_list[i]} {hours_list[i]}" for i in range(lesson_count)]
        check_processed_times = [f"{days_list[i]}-{check_hours_list[i]}" for i in range(lesson_count)]


        # Conflict calculation
        conflict_count = 0
        for time_slot in check_processed_times:
            if time_slot not in selected_times:
                conflict_count += 1

        if conflict_count <= elasticity:
            filtered_lessons.append({
                'course_code': lesson.course_code,
                'name': lesson.name,
                'processedtimes': ', '.join(processed_times),
                'instructor': lesson.instructor
            })

    return jsonify(filtered_lessons)

if __name__ == '__main__':
    app.run(debug=True)