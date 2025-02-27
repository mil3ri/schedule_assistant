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

    # --- Existing Filters ---
    course_code = request.args.get('course_code')
    name = request.args.get('name')
    if course_code:
        query = query.filter(Lesson.course_code.ilike(f'%{course_code}%'))
    if name:
        query = query.filter(Lesson.name.ilike(f'%{name}%'))

    # --- Basic Time Filters ---
    days_str = request.args.get('days')
    start_time_str = request.args.get('start_time')  # e.g., "09.00"
    end_time_str = request.args.get('end_time')      # e.g., "17.00"

    if days_str:
        days_list = days_str.split(',')
        # Create a list of day filters (case-insensitive and partial matching)
        day_filters = [Lesson.days.ilike(f'%{day}%') for day in days_list]
        query = query.filter(db.or_(*day_filters)) # Apply OR across all day filters

    if start_time_str:
        start_hour = int(start_time_str.split('.')[0])  # Extract hour (e.g., 9)
        query = query.filter(db.func.substr(Lesson.hours,1,2) >= str(start_hour-8).zfill(2))  # hours >= start_hour

    if end_time_str:
            end_hour = int(end_time_str.split('.')[0])
            query = query.filter(db.func.substr(Lesson.hours, 1, 2) <= str(end_hour - 8).zfill(2))

    # --- Advanced Time Filters ---
    time_slots_str = request.args.get('time_slots')
    if time_slots_str:
        time_slots = time_slots_str.split(';')
        slot_filters = []
        for slot in time_slots:
            day, time_val = slot.split(" ")
            hour_val = time_val.split(".")[0]

            slot_filters.append(db.and_(Lesson.days.ilike(f'%{day}%'), db.func.substr(Lesson.hours, 1, 2) == str(int(hour_val) -8).zfill(2) ))

        query = query.filter(db.or_(*slot_filters))

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