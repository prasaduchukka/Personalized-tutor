🎓 AI-Powered Personalized Tutor System

Welcome to the **AI-Powered Personalized Tutor**, an intelligent, adaptive learning platform that transforms digital education through deeply personalized learning experiences.

🔗 **Repository:** [Personalized Tutor GitHub] (https://github.com/prasaduchukka/Personalized-tutor.git)
 Demo vedio link: https://drive.google.com/file/d/17GCW8yOe-NWqseg6QjPLr0Dydi2c411b/view?usp=sharing

---
📚 Overview

The **AI-Powered Personal Tutor** is built to assess a student's prior knowledge and deliver content based on their proficiency level—offering **basic**, **intermediate**, or **advanced** modules.  

With **real-time performance tracking**, **AI-driven content recommendations**, and **voice + text doubt assistance**, this system ensures that every learner receives a tailored and engaging experience.

> Built for **local deployment**, this platform eliminates cloud dependencies, ensuring **privacy**, **speed**, and **offline availability**.

---

🚀 Features
![Screenshot 2025-04-06 005803](https://github.com/user-attachments/assets/c6b943c1-c5e5-4163-9b0b-6cc91ee124dc)

- ✨ **User Authentication**  
  Secure login/signup for individualized learning access.
![image](https://github.com/user-attachments/assets/699424e2-7279-4a52-9077-5103eb3634c3)

- 📘 **Pre-Assessment Evaluation**  
  Understands student knowledge levels before beginning the course.
![image](https://github.com/user-attachments/assets/0e441479-c2d6-4788-87be-058c8eda13ae)

- 🎯 **Adaptive Learning Path**  
  Automatically delivers suitable modules (basic/intermediate/advanced).
![image](https://github.com/user-attachments/assets/428eb4dd-f9ae-4344-beb2-631125017e95)

- 📊 **Real-Time Performance Tracking**  
  Continuously evaluates and adapts based on student progress.
![image](https://github.com/user-attachments/assets/c51b4510-f008-46d1-8e98-9d59f7d94fda)

- 🤖 **AI-Based Content Recommendation**  
  Recommends personalized content using machine learning.

- 🧠 **Interactive Doubt Assistance**  
  Ask questions via **text** or **voice** using the built-in AI assistant.

- 🧑‍🏫 **Voice + Text Tutor Interface**  
  Hands-free learning through speech or typing.
![Screenshot 2025-04-06 004629](https://github.com/user-attachments/assets/73c7bedf-3c78-480e-9958-61544ea664eb)

- 📝 **Notes Management System**  
  Take, save, and manage notes during lessons.

- ⭐ **Rating & Feedback System**  
  Rate modules and provide useful feedback.
![image](https://github.com/user-attachments/assets/d18c57f6-3df1-4a40-9129-245583ab0aac)

- 📈 **Student Engagement Metrics**  
  Monitors and reports student engagement and behavior.

- 🎓 **Module-Wise Promotions**  
  Auto-promotes students based on assessment performance.



🛠️ Tech Stack

### 🧠 Backend (Server-Side)
- **Python** – Core backend logic
- **Flask** – Web server and routing
- **MySQL** – Persistent user and performance data
- **SQLite** – Lightweight local session handling
- **Flask-CORS** – Secure cross-origin communication
- **SQLAlchemy** – ORM for DB operations
- **bcrypt** – Password hashing and authentication
- **dotenv** – Secure environment variable management

### 🤖 AI & Machine Learning
- **OpenAI API** – Smart NLP-powered doubt assistance
- **HuggingFace (HugChat)** – Conversational AI
- **scikit-learn** – Recommendation engine (Nearest Neighbors)
- **Custom Recommendation Engine** – Personalized content suggestion

### 🔊 Speech & Audio Interaction
- **pyttsx3** – Text-to-speech voice tutor
- **SpeechRecognition** – Converts speech input to text
- **PyWhatKit** – Plays YouTube videos, does web searches via voice

### 🌐 Frontend (Client-Side)
- **HTML5, CSS3** – UI structure and design
- **JavaScript** – Interface logic and interactivity
- **jQuery** – DOM manipulation
- **Textillate.js** – Dynamic text animations

### 📦 Other Utilities
- **webbrowser module** – Opens external resources
- **Flask Session** – For user session management
- **secret.py** – Custom session key manager

---

## 🖥️ Local Installation

Follow these steps to run the project locally:

```bash
# Clone the repository
git clone https://github.com/prasaduchukka/Personalized-tutor.git

# Navigate to the project directory
cd Personalized-tutor

# (Optional but recommended) Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Run the application
python app.py --> start index.html
