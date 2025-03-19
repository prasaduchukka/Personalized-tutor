// function loadDashboard() {
//     let student_id = localStorage.getItem("student_id");

//     if (!student_id) {
//         alert("Error: No student ID found. Please log in again.");
//         window.location.href = "signup.html";
//         return;
//     }

//     fetch(`http://127.0.0.1:5000/get-student/${student_id}`)
//     .then(response => response.json())
//     .then(data => {
//         console.log("DEBUG: Student Data from Backend:", data);

//         document.getElementById("student_name").innerText = data.name || "Unknown";
//         document.getElementById("assigned_course").innerText = data.course_name || "No Course Assigned";
//         document.getElementById("recommended_course").innerText = data.recommended_course || "Not Assigned";
//         document.getElementById("pre_assessment_score").innerText = data.pre_assessment_score !== null ? data.pre_assessment_score : "Not Taken";

//         let modules = getModules(data.recommended_course);
//         document.getElementById("course_modules").innerHTML = modules;
//     })
//     .catch(error => {
//         console.error('ERROR: Failed to Load Dashboard Data', error);
//         alert("Error loading dashboard. Please try again.");
//     });
// }

// window.onload = loadDashboard;
function loadDashboard() {
    // Fetch the currently logged-in user
    fetch("http://127.0.0.1:5000/current_user", {
        method: "GET",
        credentials: "include"  // ✅ Ensures cookies (session) are sent
    })
        .then(response => response.json())
        .then(data => {
            if (!data.logged_in) {
                alert("Session expired. Redirecting to login.");
                window.location.href = "login.html";
            } else {
                console.log("✅ Logged-in user:", data);
            }
            // Display logged-in user (if there's a UI element for it)
            document.getElementById("logged_user").innerText = userData.user.name || "Unknown User";

            // Fetch student data using localStorage student_id
            let student_id = localStorage.getItem("student_id");

            if (!student_id) {
                alert("Error: No student ID found. Please log in again.");
                window.location.href = "signup.html";
                return;
            }

            fetch(`http://127.0.0.1:5000/get-student/${student_id}`)
                .then(response => response.json())
                .then(data => {
                    console.log("DEBUG: Student Data from Backend:", data);

                    document.getElementById("student_name").innerText = data.name || "Unknown";
                    document.getElementById("assigned_course").innerText = data.course_name || "No Course Assigned";
                    document.getElementById("recommended_course").innerText = data.recommended_course || "Not Assigned";
                    document.getElementById("pre_assessment_score").innerText = data.pre_assessment_score !== null ? data.pre_assessment_score : "Not Taken";

                    let modules = getModules(data.recommended_course);
                    document.getElementById("course_modules").innerHTML = modules;
                })
                .catch(error => {
                    console.error("ERROR: Failed to Load Dashboard Data", error);
                    alert("Error loading dashboard. Please try again.");
                });

        })
        .catch(error => console.error("ERROR: Failed to fetch logged-in user", error));
}

window.onload = loadDashboard;
