import sys
import os
# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from flask import Flask, request, jsonify, session, send_from_directory, redirect
import mysql.connector
from flask_cors import CORS
import os  # Use environment variables for security
from bcrypt import hashpw, gensalt, checkpw  # Import bcrypt for password hashing
from secret import secret_key
from engine.ai_recommendation import AIRecommendationEngine
import openai  # Add OpenAI import
from dotenv import load_dotenv  # Add dotenv import
import pyttsx3
import speech_recognition as sr
import pywhatkit as kit
import webbrowser
import time
import os
import webbrowser
import sqlite3
from hugchat import hugchat

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')  # Make sure to set this environment variable

from flask_session import Session# Initialize the session

app = Flask(__name__)
app = Flask(__name__, static_folder="static", static_url_path="/")

# app = Flask(__name__)
# CORS(app)

app.secret_key = secret_key  # Required for session handling
CORS(app, 
     supports_credentials=True, 
    #  origins=["http://127.0.0.1:5000", "http://localhost:5000", "http://127.0.0.1:5502", "http://localhost:5502"],
     origins=["http://127.0.0.1:5000", "http://localhost:5000", "http://127.0.0.1:5500", "http://localhost:5500"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

app.config["SESSION_TYPE"] = "filesystem"  # Store sessions on disk
app.config["SESSION_PERMANENT"] = False  # Sessions should not expire automatically
app.config["SESSION_USE_SIGNER"] = True  # Secure session cookies
app.config["SESSION_KEY_PREFIX"] = "flask_"  # Prefix for session keys
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Allow cross-site cookies
app.config["SESSION_COOKIE_SECURE"] = False  # Set to True in production with HTTPS
app.config["SESSION_COOKIE_HTTPONLY"] = True  # Prevent JavaScript access to cookies
app.config["SESSION_COOKIE_DOMAIN"] = None  # Allow cookies for all domains in development

Session(app)  

# ✅ Function to create a new DB connection for each request
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Change to os.getenv("DB_USER") for production security
        password="MYsql@123",  # Change to os.getenv("DB_PASS") for security
        database="aicourse"
    )

# Initialize AI Recommendation Engine
ai_engine = AIRecommendationEngine()

@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        required_fields = ["name", "age", "gender", "class", "country", "state", "city", 
                           "parent_name", "parent_occupation", "financial_status", "username", "password"]
        
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        hashed_password = hashpw(data['password'].encode('utf-8'), gensalt()).decode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO users 
            (name, age, gender, class, country, state, city, parent_name, parent_occupation, 
            financial_status, username, password_hash) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data['name'], data['age'], data['gender'], data['class'], 
            data['country'], data['state'], data['city'], 
            data['parent_name'], data['parent_occupation'], data['financial_status'], 
            data['username'], hashed_password
        )

        cursor.execute(query, values)
        conn.commit()
        student_id = cursor.lastrowid  

        # ✅ Set session after registration
        session["user_id"] = student_id
        session["username"] = data["username"]

        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Student registered successfully!", "student_id": student_id})

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500



@app.route('/login', methods=['POST'])
def login_user():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT id, username, password_hash FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user and checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
            session.clear()  # Clear any existing session
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            print(f"✅ Logged in User: ID={user['id']}, Username={user['username']}")

            return jsonify({
                "success": True, 
                "message": "Login successful!", 
                "user_id": user["id"],
                "username": user["username"],
                "redirect": "http://127.0.0.1:5000/home"  # Updated redirect URL
            })
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/home')
def serve_home():
    if 'user_id' not in session:
        return redirect('/')  # Redirect to login if not authenticated
    return send_from_directory('static', 'home.html')

@app.route('/dashboard')
def serve_dashboard():
    if 'user_id' not in session:
        return redirect('/')  # Redirect to login if not authenticated
    return send_from_directory('static', 'dashboard.html')

@app.route('/check_session')
def check_session():
    if "user_id" in session:
        return jsonify({"logged_in": True, "user_id": session["user_id"]})
    return jsonify({"logged_in": False}), 401



# Get courses and check enrollment status
@app.route("/get_courses", methods=["GET"])
def get_courses():
    user_id = session.get("user_id")  # Assuming the user is logged in

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    for course in courses:
        cursor.execute("SELECT * FROM user_courses WHERE user_id = %s AND course_id = %s", (user_id, course["course_id"]))
        enrollment = cursor.fetchone()
        course["enrolled"] = True if enrollment else False

    cursor.close()
    connection.close()

    return jsonify(courses)



