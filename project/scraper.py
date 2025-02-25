# scraper.py
from selenium import webdriver
import selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from app import app, db
from models import Lesson
import time

def scrape_boun_schedule():
    # Specify the path to the chromedriver executable
    chromedriver_path = "/home/mileri/.wdm/drivers/chromedriver/linux64/133.0.6943.126/chromedriver-linux64/chromedriver"
    driver = webdriver.Chrome(service=Service(chromedriver_path))
    try:
        driver.get("https://registration.bogazici.edu.tr/buis/general/schedule.aspx?p=semester")
        
        # Select semester
        select = Select(driver.find_element(By.ID, "ctl00_cphMainContent_ddlSemester"))
        select.select_by_value("2024/2025-2")  # Update semester as needed
        
        # Submit form
        driver.find_element(By.ID, "ctl00_cphMainContent_btnSearch").click()
        
        # Wait for department links to load
        wait = WebDriverWait(driver, 20)
        department_links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/scripts/sch.asp?donem=2024/2025-2&kisaadi=']")))  # Update the selector as needed
        
        for i in range(len(department_links)):
            retries = 3
            while retries > 0:
                try:
                    department_links[i].click()
                    break
                except selenium.common.exceptions.StaleElementReferenceException:
                    retries -= 1
                    if retries == 0:
                        raise
                    time.sleep(1)
                    department_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/scripts/sch.asp?donem=2024/2025-2&kisaadi=']")
            
            # Wait for table to load
            try:
                table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table[border='1']")))
                print("Table found!")
            except Exception as e:
                print("Table not found:", e)
                driver.back()
                continue
            
            rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header
            
            for row in rows:
                cols = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
                if len(cols) < 9:
                    continue
                    
                # Extract the required values
                course_code = cols[0]
                course_name = cols[2]
                credits = cols[3]
                ects = cols[4]
                instructor = cols[6]
                days = cols[7]
                hours = cols[8]

                # Check if hours are not empty before parsing
                if hours:
                    # Parse the hours to get start and end times
                    start_section = int(hours[0])
                    end_section = int(hours[-1])
                    start_time = (start_section + 8) % 12 + 9  # Convert section to time
                    end_time = (end_section + 8) % 12 + 9
                else:
                    start_time = None
                    end_time = None

                # Add to database
                with app.app_context():
                    lesson = Lesson(
                        course_code=course_code,
                        name=course_name,
                        credits=credits,
                        ects=ects,
                        instructor=instructor,
                        days=days,
                        start_time=start_time,
                        end_time=end_time
                    )
                    db.session.add(lesson)
            
            with app.app_context():
                db.session.commit()
            driver.back()  # Go back to the department list page
        
    finally:
        driver.quit()

if __name__ == '__main__':
    with app.app_context():
        scrape_boun_schedule()