🎓 AI-Powered Personalized Tutor System

Welcome to the **AI-Powered Personalized Tutor**, an intelligent, adaptive learning platform that transforms digital education through deeply personalized learning experiences.

🔗 **Repository:** [Personalized Tutor GitHub] (https://github.com/prasaduchukka/Personalized-tutor.git)

---
📚 Overview

The **AI-Powered Personal Tutor** is built to assess a student's prior knowledge and deliver content based on their proficiency level—offering **basic**, **intermediate**, or **advanced** modules.  

With **real-time performance tracking**, **AI-driven content recommendations**, and **voice + text doubt assistance**, this system ensures that every learner receives a tailored and engaging experience.

> Built for **local deployment**, this platform eliminates cloud dependencies, ensuring **privacy**, **speed**, and **offline availability**.

---

🚀 Features

- ✨ **User Authentication**  
  Secure login/signup for individualized learning access.

- 📘 **Pre-Assessment Evaluation**  
  Understands student knowledge levels before beginning the course.

- 🎯 **Adaptive Learning Path**  
  Automatically delivers suitable modules (basic/intermediate/advanced).

- 📊 **Real-Time Performance Tracking**  
  Continuously evaluates and adapts based on student progress.

- 🤖 **AI-Based Content Recommendation**  
  Recommends personalized content using machine learning.

- 🧠 **Interactive Doubt Assistance**  
  Ask questions via **text** or **voice** using the built-in AI assistant.

- 🧑‍🏫 **Voice + Text Tutor Interface**  
  Hands-free learning through speech or typing.

- 🖥️ **Local Deployment**  
  Runs securely on localhost without internet.

- 📝 **Notes Management System**  
  Take, save, and manage notes during lessons.

- ⭐ **Rating & Feedback System**  
  Rate modules and provide useful feedback.

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
