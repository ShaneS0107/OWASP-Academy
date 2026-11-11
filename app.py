import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash


from database import (
    initialize_database,
    get_all_lessons,
    get_lesson_by_id,
    create_users_table,
    create_user,
    get_user_by_email,
    get_user_by_id,
    mark_lesson_completed,
    get_completed_lesson_ids,
    save_quiz_score,
    get_quiz_score,
    get_quiz_history
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
csrf = CSRFProtect(app)


# OWASP Top 10:2025 learning topics

lessons = [
       {
        "id": 1,
        "code": "A01:2025",
        "title": "Broken Access Control",
        "description": "Learn how attackers access information or functions they should not be allowed to use.",

        "overview": """
        Broken Access Control occurs when an application does not properly
        enforce restrictions on what authenticated users are allowed to access.
        Users may gain access to another person's information or perform
        actions beyond their assigned permissions.
        """,

        "impact": """
        This vulnerability can expose private information, allow unauthorized
        account changes, enable privilege escalation, and potentially let
        attackers take control of sensitive application functions.
        """,

        "example": """
        Imagine an online learning portal where users access their profiles
        through addresses such as /profile/101 and /profile/102.
        If User 101 can change the address to /profile/102 and view another
        user's private information without authorization, the application
        has a Broken Access Control vulnerability.
        """,

        "prevention": """
        Check authorization on the server for every protected request.
        Apply role-based permissions, deny access by default, verify that
        users can only access their own resources, and test access controls
        using accounts with different permission levels.
        """
    },
        {
        "id": 2,
        "code": "A02:2025",
        "title": "Security Misconfiguration",
        "description": "Understand security mistakes in application settings, servers and configurations.",

        "overview": """
        Security Misconfiguration happens when applications, servers,
        databases, or cloud services are configured insecurely.
        Examples include unnecessary services, default passwords,
        excessive permissions, and exposed administrative interfaces.
        """,

        "impact": """
        Poor configurations can expose sensitive information, allow
        unauthorized access, reveal internal system details, and give
        attackers opportunities to compromise an application.
        """,

        "example": """
        Imagine a website running in production with its debug mode enabled.
        An attacker triggers an application error and sees a detailed error
        page containing internal file paths and technical information.
        This information could help the attacker investigate further.
        """,

        "prevention": """
        Use secure default configurations, disable unnecessary services
        and debug features in production, remove default credentials,
        apply security updates, restrict administrative access, and
        regularly review server and application settings.
        """
    },
       {
        "id": 3,
        "code": "A03:2025",
        "title": "Software Supply Chain Failures",
        "description": "Learn about risks involving software dependencies, build systems and distribution.",

        "overview": """
        Software Supply Chain Failures occur when weaknesses in the
        components, tools, development processes, or distribution systems
        used to build software introduce security risks.
        Applications often depend on third-party libraries and packages,
        which can contain vulnerabilities or malicious code.
        """,

        "impact": """
        Compromised dependencies or build systems can introduce malicious
        code, expose sensitive information, disrupt services, and affect
        many applications that rely on the same software component.
        """,

        "example": """
        Imagine a developer installs a third-party package for their
        application. The package has been compromised and contains
        malicious code. When the application uses that package,
        the malicious code may execute as part of the application.
        """,

        "prevention": """
        Use trusted package sources, regularly update dependencies,
        monitor known vulnerabilities, verify package integrity,
        review third-party components, and protect build and deployment
        systems with strong access controls.
        """
    },
        {
        "id": 4,
        "code": "A04:2025",
        "title": "Cryptographic Failures",
        "description": "Understand weaknesses in encryption and protection of sensitive information.",

        "overview": """
        Cryptographic Failures occur when sensitive information is not
        properly protected through encryption or other security controls.
        Weak encryption, poor key management, and insecure data transmission
        can expose confidential information.
        """,

        "impact": """
        Attackers may obtain passwords, financial information, personal
        details, or other confidential data. Exposed information can lead
        to identity theft, account compromise, and privacy violations.
        """,

        "example": """
        Imagine an application transmitting login credentials over an
        unencrypted HTTP connection. Someone monitoring the network may
        be able to read the transmitted information.
        """,

        "prevention": """
        Use HTTPS with modern TLS configurations, choose strong and
        well-maintained cryptographic algorithms, securely manage
        encryption keys, protect sensitive stored data, and avoid
        storing passwords in plain text. Use secure password hashing
        algorithms such as Argon2 or bcrypt.
        """
    },
        {
        "id": 5,
        "code": "A05:2025",
        "title": "Injection",
        "description": "Learn how untrusted input can cause unintended commands or queries to execute.",

        "overview": """
        Injection vulnerabilities occur when an application sends
        untrusted input to an interpreter without handling it safely.
        Examples include SQL injection, command injection, and
        cross-site scripting.
        """,

        "impact": """
        Attackers may access unauthorized data, modify database records,
        execute unintended commands, bypass authentication, or affect
        the availability and integrity of an application.
        """,

        "example": """
        Imagine a login form that directly combines user input with
        an SQL query. If the application does not use parameterized
        queries, specially crafted input could change the meaning
        of the database query.
        """,

        "prevention": """
        Use parameterized queries and prepared statements, validate
        input on the server, apply context-aware output encoding,
        avoid constructing commands from untrusted input, and
        follow secure coding practices.
        """
    },
        {
        "id": 6,
        "code": "A06:2025",
        "title": "Insecure Design",
        "description": "Understand security weaknesses caused by missing or ineffective security design.",

        "overview": """
        Insecure Design refers to security weaknesses introduced
        during the planning and design of an application.
        These problems occur when security requirements, threat
        scenarios, and protective controls are not properly considered
        before development begins.
        """,

        "impact": """
        Poor security design can allow attackers to abuse application
        workflows, bypass important business rules, manipulate transactions,
        or exploit weaknesses that cannot easily be fixed through
        ordinary code changes.
        """,

        "example": """
        Imagine an online shopping application that allows customers
        to purchase products without checking whether the requested
        quantity is within permitted limits. An attacker could manipulate
        the purchase process and abuse the application's business rules.
        """,

        "prevention": """
        Include security requirements during the design stage,
        perform threat modeling, identify abuse cases, establish
        secure design patterns, apply defense in depth, and
        review important business workflows before deployment.
        """
    },
        {
        "id": 7,
        "code": "A07:2025",
        "title": "Authentication Failures",
        "description": "Learn how weak authentication can allow unauthorized access to accounts.",

        "overview": """
        Authentication Failures occur when an application does not
        properly verify the identity of users. Weak passwords,
        poorly implemented login systems, insecure session handling,
        and missing protection against automated login attempts
        can create security risks.
        """,

        "impact": """
        Attackers may gain unauthorized access to user accounts,
        steal personal information, impersonate legitimate users,
        or access sensitive application features.
        """,

        "example": """
        Imagine a website that allows unlimited login attempts.
        An attacker could repeatedly try commonly used passwords
        against an account. Without appropriate protections,
        the account may eventually be compromised.
        """,

        "prevention": """
        Enforce strong password policies, use multi-factor authentication,
        implement rate limiting and login attempt monitoring,
        use secure session management, and store passwords using
        strong password hashing algorithms.
        """
    },
        {
        "id": 8,
        "code": "A08:2025",
        "title": "Software or Data Integrity Failures",
        "description": "Understand risks caused by failing to verify software and data integrity.",

        "overview": """
        Software or Data Integrity Failures occur when applications
        do not properly verify the trustworthiness and authenticity
        of software, updates, plugins, or important data.
        This can allow unauthorized modifications to go unnoticed.
        """,

        "impact": """
        Attackers may introduce malicious code, modify important
        application data, compromise software updates, or interfere
        with application functionality and reliability.
        """,

        "example": """
        Imagine an application downloading software updates without
        verifying their digital signatures. An attacker who manages
        to interfere with the update process could potentially
        distribute a modified and malicious update.
        """,

        "prevention": """
        Verify digital signatures and software package integrity,
        use trusted update sources, protect software build pipelines,
        validate important data, and restrict unauthorized changes
        to critical application files.
        """
    },
        {
        "id": 9,
        "code": "A09:2025",
        "title": "Security Logging and Alerting Failures",
        "description": "Learn why security events must be properly recorded and monitored with alerts.",

        "overview": """
        Security Logging and Alerting Failures occur when applications
        do not adequately record important security events or generate
        alerts when suspicious activities take place.
        Without proper monitoring, security incidents may remain
        undetected for long periods.
        """,

        "impact": """
        Attackers may operate inside compromised applications without
        being detected. Organizations may struggle to investigate
        incidents, identify affected accounts, and respond quickly
        to security threats.
        """,

        "example": """
        Imagine a website experiencing hundreds of failed login
        attempts against different user accounts. If the application
        does not record these attempts or alert administrators,
        a password-guessing attack may go unnoticed.
        """,

        "prevention": """
        Record important security events, monitor authentication
        failures and suspicious activities, configure meaningful
        alerts, protect log files from unauthorized modification,
        and regularly review security logs.
        """
    },
        {
        "id": 10,
        "code": "A10:2025",
        "title": "Mishandling of Exceptional Conditions",
        "description": "Understand security problems caused by improper error handling and unexpected conditions.",

        "overview": """
        Mishandling of Exceptional Conditions occurs when applications
        do not safely handle unexpected situations such as invalid input,
        unavailable services, failed operations, or resource limitations.
        Poor error handling can expose internal details or leave an
        application in an unsafe state.
        """,

        "impact": """
        Attackers may exploit unexpected application behavior to cause
        service interruptions, bypass security checks, expose sensitive
        technical information, or trigger unintended operations.
        """,

        "example": """
        Imagine an application that displays detailed database error
        messages to users whenever a database operation fails.
        These messages might reveal internal table names, file paths,
        or other implementation details that attackers could use
        to investigate the application.
        """,

        "prevention": """
        Handle exceptions safely, validate input, fail securely,
        display generic error messages to users, record technical
        details securely in server logs, and test applications
        under unexpected and failure conditions.
        """
    },
]


# Initialize database
initialize_database(lessons)
create_users_table()


# Homepage
@app.route("/")
def home():
    return render_template("index.html")


# Lessons page
@app.route("/lessons")
def show_lessons():
    all_lessons = get_all_lessons()
    return render_template("lessons.html", lessons=all_lessons)


# Individual lesson page
@app.route("/lessons/<int:lesson_id>")
def lesson_detail(lesson_id):

    lesson = get_lesson_by_id(lesson_id)

    if lesson is None:
        return "Lesson not found", 404

    return render_template("lesson_detail.html", lesson=lesson)


# Complete lesson
@app.route("/complete_lesson/<int:lesson_id>", methods=["POST"])
def complete_lesson(lesson_id):

    if "user_id" not in session:
        flash("Please log in to complete lessons.")
        return redirect(url_for("login"))

    lesson = get_lesson_by_id(lesson_id)

    if lesson is None:
        return "Lesson not found", 404

    mark_lesson_completed(session["user_id"], lesson_id)

    flash("Lesson marked as completed!")

    return redirect(url_for("show_lessons"))


# Registration page
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in all fields.")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.")
            return redirect(url_for("register"))

        existing_user = get_user_by_email(email)

        if existing_user:
            flash("This email is already registered.")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        create_user(name, email, password_hash)

        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = get_user_by_email(email)

        if user and check_password_hash(user["password_hash"], password):
            session.clear()

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            flash("Login successful!")
            return redirect(url_for("home"))

        flash("Invalid email or password.")

    return render_template("login.html")


