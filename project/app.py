from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lessons.db'
db = SQLAlchemy(app)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    grade = db.Column(db.String(20))
    requirements = db.Column(db.String(200))
    description = db.Column(db.String(300))

@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to search/filter lessons
@app.route('/api/lessons', methods=['GET'])
def get_lessons():
    query = Lesson.query
    # Filters
    if name := request.args.get('name'):
        query = query.filter(Lesson.name.contains(name))
    if grade := request.args.get('grade'):
        query = query.filter_by(grade=grade)
    # Add more filters for time/requirements...
    lessons = query.all()
    return jsonify([{
        'id': lesson.id,
        'name': lesson.name,
        'time': lesson.time.isoformat(),
        'grade': lesson.grade
    } for lesson in lessons])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)