document.getElementById('userForm').addEventListener('submit', function (event) {
    event.preventDefault();

    let studentData = {
        name: document.getElementById("name").value,
        age: document.getElementById("age").value,
        gender: document.getElementById("gender").value,
        class: document.getElementById("class").value,
        country: document.getElementById("country").value,
        state: document.getElementById("state").value,
        city: document.getElementById("city").value,
        parent_name: document.getElementById("parent_name").value,
        parent_occupation: document.getElementById("parent_occupation").value,
        financial_status: document.getElementById("financial_status").value,
        username: document.getElementById("username").value,
        password: document.getElementById("password").value
    };

    fetch('http://127.0.0.1:5000/register', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", // ✅ Ensures cookies (session) are sent
        body: JSON.stringify(studentData)
    })
        .then(response => response.json())
        .then(data => {
            console.log("✅ Server Response:", data);
            if (data.success) {
                alert("Registration successful! Redirecting...");
                window.location.href = "http://127.0.0.1:5000/home";
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => {
            console.error('❌ Fetch Error:', error);
            alert("Something went wrong! Please try again.");
        });

    document.getElementById('loginForm').addEventListener('submit', function (event) {
        event.preventDefault();

        let loginData = {
            username: document.getElementById("loginUsername").value,
            password: document.getElementById("loginPassword").value
        };

        fetch('http://127.0.0.1:5000/login', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(loginData)
        })
            .then(response => response.json())
            .then(data => {
                console.log("✅ Server Response:", data);

                if (data.success) {
                    // ✅ Store user_id and username in `localStorage`
                    localStorage.setItem("user_id", data.user_id);
                    localStorage.setItem("username", loginData.username);

                    alert("Login successful! Redirecting...");
                    window.location.href = "home.html";
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(error => {
                console.error('❌ Fetch Error:', error);
                alert("Something went wrong! Please try again.");
            });
    });


});






function submitAssessment(userId, marks) {
    let resultData = { user_id: userId, marks: marks };

    console.log("📌 Sending Assessment Data:", resultData);  // Debugging

    fetch('http://127.0.0.1:5000/store_results', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(resultData)
    })
        .then(response => response.json())
        .then(data => {
            console.log("📌 Response Received:", data); // Debugging
            if (data.success) {
                alert("Assessment submitted successfully!");
                window.location.href = "dashboard.html"; // Redirect after submission
            } else {
                alert("Error: " + (data.error || "Something went wrong!"));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("Something went wrong! Please try again.");
        });
}

// ✅ Move `startAssessment(course)` function OUTSIDE of event listener
function startAssessment(course) {
    console.log("Selected course:", course);  // Debugging: Check if function is triggered
    localStorage.setItem("selected_course", course);
    window.location.href = "pre_assessment.html";
}

