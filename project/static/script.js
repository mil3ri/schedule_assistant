async function loadLessons() {
    const name = document.getElementById('searchName').value;
    const grade = document.getElementById('searchGrade').value;
    
    const params = new URLSearchParams();
    if (name) params.append('name', name);
    if (grade) params.append('grade', grade);

    const response = await fetch(`/api/lessons?${params.toString()}`);
    const lessons = await response.json();

    const lessonsList = document.getElementById('lessonsList');
    lessonsList.innerHTML = lessons.map(lesson => `
        <div class="card mb-2">
            <div class="card-body">
                <h5>${lesson.name}</h5>
                <p>Time: ${new Date(lesson.time).toLocaleString()}</p>
                <p>Grade: ${lesson.grade}</p>
                <button onclick="addToSchedule(${lesson.id})" class="btn btn-success">Add to Schedule</button>
            </div>
        </div>
    `).join('');
}

// TODO: Implement addToSchedule()