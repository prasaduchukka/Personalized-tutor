import pyttsx3
import speech_recognition as sr
import eel
import time
import pywhatkit as kit

def speak(text):
    text=str(text)
    engine = pyttsx3.init()             #object Creation
    rate = engine.getProperty('rate')   # getting details of current speaking rate
    # print (rate)                        #printing current voice rate
    engine.setProperty('rate', 178)     # setting up new voice rate

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)   #changing index, changes voices. 1 for female
    eel.DisplayMessage(text)
    engine.say(text)
    engine.runAndWait()

@eel.expose
def speech():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        print("Listning....")
        eel.DisplayMessage("listening....")
        r.pause_threshold=1
        r.adjust_for_ambient_noise(source)
        audio =  r.listen(source,20,10)
    try:
        print("recognizing...")
        eel.DisplayMessage("Recognizing....")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said:{query}")
        eel.DisplayMessage(query)
        # speak(query)
        time.sleep(4)
        
    except Exception as e:
        return ""
    
    return query.lower()

# New Function for Handling Text-Based Chat

@eel.expose
def chat_command(user_input):
    print("User typed:", user_input)

    from engine.features import chatBot  # Ensure chatBot function exists
    response = chatBot(user_input)  # Get response from chatbot

    print("Chatbot response:", response)
    eel.DisplayMessage(response)  # Show response on UI
    return response  # Send response back to JavaScript


@eel.expose
def allcommands():
    query=speech()
    print(query)

    if "open" in query:
        from engine.features import openCommand
        openCommand(query)
    
    elif "play" in query:
        query=query.replace('play','')
        print("Playing"+query)
        speak("Playing"+query)
        kit.playonyt(query)
    elif "search" in query:
        query=query.replace('search','')
        print("Searching"+query)
        speak("Searching"+query)
        kit.search(query)
    elif "jarvis" in query or  "when" in query or "bro" in query:
        # print("no")
        query=query.replace('jarvis','')
        query=query.replace('bro','')
        from engine.features import chatBot
        chatBot(query)
    else:
        print("no prin t")

    eel.quit()
