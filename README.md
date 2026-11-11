# OWASP Academy – OWASP Top 10 Learning Portal

## Project Overview
OWASP Academy is a web-based cybersecurity learning portal designed to help users understand the OWASP Top 10 security risks through educational lessons and interactive quizzes.

## Technologies Used
- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Flask-WTF

## Features
- User registration and login
- Secure password hashing
- OWASP Top 10 educational lessons
- Individual lesson detail pages
- Lesson completion tracking
- Interactive cybersecurity quizzes
- Automatic quiz scoring
- Quiz results and attempt history
- User dashboard and learning progress
- Certificate of Completion
- CSRF protection
- Session-based authentication

## Certificate Eligibility
Users must:
1. Complete all 10 lessons.
2. Achieve at least 70% in the quiz.

## Installation and Setup

1. Clone or download the project.
2. Open the project folder in VS Code.
3. Create a virtual environment:

   `python -m venv venv`

4. Activate the virtual environment on Windows:

   `.\venv\Scripts\Activate.ps1`

5. Install dependencies:

   `pip install -r requirements.txt`

6. Run the application:

   `python app.py`

7. Open your browser and visit:

   `http://127.0.0.1:5000`

## Database
The project uses SQLite to store user accounts, lessons, completion records and quiz results.

## Project Purpose
This project aims to improve cybersecurity awareness by providing an interactive learning environment based on the OWASP Top 10.

## Security
- Passwords are stored using secure password hashing.
- CSRF protection is enabled.
- Login-protected routes use session authentication.
- The Flask secret key is configured using an environment variable.
