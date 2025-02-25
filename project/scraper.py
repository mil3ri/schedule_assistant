# scraper.py
import argparse
from selenium import webdriver
import selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import time, datetime  # Import datetime
from app import app, db
from models import Lesson
import time as pytime  # Rename the imported time module
import os  # Import the os module


def scrape_boun_schedule(headless=False):
    # Specify the path to the chromedriver executable
    chromedriver_path = "/home/mileri/.wdm/drivers/chromedriver/linux64/133.0.6943.126/chromedriver-linux64/chromedriver"
    
    # Configure Chrome options
    chrome_options = webdriver.ChromeOptions()
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
    
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
                    pytime.sleep(1)
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
                    try:
                        start_section = int(hours[0])
                        end_section = int(hours[-1])
                        start_time = time(hour=(start_section - 1 + 8) % 24)
                        end_time = time(hour=(end_section - 1 + 8) % 24)
                    except ValueError as e:
                        print(f"Error parsing time: {e}, Hours: {hours}")
                        start_time = None
                        end_time = None

                else:
                    start_time = None
                    end_time = None

                # Print extracted data for debugging
                print(f"Extracted data: {course_code}, {course_name}, {credits}, {ects}, {instructor}, {days}, {start_time}, {end_time}")
                # Database interaction with extensive debugging
                with app.app_context():
                    print("Entered app context")
                    try:
                        lesson = Lesson(
                            course_code=course_code,
                            name=course_name,
                            credits=int(credits) if credits else None,
                            ects=int(ects) if ects else None,
                            instructor=instructor,
                            days=days,
                            start_time=start_time,
                            end_time=end_time
                        )
                        print(f"Lesson object created: {lesson}")

                        db.session.add(lesson)
                        print("Lesson added to session")

                        db.session.commit()
                        print("Session committed")
                        print(f"Data for lesson successfully recorded in the database.")


                    except Exception as e:
                        print(f"DATABASE ERROR: {e}")  # Catch any database errors
                        db.session.rollback()  # Rollback if there's an error
                        print("Session rolled back")

            driver.back()  # Go back to the department list page

    finally:
        driver.quit()
        print("Driver quit")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scrape BOUN schedule")
    parser.add_argument('--nogui', action='store_true', help="Run in headless mode (no GUI)")
    args = parser.parse_args()

    with app.app_context():
      db_file_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
      print(f"Database file path: {db_file_path}") #Prints db file path

      if not os.path.exists(db_file_path):
          print("Creating database...")
          db.create_all()
          print("Database created.")
      else:
          print("Database already exists.")

      scrape_boun_schedule(headless=args.nogui)