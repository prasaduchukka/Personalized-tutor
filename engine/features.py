import os
import webbrowser
from engine.command import speak
import sqlite3
from hugchat import hugchat
from engine.config import ASSISTANT_NAME

# ASSISTANT_NAME="jarvis"
con = sqlite3.connect("jarvis.db")
cursor = con.cursor()


def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()
     

    # if query!="":
    #    speak("Opening "+query)
    #    os.system('start'+query)
    # else:
    #     speak("not found")
    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")


def chatBot(query):
    user_input = query.lower()
    # chatbot = hugchat.ChatBot(cookies=cookies.get_dict()) 
    chatbot = hugchat.ChatBot(cookie_path="D:\\2nd test web for intel\\engine\\cookies.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response =  chatbot.chat(user_input)
    print(response)
    speak(response)
    return response
