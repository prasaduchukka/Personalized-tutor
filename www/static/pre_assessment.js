async function calculateScore() {
    const sessionCheck = await fetch('http://127.0.0.1:5000/check_session', {
        credentials: 'include'  // Required for cookies
    });

    const sessionData = await sessionCheck.json();
    if (!sessionData.logged_in) {
        alert("User not logged in!");
        return;
    }

    let score = 0;
    let answers = {
        q1: "A",//uido van Rossum
        q2: "B", // # This is a comment
        q3: "C", // 8 (2 ** 3)
        q4: "B", // 3 (10 // 3 is floor division)
        q5: "D", // ArrayList (not a Python data type)
        q6: "B", // x = 5 (Python doesn't require var, int, or let)
        q7: "B", // def (used to define functions)
        q8: "B", // # This is a comment
        q9: "D", // All of the above (len() works on strings, lists, etc.)
        q10: "B" // for x in list: (correct syntax)
    };

    for (let key in answers) {
        let selectedOption = document.querySelector(`input[name="${key}"]:checked`);
        if (selectedOption && selectedOption.value === answers[key]) {
            score++;
        }
    }

    document.getElementById("score").innerText = `${score}/10`;

    // ✅ Submit assessment data (Send to backend)
    submitAssessment(sessionData.user_id, score);

    // ✅ Navigate to dashboard after showing score
    setTimeout(() => {
        window.location.href = "dashboard.html";
    }, 3000); // Redirect after 3 seconds
}

function submitAssessment(user_id, score) {
    let resultData = {
        user_id: user_id,  // Ensure user ID is sent
        marks: score,
        course_name: "Python Fundamentals" 
    };

    console.log("📌 Sending Assessment Data:", resultData);

    fetch('http://127.0.0.1:5000/store_results', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(resultData)
    })
    .then(response => response.json())
    .then(data => {
        console.log("📌 Response Received:", data);
        if (data.success) {
            alert("Assessment submitted successfully!");
            window.location.href = "dashboard.html"; 
        } else {
            alert("Error: " + (data.error || "Something went wrong!"));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Something went wrong! Please try again.");
    });
}