# Enroll a user in a course
@app.route("/enroll", methods=["POST"])
def enroll_course():
    data = request.json
    user_id = session.get("user_id")
    course_id = data.get("course_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check if the user is already enrolled
    cursor.execute("SELECT * FROM user_courses WHERE user_id = %s AND course_id = %s", (user_id, course_id))
    existing = cursor.fetchone()

    if existing:
        return jsonify({"message": "Already enrolled"}), 200

    # Insert enrollment
    cursor.execute("INSERT INTO user_courses (user_id, course_id) VALUES (%s, %s)", (user_id, course_id))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({"message": "Enrolled successfully"})


@app.route("/get_enrolled_courses", methods=["GET"])
def get_enrolled_courses():
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Unauthorized", "debug": "No user ID in session"}), 401

    print("User ID:", user_id)  # Debugging

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT course_id FROM user_courses WHERE user_id = %s", (user_id,))
    enrolled_courses = cursor.fetchall()

    if not enrolled_courses:
        cursor.close()
        connection.close()
        return jsonify([])

    course_ids = [course["course_id"] for course in enrolled_courses]
    format_strings = ",".join(["%s"] * len(course_ids))
    cursor.execute(f"SELECT * FROM courses WHERE course_id IN ({format_strings})", tuple(course_ids))
    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(courses)

@app.route('/get_results', methods=['GET'])
def get_results():
    user_id = session.get("user_id")  # Fetch user_id from session

    if not user_id:
        return jsonify({"error": "Unauthorized", "debug": "No user ID in session"}), 401

    print(f"🔍 Fetching results for User ID: {user_id}")  # Debugging

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch only results for the logged-in user
        query = """
            SELECT course_name, marks, date_completed 
            FROM results 
            WHERE user_id = %s 
            ORDER BY date_completed DESC 
            LIMIT 1;
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"message": "No results found for the user"}), 404

        print(f"✅ Retrieved result: {result}")  # Debugging

        return jsonify(result), 200

    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
        return jsonify({"error": "Database connection failed", "details": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()



# ✅ API: Get current logged-in user
@app.route('/current_user', methods=['GET'])
def get_current_user():
    if "user_id" in session:
        return jsonify({"user_id": session["user_id"], "username": session["username"]})
    return jsonify({"error": "No user logged in"}), 401





# ----------------- Database Connection -----------------
con = sqlite3.connect("jarvis.db", check_same_thread=False)
cursor = con.cursor()

# ---------------- Text-to-Speech Function ----------------
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 178)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.say(text)
    engine.runAndWait()
    # eel.DisplayMessage(text)
    return text  # Return text to display in UI
# ---------------- Speech Recognition Route ----------------
@app.route('/listen', methods=['POST'])
def listen():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=10)

        query = recognizer.recognize_google(audio, language='en-in').lower().strip()
        print(f"User said: {query}")

        if "open" in query:
            return jsonify(openCommand(query.replace("open", "").strip()))
        elif "play" in query:
            speak(f"Playing {query}")
            kit.playonyt(query)
            return jsonify({"response": f"Playing {query}"})
        elif "search" in query:
            speak(f"Searching {query}")
            kit.search(query)
            return jsonify({"response": f"Searching {query}"})
        elif "jarvis" in query or "bro" in query or "when" in query:
            return chatBot(query.replace("jarvis", "").replace("bro", "").strip())
        else:
            return jsonify({"response": "Command not recognized."})

    except sr.UnknownValueError:
        return jsonify({"response": "Sorry, I didn't understand."})
    except sr.RequestError:
        return jsonify({"response": "Speech service unavailable."})
    except Exception as e:
        print(f"Error in listen(): {str(e)}")  # Debugging
        return jsonify({"response": "Error occurred while processing your request."})

# ---------------- Chatbot Response Route ----------------
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    chatbot = hugchat.ChatBot(cookie_path="D:\\2nd test web for intel\\engine\\cookies.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response = chatbot.chat(user_message)

    print("Chatbot response:", response)
    # Speak the response (voice output)
    spoken_text = speak(response)  
    # return response
    # Send the response back to the frontend to display
    return jsonify({"response": spoken_text})

# ---------------- Open App/Website Route ----------------
@app.route('/command', methods=['POST'])
def execute_command():
    data = request.json
    query = data.get("command", "").lower()

    if "open" in query:
        return jsonify(openCommand(query.replace("open", "").strip()))

    return jsonify({"response": "Command not recognized."})

def openCommand(query):
    try:
        cursor.execute('SELECT path FROM sys_command WHERE name=?', (query,))
        results = cursor.fetchall()

        if results:
            speak(f"Opening {query}")
            os.startfile(results[0][0])
            return {"response": f"Opened {query}"}

        cursor.execute('SELECT url FROM web_command WHERE name=?', (query,))
        results = cursor.fetchall()

        if results:
            speak(f"Opening {query}")
            webbrowser.open(results[0][0])
            return {"response": f"Opened {query}"}

        return {"response": f"No known app or website for '{query}'"}

    except Exception as e:
        return {"error": f"Could not open the requested item: {str(e)}"}

def chatBot(query):
    chatbot = hugchat.ChatBot(cookie_path="D:\\2nd test web for intel\\engine\\cookies.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response = chatbot.chat(query)

    print("Chatbot response:", response)
    speak(response)  # ✅ Speaks response
    # eel.DisplayMessage(response)  # ✅ Updates UI with chatbot response
    return {"response": response}

    
#-------------------------------Course end points----------------------------------------->

@app.route('/api/courses/<int:course_id>/dashboard', methods=['GET'])
def get_course_dashboard(course_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get course progress data
        cursor.execute("""
            SELECT c.title, 
                   COUNT(m.module_id) AS total_modules,
                   c.description
            FROM courses c
            LEFT JOIN modules m ON c.course_id = m.course_id
            WHERE c.course_id = %s
            GROUP BY c.course_id
        """, (course_id,))
        course_data = cursor.fetchone()
        
        if not course_data:
            return jsonify({"error": "Course not found"}), 404
        
        # Get completed modules count
        cursor.execute("""
            SELECT COUNT(*) AS completed_modules
            FROM user_modules um
            JOIN modules m ON um.module_id = m.module_id
            WHERE um.user_id = %s AND m.course_id = %s AND um.status = 'completed'
        """, (user_id, course_id))
        completed = cursor.fetchone()
        
        # Get learning path
        cursor.execute("""
            SELECT learning_path FROM user_courses
            WHERE user_id = %s AND course_id = %s
        """, (user_id, course_id))
        learning_path = cursor.fetchone()

        # Get video progress for all videos in the course
        cursor.execute("""
            SELECT v.video_id, v.title, v.module_id,
                   COALESCE(uv.percent_watched, 0) as percent_watched,
                   uv.watch_date, uv.notes, uv.rating
            FROM videos v
            LEFT JOIN user_videos uv ON v.video_id = uv.video_id AND uv.user_id = %s
            WHERE v.module_id IN (
                SELECT module_id FROM modules WHERE course_id = %s
            )
            ORDER BY v.module_id, v.sequence_order
        """, (user_id, course_id))
        video_progress = cursor.fetchall()

        # Format video progress data
        formatted_videos = []
        for video in video_progress:
            video_dict = dict(video)
            video_dict['percent_watched'] = float(video_dict['percent_watched']) if video_dict['percent_watched'] else 0
            formatted_videos.append(video_dict)
        
        return jsonify({
            "course": {
                "title": course_data['title'],
                "description": course_data['description']
            },
            "total_modules": course_data['total_modules'],
            "completed_modules": completed['completed_modules'] if completed else 0,
            "recommended_path": learning_path['learning_path'] if learning_path else 'standard',
            "video_progress": formatted_videos
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/courses/<int:course_id>/path', methods=['POST'])
def update_learning_path(course_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    data = request.json
    path = data.get('path')
    
    if path not in ['advanced', 'standard', 'remedial']:
        return jsonify({"error": "Invalid path"}), 400
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE user_courses 
            SET learning_path = %s 
            WHERE user_id = %s AND course_id = %s
        """, (path, user_id, course_id))
        
        conn.commit()
        return jsonify({"success": True})
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/courses/<int:course_id>/modules/<int:module_id>/start', methods=['POST'])
def start_module(course_id, module_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_progress (user_id, module_id, started) 
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE started = NOW()
        """, (user_id, module_id))
        
        conn.commit()
        return jsonify({"success": True})
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/videos/<int:video_id>/watch', methods=['POST'])
def watch_video(video_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First get module_id for this video
        cursor.execute("SELECT module_id FROM videos WHERE video_id = %s", (video_id,))
        video = cursor.fetchone()
        
        if not video:
            return jsonify({"error": "Video not found"}), 404
        
        cursor.execute("""
            INSERT INTO user_videos (user_id, video_id, module_id, watched) 
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE watched = NOW()
        """, (user_id, video_id, video['module_id']))
        
        conn.commit()
        return jsonify({"success": True})
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/courses/<int:course_id>/modules/<int:module_id>/quiz', methods=['GET', 'POST'])
def handle_quiz(course_id, module_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'GET':
            # Get quiz questions for this module
            cursor.execute("""
                SELECT question_id, question_text, question_type, options 
                FROM questions
                WHERE module_id = %s
                ORDER BY RAND()
                LIMIT 10  # Get 10 random questions
            """, (module_id,))
            questions = cursor.fetchall()
            
            # Format questions for frontend
            formatted_questions = []
            for q in questions:
                question = {
                    'question_id': q['question_id'],
                    'question_text': q['question_text'],
                    'question_type': q['question_type']
                }
                
                if q['question_type'] == 'multiple_choice' and q['options']:
                    try:
                        question['options'] = json.loads(q['options'])
                    except json.JSONDecodeError:
                        question['options'] = {}
                
                formatted_questions.append(question)
            
            return jsonify({"questions": formatted_questions})
            
        elif request.method == 'POST':
            data = request.get_json()
            answers = data.get('answers', {})
            
            # Get all questions for this module to calculate score
            cursor.execute("""
                SELECT question_id, correct_answer, points 
                FROM questions 
                WHERE module_id = %s
            """, (module_id,))
            questions = cursor.fetchall()
            
            total_points = 0
            earned_points = 0
            
            for q in questions:
                total_points += q['points']
                if str(q['question_id']) in answers:
                    if answers[str(q['question_id'])] == q['correct_answer']:
                        earned_points += q['points']
            
            score = (earned_points / total_points) * 100 if total_points > 0 else 0
            
            # Store exam result
            cursor.execute("""
                INSERT INTO user_exams (user_id, exam_id, score, completed_at)
                SELECT %s, exam_id, %s, NOW() FROM exams WHERE module_id = %s
                ON DUPLICATE KEY UPDATE score = VALUES(score), completed_at = NOW()
            """, (user_id, score, module_id))
            
            # Update module progress
            cursor.execute("""
                UPDATE user_modules
                SET status = 'completed', mastery_score = %s, completed_at = NOW()
                WHERE user_id = %s AND module_id = %s
            """, (score, user_id, module_id))
            
            conn.commit()
            
            # Determine next module
            cursor.execute("""
                SELECT m.module_id FROM modules m
                LEFT JOIN user_modules um ON m.module_id = um.module_id AND um.user_id = %s
                WHERE m.course_id = %s AND m.sequence_order > (
                    SELECT sequence_order FROM modules WHERE module_id = %s
                ) AND (um.status IS NULL OR um.status = 'not_started')
                ORDER BY m.sequence_order
                LIMIT 1
            """, (user_id, course_id, module_id))
            next_module = cursor.fetchone()
            
            return jsonify({
                'success': True,
                'score': score,
                'passed': score >= 70,
                'next_module': next_module['module_id'] if next_module else None
            })
            
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()






# ✅ API: Get All Courses
@app.route('/courses', methods=['GET'])
def get_all_courses():
    db = get_db_connection()  # Create a new connection
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM courses WHERE is_active = 1")
    courses = cursor.fetchall()
    
    cursor.close()  # Close the cursor
    db.close()  # Close the DB connection

    return jsonify({"courses": courses})



# ✅ API: Get all users
@app.route('/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, username FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ✅ API: Get a specific user by ID
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, username FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return jsonify(user)
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/store_results', methods=['POST'])
def store_results():
    try:
        # 1. Check if user is logged in via session
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized - Please log in first"}), 401

        # 2. Get the logged-in user's ID from session
        logged_in_user_id = session["user_id"]
        
        # 3. Validate request data
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        print("📌 Received Assessment Data:", data)

        # 4. Validate required fields (except user_id - we get it from session)
        required_fields = ["marks", "course_name"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "missing_fields": missing_fields
            }), 400

        marks = data["marks"]
        course_name = data["course_name"]

        # 5. Validate data types
        if not isinstance(marks, (int, float)) or marks < 0:
            return jsonify({"error": "Marks must be a positive number"}), 400

        # 6. Database operation
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO results (user_id, course_name, marks, date_completed) 
                VALUES (%s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE 
                    marks = VALUES(marks),
                    date_completed = NOW()
            """
            cursor.execute(query, (logged_in_user_id, course_name, marks))
            conn.commit()

            return jsonify({
                "success": True,
                "message": "Results stored successfully",
                "user_id": logged_in_user_id,
                "course": course_name,
                "score": marks
            })

        except mysql.connector.Error as db_err:
            conn.rollback()
            return jsonify({
                "error": "Database operation failed",
                "details": str(db_err)
            }), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500



@app.route('/course/<int:course_id>/modules', methods=['GET'])
def get_modules(course_id):
    db = get_db_connection()  # ✅ New DB connection
    cursor = db.cursor(dictionary=True)  # ✅ New cursor
    cursor.execute("SELECT * FROM modules WHERE course_id = %s ORDER BY module_id", (course_id,))
    modules = cursor.fetchall()
    
    # ✅ Close connection after use
    cursor.close()
    db.close()

    return jsonify(modules)

@app.route('/unlock-module', methods=['POST'])
def unlock_module():
    data = request.json
    user_id = data['user_id']
    course_id = data['course_id']
    module_id = data['module_id']

    db = get_db_connection()  # ✅ Create a new DB connection
    cursor = db.cursor(dictionary=True)  # ✅ New cursor

    # ✅ Check if the user has completed the current module
    cursor.execute(
        "SELECT status FROM user_progress WHERE user_id = %s AND module_id = %s", 
        (user_id, module_id)
    )
    progress = cursor.fetchone()

    if progress and progress['status'] == 'completed':
        # ✅ Unlock next module
        cursor.execute("""
            UPDATE modules 
            SET status = 'unlocked' 
            WHERE course_id = %s 
            AND module_id = (SELECT MIN(module_id) FROM modules WHERE module_id > %s)
        """, (course_id, module_id))

        db.commit()  # ✅ Save changes

        # ✅ Close connection after execution
        cursor.close()
        db.close()
        
        return jsonify({"message": "Next module unlocked"}), 200

    # ✅ Close connection before returning error
    cursor.close()
    db.close()
    
    return jsonify({"error": "Current module not completed"}), 400



# ✅ API: Select Course & Store Assessment Score
@app.route('/select-course', methods=['POST'])
def select_course():
    try:
        data = request.json
        print("DEBUG: Received Data from Frontend:", data)

        student_id = data.get('id')
        course_name = data.get('course_name', 'Unknown')

        try:
            pre_score = int(data['pre_assessment_score'])
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid pre_assessment_score format"}), 400

        if not student_id:
            return jsonify({"error": "Student ID is missing!"}), 400

        # ✅ Determine course difficulty level
        if pre_score <= 40:
            recommended_course = "Basic"
        elif pre_score <= 70:
            recommended_course = "Medium"
        else:
            recommended_course = "Advanced"

        print(f"DEBUG: Updating Student {student_id} - Course: {course_name}, Score: {pre_score}, Level: {recommended_course}")

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            UPDATE students 
            SET pre_assessment_score = %s, recommended_course = %s, course_name = %s 
            WHERE id = %s
        """
        cursor.execute(query, (pre_score, recommended_course, course_name, student_id))
        conn.commit()

        cursor.close()
        conn.close()

        print("DEBUG: Score and Course Updated Successfully!")
        return jsonify({"recommended_course": recommended_course, "message": "Course updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



# ✅ API: Get Student Details for Dashboard
@app.route('/get-student/<int:student_id>', methods=['GET'])
def get_student_details(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ✅ Fetch student details from `users` table
        query = """
            SELECT u.id, u.name, u.username, u.class, u.country, 
                   s.course_name, s.recommended_course, s.pre_assessment_score, 
                   r.marks AS post_assessment_score
            FROM users u
            LEFT JOIN students s ON u.id = s.id
            LEFT JOIN results r ON u.id = r.user_id
            WHERE u.id = %s
        """
        cursor.execute(query, (student_id,))
        student = cursor.fetchone()

        cursor.close()
        conn.close()

        if student:
            return jsonify(student)
        else:
            return jsonify({"error": "Student not found"}), 404

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)}), 500



# ✅ API: Update Student Score
# @app.route("/update_student_score", methods=["POST"])
# def update_student_score():
    try:
        data = request.get_json()
        print("📌 Received Data:", data)

        student_id = data.get("student_id")
        course_name = data.get("course_name")
        pre_assessment_score = data.get("pre_assessment_score")

        if not student_id or not course_name or pre_assessment_score is None:
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            UPDATE students 
            SET pre_assessment_score = %s, course_name = %s
            WHERE id = %s
        """
        cursor.execute(sql, (pre_assessment_score, course_name, student_id))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Updated successfully!"})
    
    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

# ✅ API: Update Post-Assessment Score
@app.route("/update_post_score", methods=["POST"])
def update_post_score():
    try:
        data = request.get_json()
        student_id = data.get("student_id")
        post_score = data.get("post_score")

        if not student_id or post_score is None:
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "UPDATE students SET post_assessment_score = %s WHERE id = %s"
        cursor.execute(sql, (post_score, student_id))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Post-assessment score updated!"})
    
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500


# ✅ Redirect to Dashboard
@app.route("/redirect_dashboard", methods=["GET"])
def redirect_dashboard():
    try:
        return jsonify({"success": True, "message": "Redirecting to dashboard..."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/get_ai_recommendations', methods=['GET'])
def get_ai_recommendations():
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get user's latest exam scores
        cursor.execute("""
            SELECT ue.exam_id, ue.score, e.module_id
            FROM user_exams ue
            JOIN exams e ON ue.exam_id = e.exam_id
            WHERE ue.user_id = %s
            ORDER BY ue.attempt_date DESC
            LIMIT 5
        """, (user_id,))
        exam_scores = cursor.fetchall()

        # If user has taken exams, use their highest module_id as reference
        if exam_scores:
            # Get the highest module they've passed (score >= 70)
            passed_modules = [score['module_id'] for score in exam_scores if score['score'] >= 70]
            if passed_modules:
                highest_passed_module = max(passed_modules)
                
                # Get next modules in sequence
                cursor.execute("""
                    SELECT m.module_id, m.title, m.description, m.difficulty_level
                    FROM modules m
                    WHERE m.module_id > %s
                    ORDER BY m.sequence_order
                    LIMIT 2
                """, (highest_passed_module,))
            else:
                # If no modules passed, start with basic modules
                cursor.execute("""
                    SELECT m.module_id, m.title, m.description, m.difficulty_level
                    FROM modules m
                    ORDER BY m.sequence_order
                    LIMIT 2
                """)
        else:
            # If no exams taken, start with first modules
            cursor.execute("""
                SELECT m.module_id, m.title, m.description, m.difficulty_level
                FROM modules m
                ORDER BY m.sequence_order
                LIMIT 2
            """)

        recommended_modules = cursor.fetchall()
        
        # Format recommendations
        recommendations = []
        for module in recommended_modules:
            recommendations.append({
                "id": module['module_id'],
                "title": module['title'],
                "description": module['description'],
                "difficulty": module['difficulty_level']
            })

        return jsonify(recommendations)

    except Exception as e:
        print(f"Error in get_ai_recommendations: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/generate_module_test', methods=['POST'])
def generate_module_test():
    try:
        data = request.json
        module_id = data.get('module_id')
        
        if not module_id:
            return jsonify({"error": "Module ID is required"}), 400

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch 8 random questions from your existing questions table
        cursor.execute("""
            SELECT question_id, question_text, options, correct_answer, explanation
            FROM questions
            WHERE module_id = %s
            ORDER BY RAND()
            LIMIT 8
        """, (module_id,))
        
        questions = cursor.fetchall()
        
        if not questions:
            return jsonify({
                "error": "No questions found",
                "message": "No questions are available for this module. Please contact your instructor."
            }), 404

        # Format questions for frontend
        formatted_questions = []
        for q in questions:
            try:
                options = json.loads(q['options']) if isinstance(q['options'], str) else q['options']
                question = {
                    "id": q['question_id'],
                    "question": q['question_text'],
                    "options": options,
                    "correct_answer": q['correct_answer'],
                    "explanation": q['explanation']
                }
                formatted_questions.append(question)
            except json.JSONDecodeError as e:
                print(f"Error parsing options for question {q['question_id']}: {str(e)}")
                continue

        return jsonify({
            "questions": formatted_questions
        })

    except Exception as e:
        print(f"Error generating module test: {str(e)}")
        return jsonify({
            "error": "Failed to generate test",
            "details": str(e)
        }), 500
    finally:
        cursor.close()
        connection.close()

def get_next_recommended_module(user_id, course_id, current_module_id=None):
    """
    Determines the next recommended module based on:
    1. Pre-assessment score (if first time)
    2. Current module's exam score
    3. Overall performance pattern
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # If no current module, check pre-assessment score
        if not current_module_id:
            cursor.execute("""
                SELECT marks 
                FROM results 
                WHERE user_id = %s 
                ORDER BY date_completed DESC 
                LIMIT 1
            """, (user_id,))
            pre_assessment = cursor.fetchone()
            
            if not pre_assessment:
                # No pre-assessment, start with first module
                cursor.execute("""
                    SELECT module_id, title, difficulty_level 
                    FROM modules 
                    WHERE course_id = %s 
                    ORDER BY sequence_order ASC 
                    LIMIT 1
                """, (course_id,))
                return cursor.fetchone()

            # Based on pre-assessment score, determine starting point
            difficulty_level = 'introductory'
            if pre_assessment['marks'] >= 8:
                difficulty_level = 'intermediate'
            elif pre_assessment['marks'] >= 5:
                difficulty_level = 'basic'

            cursor.execute("""
                SELECT module_id, title, difficulty_level 
                FROM modules 
                WHERE course_id = %s AND difficulty_level = %s
                ORDER BY sequence_order ASC 
                LIMIT 1
            """, (course_id, difficulty_level))
            return cursor.fetchone()

        # Get current module's exam results
        cursor.execute("""
            SELECT ue.score, ue.attempt_number, ue.is_passed,
                   m.sequence_order, m.difficulty_level
            FROM user_exams ue
            JOIN exams e ON ue.exam_id = e.exam_id
            JOIN modules m ON e.module_id = m.module_id
            WHERE e.module_id = %s AND ue.user_id = %s
            ORDER BY ue.attempt_date DESC
            LIMIT 1
        """, (current_module_id, user_id))
        exam_result = cursor.fetchone()

        if not exam_result or not exam_result['is_passed']:
            # Failed or no attempt - check if needs to go back to basics
            cursor.execute("""
                SELECT COUNT(*) as failed_attempts
                FROM user_exams ue
                JOIN exams e ON ue.exam_id = e.exam_id
                WHERE e.module_id = %s AND ue.user_id = %s AND ue.is_passed = 0
            """, (current_module_id, user_id))
            failed_count = cursor.fetchone()['failed_attempts']

            if failed_count >= 3:
                # Too many failures, recommend a more basic module
                cursor.execute("""
                    SELECT m.module_id, m.title, m.difficulty_level
                    FROM modules m
                    WHERE m.course_id = %s 
                    AND m.sequence_order < (
                        SELECT sequence_order FROM modules WHERE module_id = %s
                    )
                    AND m.difficulty_level = 'introductory'
                    ORDER BY m.sequence_order DESC
                    LIMIT 1
                """, (course_id, current_module_id))
                basic_module = cursor.fetchone()
                if basic_module:
                    return basic_module

            # Return same module for retry
            cursor.execute("""
                SELECT module_id, title, difficulty_level
                FROM modules
                WHERE module_id = %s
            """, (current_module_id,))
            return cursor.fetchone()

        # Passed the exam - determine next module based on performance
        performance_threshold = 85  # High performance threshold
        if exam_result['score'] >= performance_threshold:
            # Check if can skip to a more advanced module
            cursor.execute("""
                SELECT m.module_id, m.title, m.difficulty_level
                FROM modules m
                WHERE m.course_id = %s 
                AND m.sequence_order > (
                    SELECT sequence_order FROM modules WHERE module_id = %s
                )
                AND m.difficulty_level >= %s
                ORDER BY m.sequence_order ASC
                LIMIT 1
            """, (course_id, current_module_id, exam_result['difficulty_level']))
        else:
            # Normal progression to next module
            cursor.execute("""
                SELECT m.module_id, m.title, m.difficulty_level
                FROM modules m
                WHERE m.course_id = %s 
                AND m.sequence_order = (
                    SELECT sequence_order + 1 
                    FROM modules 
                    WHERE module_id = %s
                )
            """, (course_id, current_module_id))

        next_module = cursor.fetchone()
        return next_module

    except Exception as e:
        print(f"Error determining next module: {str(e)}")
        return None
    finally:
        cursor.close()
        connection.close()

@app.route('/api/modules/<int:module_id>/next', methods=['GET'])
def get_next_module(module_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get course_id for the current module
        cursor.execute("SELECT course_id FROM modules WHERE module_id = %s", (module_id,))
        module_data = cursor.fetchone()
        
        if not module_data:
            return jsonify({"error": "Module not found"}), 404

        next_module = get_next_recommended_module(user_id, module_data['course_id'], module_id)
        
        if not next_module:
            return jsonify({
                "message": "Course completed",
                "is_complete": True
            })

        # Check if module is already unlocked
        cursor.execute("""
            SELECT status, mastery_score
            FROM user_modules
            WHERE user_id = %s AND module_id = %s
        """, (user_id, next_module['module_id']))
        module_status = cursor.fetchone()

        return jsonify({
            "next_module": {
                "module_id": next_module['module_id'],
                "title": next_module['title'],
                "difficulty_level": next_module['difficulty_level'],
                "status": module_status['status'] if module_status else "locked",
                "mastery_score": module_status['mastery_score'] if module_status else None
            }
        })

    except Exception as e:
        print(f"Error getting next module: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# Update the submit_module_test endpoint to use the new recommendation system
@app.route('/api/modules/<int:module_id>/submit-test', methods=['POST'])
def submit_module_test(module_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    user_id = session['user_id']
    connection = None
    cursor = None
    
    try:
        data = request.json
        answers = data.get('answers', {})
        total_questions = data.get('total_questions', 0)
        time_spent = data.get('time_spent_seconds', 0)

        if not answers or total_questions == 0:
            return jsonify({"error": "Invalid test submission"}), 400

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Verify module access
        cursor.execute("""
            SELECT status FROM user_modules 
            WHERE user_id = %s AND module_id = %s
        """, (user_id, module_id))
        module_status = cursor.fetchone()

        if not module_status or module_status['status'] == 'locked':
            return jsonify({"error": "Module access denied"}), 403

        # Calculate score and check if passed
        correct_answers = 0
        for question_id, user_answer in answers.items():
            cursor.execute("""
                SELECT correct_answer FROM questions 
                WHERE question_id = %s
            """, (question_id,))
            question = cursor.fetchone()
            if question and user_answer == question['correct_answer']:
                correct_answers += 1

        score = (correct_answers / total_questions) * 100
        passing_score = 70

        # Update user_modules with test results
        cursor.execute("""
            UPDATE user_modules 
            SET exam_score = %s,
                time_spent_minutes = time_spent_minutes + %s,
                status = %s,
                completion_date = NOW()
            WHERE user_id = %s AND module_id = %s
        """, (score, time_spent // 60, 'completed' if score >= passing_score else 'started', user_id, module_id))

        # If passed, unlock next module
        next_module = None
        if score >= passing_score:
            cursor.execute("""
                SELECT course_id, sequence_order 
                FROM modules 
                WHERE module_id = %s
            """, (module_id,))
            current_module = cursor.fetchone()

            cursor.execute("""
                SELECT module_id 
                FROM modules 
                WHERE course_id = %s AND sequence_order = %s
            """, (current_module['course_id'], current_module['sequence_order'] + 1))
            next_module = cursor.fetchone()

            if next_module:
                cursor.execute("""
                    INSERT INTO user_modules (user_id, module_id, status, start_date)
                    VALUES (%s, %s, 'not_started', NOW())
                    ON DUPLICATE KEY UPDATE status = 'not_started'
                """, (user_id, next_module['module_id']))

        connection.commit()

        return jsonify({
            "success": True,
            "score": score,
            "passed": score >= passing_score,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "next_module_unlocked": score >= passing_score and next_module is not None
        })

    except Exception as e:
        print(f"Error submitting test: {str(e)}")
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/courses/<int:course_id>/modules', methods=['GET'])
def get_course_modules(course_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    user_id = session['user_id']
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get all modules with their status for this user
        cursor.execute("""
            SELECT m.*, 
                   COALESCE(um.status, 'locked') as status,
                   um.mastery_score,
                   um.completion_date,
                   (
                       SELECT COUNT(*) 
                       FROM user_modules um2 
                       WHERE um2.user_id = %s 
                       AND um2.module_id < m.module_id 
                       AND um2.status != 'completed'
                   ) as incomplete_previous
            FROM modules m
            LEFT JOIN user_modules um ON m.module_id = um.module_id AND um.user_id = %s
            WHERE m.course_id = %s
            ORDER BY m.sequence_order
        """, (user_id, user_id, course_id))
        
        modules = cursor.fetchall()

        # If this is the first time accessing the course, unlock the first module
        if modules and (not modules[0]['status'] or modules[0]['status'] == 'locked'):
            cursor.execute("""
                INSERT INTO user_modules (user_id, module_id, status, start_date)
                VALUES (%s, %s, 'not_started', NOW())
                ON DUPLICATE KEY UPDATE status = 'not_started'
            """, (user_id, modules[0]['module_id']))
            connection.commit()
            modules[0]['status'] = 'not_started'

        return jsonify({
            "modules": modules,
            "course_id": course_id
        })

    except Exception as e:
        print(f"Error getting course modules: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/videos/<int:video_id>', methods=['GET'])
def get_video(video_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT v.*, m.title as module_title
            FROM videos v
            JOIN modules m ON v.module_id = m.module_id
            WHERE v.video_id = %s
        """, (video_id,))
        video = cursor.fetchone()

        if not video:
            return jsonify({"error": "Video not found"}), 404

        return jsonify(video)

    except Exception as e:
        print(f"Error getting video: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/videos/<int:video_id>/progress', methods=['GET', 'POST'])
def handle_video_progress(video_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        if request.method == 'GET':
            cursor.execute("""
                SELECT * FROM user_videos
                WHERE user_id = %s AND video_id = %s
            """, (user_id, video_id))
            progress = cursor.fetchone()
            return jsonify(progress or {"percent_watched": 0, "notes": "", "rating": 0})

        elif request.method == 'POST':
            data = request.json
            percent_watched = data.get('percent_watched', 0)
            notes = data.get('notes', '')

            # First, ensure the user_videos record exists
            cursor.execute("""
                INSERT INTO user_videos 
                (user_id, video_id, watch_date, percent_watched, notes)
                VALUES (%s, %s, NOW(), %s, %s)
                ON DUPLICATE KEY UPDATE 
                watch_date = NOW(),
                percent_watched = GREATEST(COALESCE(percent_watched, 0), %s),
                notes = %s
            """, (user_id, video_id, percent_watched, notes, percent_watched, notes))
            
            connection.commit()
            return jsonify({"success": True})

    except Exception as e:
        print(f"Error handling video progress: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/videos/<int:video_id>/rate', methods=['POST'])
def rate_video(video_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.json
        rating = data.get('rating')
        
        if not rating or not 1 <= rating <= 5:
            return jsonify({"error": "Invalid rating"}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE user_videos 
            SET rating = %s
            WHERE user_id = %s AND video_id = %s
        """, (rating, user_id, video_id))
        
        connection.commit()
        return jsonify({"success": True})

    except Exception as e:
        print(f"Error rating video: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/modules/<int:module_id>/next-video', methods=['GET'])
def get_next_video(module_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        current_video = request.args.get('current_video')
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get next video in sequence
        cursor.execute("""
            SELECT v.video_id, v.title, v.sequence_order
            FROM videos v
            WHERE v.module_id = %s AND v.sequence_order > (
                SELECT sequence_order FROM videos WHERE video_id = %s
            )
            ORDER BY v.sequence_order
            LIMIT 1
        """, (module_id, current_video))
        
        next_video = cursor.fetchone()
        return jsonify({"next_video": next_video})

    except Exception as e:
        print(f"Error getting next video: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/modules/save-recommendations', methods=['POST'])
def save_recommended_modules():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.json
        modules = data.get('modules', [])
        
        connection = get_db_connection()
        cursor = connection.cursor()

        for module in modules:
            cursor.execute("""
                INSERT INTO user_modules 
                (user_id, module_id, start_date, status)
                VALUES (%s, %s, NOW(), %s)
                ON DUPLICATE KEY UPDATE
                status = VALUES(status)
            """, (user_id, module['module_id'], module['status']))
        
        connection.commit()
        return jsonify({"success": True})

    except Exception as e:
        print(f"Error saving recommended modules: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/modules/start', methods=['POST'])
def start_user_module():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.json
        module_id = data.get('module_id')
        
        if not module_id:
            return jsonify({"error": "Module ID is required"}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        # Update module status to 'started'
        cursor.execute("""
            UPDATE user_modules 
            SET status = 'started',
                start_date = NOW()
            WHERE user_id = %s AND module_id = %s
        """, (user_id, module_id))
        
        connection.commit()
        return jsonify({"success": True})

    except Exception as e:
        print(f"Error starting module: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/modules/<int:module_id>/videos', methods=['GET'])
def get_module_videos(module_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT video_id, title, description, sequence_order
            FROM videos
            WHERE module_id = %s
            ORDER BY sequence_order
        """, (module_id,))
        
        videos = cursor.fetchall()
        return jsonify(videos)

    except Exception as e:
        print(f"Error getting module videos: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/modules/<int:module_id>/complete', methods=['POST'])
def complete_module(module_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.json
        mastery_score = data.get('mastery_score', 0)
        time_spent = data.get('time_spent_minutes', 0)
        
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE user_modules 
            SET status = 'completed',
                completion_date = NOW(),
                mastery_score = %s,
                time_spent_minutes = %s
            WHERE user_id = %s AND module_id = %s
        """, (mastery_score, time_spent, user_id, module_id))
        
        connection.commit()
        return jsonify({"success": True})

    except Exception as e:
        print(f"Error completing module: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/modules/<int:module_id>', methods=['GET'])
def get_module(module_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    user_id = session['user_id']
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # First, check if the user has access to this module
        cursor.execute("""
            SELECT m.*, um.status, um.mastery_score,
                   (SELECT COUNT(*) 
                    FROM user_modules um2 
                    WHERE um2.user_id = %s 
                    AND um2.module_id < %s 
                    AND um2.status != 'completed') as incomplete_previous
            FROM modules m
            LEFT JOIN user_modules um ON m.module_id = um.module_id AND um.user_id = %s
            WHERE m.module_id = %s
        """, (user_id, module_id, user_id, module_id))
        
        module = cursor.fetchone()
        if not module:
            return jsonify({"error": "Module not found"}), 404

        # If this is the first module, unlock it
        if module['sequence_order'] == 1:
            if not module['status'] or module['status'] == 'locked':
                cursor.execute("""
                    INSERT INTO user_modules (user_id, module_id, status, start_date)
                    VALUES (%s, %s, 'not_started', NOW())
                    ON DUPLICATE KEY UPDATE status = 'not_started'
                """, (user_id, module_id))
                connection.commit()
                module['status'] = 'not_started'
        # Otherwise, check if previous modules are completed
        elif module['incomplete_previous'] > 0:
            return jsonify({
                "error": "Module locked",
                "message": "You must complete all previous modules before accessing this one.",
                "status": "locked"
            }), 403

        # Get module progress
        cursor.execute("""
            SELECT COUNT(*) as total_videos,
                   SUM(CASE WHEN uv.percent_watched >= 90 THEN 1 ELSE 0 END) as completed_videos
            FROM videos v
            LEFT JOIN user_videos uv ON v.video_id = uv.video_id AND uv.user_id = %s
            WHERE v.module_id = %s
        """, (user_id, module_id))
        video_progress = cursor.fetchone()

        # Calculate completion percentage
        total_videos = video_progress['total_videos'] or 0
        completed_videos = video_progress['completed_videos'] or 0
        completion_percentage = (completed_videos / total_videos * 100) if total_videos > 0 else 0

        return jsonify({
            "module": module,
            "completion_percentage": completion_percentage,
            "can_take_test": completion_percentage >= 70,
            "is_accessible": module['status'] != 'locked'
        })

    except Exception as e:
        print(f"Error getting module: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/modules/<int:module_id>/unlock', methods=['POST'])
def unlock_next_module(module_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    user_id = session['user_id']
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get current module's course and sequence order
        cursor.execute("""
            SELECT course_id, sequence_order 
            FROM modules 
            WHERE module_id = %s
        """, (module_id,))
        current_module = cursor.fetchone()

        if not current_module:
            return jsonify({"error": "Module not found"}), 404

        # Get next module in sequence
        cursor.execute("""
            SELECT module_id 
            FROM modules 
            WHERE course_id = %s AND sequence_order = %s
        """, (current_module['course_id'], current_module['sequence_order'] + 1))
        next_module = cursor.fetchone()

        if next_module:
            # Unlock next module
            cursor.execute("""
                INSERT INTO user_modules (user_id, module_id, status, start_date)
                VALUES (%s, %s, 'not_started', NOW())
                ON DUPLICATE KEY UPDATE status = 'not_started'
            """, (user_id, next_module['module_id']))
            connection.commit()

            return jsonify({
                "success": True,
                "next_module_id": next_module['module_id']
            })
        else:
            return jsonify({
                "success": True,
                "message": "Course completed",
                "is_complete": True
            })

    except Exception as e:
        print(f"Error unlocking next module: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/modules/<int:module_id>/progress', methods=['GET'])
def get_module_progress(module_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    user_id = session['user_id']
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get total videos in module
        cursor.execute("""
            SELECT COUNT(*) as total_videos
            FROM videos
            WHERE module_id = %s
        """, (module_id,))
        video_count = cursor.fetchone()
        total_videos = video_count['total_videos'] or 0

        # Get completed videos (watched >= 90%)
        cursor.execute("""
            SELECT COUNT(*) as completed_videos
            FROM user_videos uv
            JOIN videos v ON uv.video_id = v.video_id
            WHERE v.module_id = %s AND uv.user_id = %s AND uv.percent_watched >= 90
        """, (module_id, user_id))
        completed = cursor.fetchone()
        completed_videos = completed['completed_videos'] or 0

        # Get exam attempts and scores
        cursor.execute("""
            SELECT exam_score as score, status, completion_date
            FROM user_modules
            WHERE module_id = %s AND user_id = %s
        """, (module_id, user_id))
        module_result = cursor.fetchone()

        # Calculate completion percentage
        video_weight = 0.7  # Videos are 70% of completion
        exam_weight = 0.3   # Exam is 30% of completion
        
        video_progress = (completed_videos / total_videos * 100) if total_videos > 0 else 0
        exam_progress = float(module_result['score']) if module_result and module_result['score'] else 0
        
        total_progress = (video_progress * video_weight) + (exam_progress * exam_weight)

        # Get video progress details
        cursor.execute("""
            SELECT v.video_id, v.title, v.description, v.sequence_order,
                   COALESCE(uv.percent_watched, 0) as percent_watched,
                   uv.watch_date
            FROM videos v
            LEFT JOIN user_videos uv ON v.video_id = uv.video_id AND uv.user_id = %s
            WHERE v.module_id = %s
            ORDER BY v.sequence_order
        """, (user_id, module_id))
        videos = cursor.fetchall()

        # Convert Decimal to float in video progress
        formatted_videos = []
        for video in videos:
            video_dict = dict(video)
            video_dict['percent_watched'] = float(video_dict['percent_watched']) if video_dict['percent_watched'] else 0
            formatted_videos.append(video_dict)

        return jsonify({
            "total_progress": round(total_progress, 2),
            "video_progress": round(video_progress, 2),
            "exam_progress": round(exam_progress, 2),
            "videos_completed": completed_videos,
            "total_videos": total_videos,
            "module_result": module_result,
            "videos": formatted_videos,
            "can_take_test": video_progress >= 70  # Can take test if watched 70% of videos
        })

    except Exception as e:
        print(f"Error getting module progress: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# ✅ Run Flask App
if __name__ == '__main__':
    app.run(debug=True)