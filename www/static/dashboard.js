function loadDashboard() {
    let student_id = localStorage.getItem("user_id");

    if (!student_id) {
        alert("Error: No student ID found. Please log in again.");
        window.location.href = "signup.html";
        return;
    }

    fetch(`http://127.0.0.1:5000/get-student/${student_id}`)
    .then(response => response.json())
    .then(data => {
        console.log("DEBUG: Student Data from Backend:", data);

        if (data.error) {
            alert("Error fetching user details: " + data.error);
            return;
        }

        document.getElementById("student_name").innerText = data.name || "Unknown";
        document.getElementById("assigned_course").innerText = data.course_name || "No Course Assigned";
        document.getElementById("recommended_course").innerText = data.recommended_course || "Not Assigned";
        document.getElementById("pre_assessment_score").innerText = 
            data.pre_assessment_score !== null ? data.pre_assessment_score : "Not Taken";
        document.getElementById("post_assessment_score").innerText = 
            data.post_assessment_score !== null ? data.post_assessment_score : "Not Taken";
    })
    .catch(error => {
        console.error('ERROR: Failed to Load Dashboard Data', error);
        alert("Error loading dashboard. Please try again.");
    });
}

function updateLearning() {
    let student_id = localStorage.getItem("user_id");
    let post_score = document.getElementById("post_score").value;

    if (!student_id) {
        alert("Error: No student ID found. Please log in again.");
        return;
    }

    if (!post_score) {
        alert("Please enter a valid post-assessment score.");
        return;
    }

    let resultData = {
        student_id: student_id,
        post_score: post_score
    };

    fetch('http://127.0.0.1:5000/update_post_score', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(resultData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Post-assessment score updated successfully!");
            loadDashboard(); // ✅ Refresh dashboard after update
        } else {
            alert("Error: " + (data.error || "Something went wrong!"));
        }
    })
    .catch(error => {
        console.error("Error updating score:", error);
        alert("Something went wrong! Please try again.");
    });
}
