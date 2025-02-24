async function loadLessons() {
    const params = new URLSearchParams({
      course_code: document.getElementById('courseCode').value,
      name: document.getElementById('courseName').value,
      day: document.getElementById('dayFilter').value
    });
  
    const response = await fetch(`/api/lessons?${params}`);
    const lessons = await response.json();
  
    const lessonsList = document.getElementById('lessonsList');
    lessonsList.innerHTML = lessons.map(lesson => `
      <div class="card mb-2">
        <div class="card-body">
          <h5>${lesson.course_code} - ${lesson.name}</h5>
          <p>Day: ${lesson.day}</p>
          <p>Time: ${lesson.time}</p>
          <p>Instructor: ${lesson.instructor}</p>
          <p>Classroom: ${lesson.classroom}</p>
          <button onclick="addToSchedule('${lesson.course_code}')" class="btn btn-success">Add</button>
        </div>
      </div>
    `).join('');
  }