# Logout

@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    flash("You have been logged out.")

    return redirect(url_for("home"))


# Dashboard
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        flash("Please log in to access your dashboard.")
        return redirect(url_for("login"))

    total_lessons = len(get_all_lessons())

    completed_ids = get_completed_lesson_ids(session["user_id"])
    completed_lessons = len(completed_ids)

    quiz_score = get_quiz_score(session["user_id"])
    quiz_history = get_quiz_history(session["user_id"])

    certificate_eligible = (
        completed_lessons == total_lessons
        and quiz_score is not None
        and quiz_score >= 70
    )

    if total_lessons > 0:
        progress = round((completed_lessons / total_lessons) * 100)
    else:
        progress = 0

    return render_template(
        "dashboard.html",
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        quiz_score=quiz_score,
        quiz_history=quiz_history,
        progress=progress,
        certificate_eligible=certificate_eligible
    )


@app.route("/certificate")
def certificate():

    if "user_id" not in session:
        flash("Please log in to access your certificate.")
        return redirect(url_for("login"))

    completed_ids = get_completed_lesson_ids(session["user_id"])
    total_lessons = len(get_all_lessons())
    completed_lessons = len(completed_ids)

    quiz_score = get_quiz_score(session["user_id"])

    if (
        completed_lessons != total_lessons
        or quiz_score is None
        or quiz_score < 70
    ):
        flash("Complete all lessons and score at least 70% to earn your certificate.")
        return redirect(url_for("dashboard"))

    user = get_user_by_id(session["user_id"])

    return render_template(
        "certificate.html",
        user_name=user["name"],
        quiz_score=quiz_score,
        completion_date=__import__("datetime").date.today().strftime("%d %B %Y")
    )    
