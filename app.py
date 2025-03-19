from flask import Flask, request, jsonify, session
import mysql.connector
from flask_cors import CORS
import os  # Use environment variables for security
from bcrypt import hashpw, gensalt # checkpw  # Import bcrypt for password hashing
from secret import secret_key


# app = Flask(__name__)
# CORS(app)
app = Flask(__name__)
app.secret_key = secret_key  # Required for session handling
CORS(app)  # Allow frontend to access the API

# ✅ Function to create a new DB connection for each request
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Change to os.getenv("DB_USER") for production security
        password="MYsql@123",  # Change to os.getenv("DB_PASS") for security
        database="user_registration"
    )

# ✅ API: Register a new student
@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        print("📌 Received Data:", data)  # Debugging line
        required_fields = ["name", "age", "gender", "class", "country", "state", "city", "parent_name", "parent_occupation", "financial_status", "username", "password"]
        
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        # Hash the password
        hashed_password = hashpw(data['password'].encode('utf-8'), gensalt()).decode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO users 
            (name, age, gender, class, country, state, city, parent_name, parent_occupation, financial_status, username, password_hash) 
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
        student_id = cursor.lastrowid  # Get the inserted student's ID

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

        query = "SELECT id, username FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session["user_id"] = user["id"]  # Store user ID in session
            session["username"] = user["username"]  # Store username in session
            print(f"✅ Logged in User: ID={user['id']}, Username={user['username']}")  

            return jsonify({"success": True, "message": "Login successful!", "user_id": user["id"]})
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

# Create /current_user Route to Get Logged-in User
@app.route('/current_user', methods=['GET'])
def get_current_user():
    if "user_id" in session:
        return jsonify({"logged_in": True, "user": {"id": session["user_id"], "name": session["username"]}})
    else:
        return jsonify({"logged_in": False, "error": "No active session"}), 401



# STORING RESULTS OF ASSESSMENT
@app.route('/store_results', methods=['POST'])
def store_results():
    try:
        data = request.json
        print("📌 Received Assessment Data:", data)  # Debugging

        # Check required fields
        if "user_id" not in data or "marks" not in data:
            return jsonify({"error": "Missing user_id or marks"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "INSERT INTO results (user_id, marks) VALUES (%s, %s)"
        values = (data["user_id"], data["marks"])

        print("Executing Query:", query)  # Debugging
        print("Values:", values)  # Debugging

        cursor.execute(query, values)
        conn.commit()
        result_id = cursor.lastrowid  # Get the inserted result ID

        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Assessment results stored!", "result_id": result_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

# ✅ API: Update Student Score
@app.route("/update_student_score", methods=["POST"])
def update_student_score():
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

# ✅ Redirect to Dashboard
@app.route("/redirect_dashboard", methods=["GET"])
def redirect_dashboard():
    try:
        return jsonify({"success": True, "message": "Redirecting to dashboard..."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ✅ Run Flask App
if __name__ == '__main__':
    app.run(debug=True)