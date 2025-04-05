$(document).ready(function () {

    eel.expose(DisplayMessage)
    function DisplayMessage(message) {

        $(".Siritext li:first").text(message);
        $('.Siritext').textillate('start');

    }


    eel.expose(quit);
    function quit() {
        console.log("Quitting... Stopping SiriWave!");
        $(".web-learning").show();  // Show J.A.R.V.I.S UI
        $(".SiriWave").hide();    // Hide SiriWave
    }

    eel.expose(DisplayMessage);
    function DisplayMessage(message) {
        console.log("Message from Python:", message);
        $(".Siritext").text(message); // Show chatbot response
        $('.Siritext').textillate('start');
    }
});