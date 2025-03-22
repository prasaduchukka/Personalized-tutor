function calculateScore() {
    let score = 0;
    let answers = {
        q1: "D", // Guido van Rossum
        q2: "B", // # This is a comment
        q3: "C", // 8
        q4: "B", // 3
        q5: "D", // ArrayList (not a Python data type)
        q6: "B", // x = 5
        q7: "B", // def
        q8: "B", // # This is a comment (duplicate question)
        q9: "D", // All of the above
        q10: "B" // for x in list:
    };

    for (let key in answers) {
        let selectedOption = document.querySelector(`input[name="${key}"]:checked`);
        if (selectedOption && selectedOption.value === answers[key]) {
            score++;
        }
    }

    document.getElementById("score").innerText = `${score}/10`;

    // ✅ Get user ID from localStorage
    let userId = localStorage.getItem('user_id');

    if (!userId) {
        alert("User not logged in!");
        return;
    }

    // ✅ Submit assessment data (Send to backend)
    submitAssessment(userId, score);

    // ✅ Navigate to dashboard after showing score
    setTimeout(() => {
        window.location.href = "dashboard.html";
    }, 3000); // Redirect after 3 seconds
}

// ✅ Function to send user ID and marks to backend (Flask API)
function submitAssessment(userId, score) {
    fetch('http://localhost:5000/submit_assessment', {  // Change URL if different
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userId,
            marks: score
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Assessment submitted successfully:", data);
    })
    .catch(error => {
        console.error("Error submitting assessment:", error);
    });
}