def certificate():

    if "user_id" not in session:
        flash("Please log in to access your certificate.")
        return redirect(url_for("login"))

    completed_ids = get_completed_lesson_ids(session["user_id"])
    total_lessons = len(get_all_lessons())
    completed_lessons = len(completed_ids)

    quiz_score = get_quiz_score(session["user_id"])

    if (
        completed_lessons != total_lessons
        or quiz_score is None
        or quiz_score < 70
    ):
        flash("Complete all lessons and score at least 70% to earn your certificate.")
        return redirect(url_for("dashboard"))

    user = get_user_by_id(session["user_id"])

    return render_template(
        "certificate.html",
        user_name=user["name"],
        quiz_score=quiz_score,
        completion_date=__import__("datetime").date.today().strftime("%d %B %Y")
    )

# Quiz page


@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    # Check whether the user is logged in
    if "user_id" not in session:
        flash("Please log in to take the quiz.")
        return redirect(url_for("login"))

    if request.method == "POST":

        # Correct answers
        answers = {
            "q1": "a",
            "q2": "b",
            "q3": "c"
        }

        # Quiz questions and options
        questions = {
            "q1": {
                "question": "What does OWASP stand for?",
                "options": {
                    "a": "Open Web Application Security Project",
                    "b": "Online Website Application Safety Program",
                    "c": "Open World Application Software Platform"
                },
                "explanation": "OWASP originally stood for Open Web Application Security Project. Today, it is known as the Open Worldwide Application Security Project."
            },
            "q2": {
                "question": "What is SQL Injection?",
                "options": {
                    "a": "A method of improving database speed",
                    "b": "An attack that inserts malicious SQL commands",
                    "c": "A way to encrypt passwords"
                },
                "explanation": "SQL Injection is a vulnerability where attackers insert malicious SQL commands into application inputs to manipulate database queries."
            },
            "q3": {
                "question": "Which practice helps protect user passwords?",
                "options": {
                    "a": "Store passwords as plain text",
                    "b": "Share passwords with administrators",
                    "c": "Use secure password hashing"
                },
                "explanation": "Secure password hashing converts passwords into protected hash values. Dedicated algorithms such as Argon2id and bcrypt help protect stored passwords."
            }
        }

        score = 0
        results = []

        # Check submitted answers
        for question_id, correct_answer in answers.items():

            selected_answer = request.form.get(question_id, "")

            # Validate the submitted answer
            if selected_answer not in questions[question_id]["options"]:
                selected_answer = None

            is_correct = selected_answer == correct_answer

            if is_correct:
                score += 1

            results.append({
                "question": questions[question_id]["question"],
                "selected": questions[question_id]["options"].get(
                    selected_answer, "Not answered"
                ),
                "correct": questions[question_id]["options"][correct_answer],
                "is_correct": is_correct,
                "explanation": questions[question_id]["explanation"]
            })

        # Calculate quiz percentage
        quiz_score = round((score / len(answers)) * 100)

        # Save the score for the logged-in user
        save_quiz_score(session["user_id"], quiz_score)

        # Display quiz results
        return render_template(
            "quiz_results.html",
            score=score,
            total=len(answers),
            quiz_score=quiz_score,
            results=results
        )

    return render_template("quiz.html")





        

# Run application
if __name__ == "__main__":
    print("REGISTERED ROUTES:")
    print(app.url_map)

    app.run(debug=False)
