// $(document).ready(function () {
//   var siriWave = new SiriWave({
//       container: document.getElementById("siri-container"),
//       width: 600,
//       height: 150,
//       speed: 0.1, // Adjust wave speed
//       amplitude: 1, // Adjust wave height
//       frequency: 6, // Wave peaks
//       style: "ios9",
//       autostart: true
//   });

//   $('.Siritext').textillate({
//     loop: true,
//     sync: true,
//     in: {
//       effect: "fadeInUp",
//       sync: true
//     },
//     out: {
//       effect: "fadeOutUp",
//       sync: true

//     },
//   });

//   $(".bot").click(function () {
//     $(".web-learning").attr("hidden", true);
//     // $(".J-stucture").attr("hidden", true);
//     $(".SiriWave").attr("hidden", false);
//   });

//   // $("#mic").click(function () {
//   //   // $(".J-stucture").attr("hidden", false);
//   //   $(".SiriWave").attr("hidden", false);
//   //   eel.allcommands()()

//   // });

// });


$(document).ready(function () {
    console.log("Main.js loaded"); // Debugging

    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 600,
        height: 150,
        speed: 0.1,
        amplitude: 1,
        frequency: 6,
        style: "ios9",
        autostart: true
    });

    $(".bot").click(function () {
        console.log("Bot button clicked!"); // Debugging
        $(".web-learning").hide();
        $(".SiriWave").show(); // Ensure visibility
    });

    // $("#mic").click(function () {
    //     console.log("Mic button clicked! Listening..."); // Debugging

    //     $(".SiriWave").show(); // Ensure SiriWave is visible

    //     // Call Python function via Eel
    //     eel.allcommands()(); // Ensure Python function exists
    // });
    // // New Feature: Send Text to Chatbot
    // $("#send").click(function () {
    //     let userMessage = $("#chat-input").val().trim(); // Get input value
    //     if (userMessage === "") return; // Prevent empty messages

    //     console.log("User typed:", userMessage);
    //     $(".SiriWave").show(); // Show SiriWave while processing

    //     eel.chat_command(userMessage)(function (response) {
    //         console.log("Bot response:", response);
    //         $(".Siritext").text(response); // Display response
    //     });

    //     $("#chat-input").val(""); // Clear input field after sending
    // });
    
    $("#mic").click(function () {
        console.log("Mic button clicked! Listening...");
        $(".SiriWave").show();

        fetch("/listen", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                console.log("Speech recognized:", data.response);
                $(".Siritext span").text(data.response);
                $(".Siritext").textillate("start");
                $(".SiriWave").hide();
            })
            .catch(error => {
                console.error("Error:", error);
                $(".Siritext span").text("Speech recognition failed. Try again.");
                $(".Siritext").textillate("start");
                $(".SiriWave").hide();
            });
    });

    $("#send").click(function () {
        let userMessage = $("#chat-input").val().trim();
        if (userMessage === "") return;

        console.log("User typed:", userMessage);
        $(".SiriWave").show();

        fetch("/chat", {
            method: "POST",
            body: JSON.stringify({ message: userMessage }),
            headers: { "Content-Type": "application/json" }
        })
        .then(response => response.json())
        .then(data => {
            console.log("Bot response:", data.response);
            $(".Siritext span").text(data.response);
            $(".Siritext").textillate("start");
            $(".SiriWave").hide();
        })
        .catch(error => console.error("Error:", error));

        $("#chat-input").val("");
    });

    $(".Siritext span").textillate({
        loop: true,
        sync: true,
        in: { effect: "fadeInUp", sync: true },
        out: { effect: "fadeOutUp", sync: true }
    });
});

