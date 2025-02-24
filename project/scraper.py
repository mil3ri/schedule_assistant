from models import db, Lesson
from app import app
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_boun():
    url = "https://registration.bogazici.edu.tr/buis/general/schedule.aspx?p=semester"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table', {'class': 'schedule-table'})
    
    for row in table.find_all('tr')[1:]:  # Skip header
        cols = [td.text.strip() for td in row.find_all('td')]
        if len(cols) < 7:
            continue
            
        # BOUN-specific columns (verify indices!)
        course_code = cols[0]
        course_name = cols[1]
        day = cols[2]
        time_range = cols[3]
        instructor = cols[4]
        classroom = cols[5]
        requirements = cols[6]

        # Parse time (e.g., "09:00 - 10:15")
        start_str, end_str = time_range.split(' - ')
        start_time = datetime.strptime(start_str, "%H:%M").time()
        end_time = datetime.strptime(end_str, "%H:%M").time()

        # Add to DB
        with app.app_context():
            if not Lesson.query.filter_by(course_code=course_code, day=day, start_time=start_time).first():
                lesson = Lesson(
                    course_code=course_code,
                    name=course_name,
                    day=day,
                    start_time=start_time,
                    end_time=end_time,
                    instructor=instructor,
                    classroom=classroom,
                    requirements=requirements
                )
                db.session.add(lesson)
            db.session.commit()

if __name__ == '__main__':
    scrape_boun()