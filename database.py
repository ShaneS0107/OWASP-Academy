
import sqlite3

DATABASE = "portal.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(lessons):
    connection = get_connection()
        # Add educational content columns to existing lessons table
    existing_columns = [
        column[1]
        for column in connection.execute(
            "PRAGMA table_info(lessons)"
        ).fetchall()
    ]

    new_columns = {
        "overview": "TEXT",
        "impact": "TEXT",
        "example": "TEXT",
        "prevention": "TEXT"
    }

    for column_name, column_type in new_columns.items():
        if column_name not in existing_columns:
            connection.execute(
                f"ALTER TABLE lessons ADD COLUMN {column_name} {column_type}"
            )

    # Create lessons table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY,
            code TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)

    # Create users table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    # Insert lessons
    # Insert or update lessons and educational content
    for lesson in lessons:
        connection.execute("""
            INSERT INTO lessons
            (id, code, title, description, overview, impact, example, prevention)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                code = excluded.code,
                title = excluded.title,
                description = excluded.description,
                overview = excluded.overview,
                impact = excluded.impact,
                example = excluded.example,
                prevention = excluded.prevention
        """, (
            lesson["id"],
            lesson["code"],
            lesson["title"],
            lesson["description"],
            lesson.get("overview", ""),
            lesson.get("impact", ""),
            lesson.get("example", ""),
            lesson.get("prevention", "")
        ))
    connection.commit()
    connection.close()


def get_all_lessons():
    connection = get_connection()

    lessons = connection.execute(
        "SELECT * FROM lessons ORDER BY id"
    ).fetchall()

    connection.close()
    return lessons


def get_lesson_by_id(lesson_id):
    connection = get_connection()

    lesson = connection.execute(
        "SELECT * FROM lessons WHERE id = ?",
        (lesson_id,)
    ).fetchone()

    connection.close()
    return lesson


# Register a new user
def create_user(name, email, password_hash):
    connection = get_connection()

    try:
        connection.execute("""
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
        """, (name, email, password_hash))

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


# Find a user by email
def get_user_by_email(email):
    connection = get_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    connection.close()
    return user
def create_users_table():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def create_user(name, email, password_hash):
    connection = get_connection()

    connection.execute("""
        INSERT INTO users (name, email, password_hash)
        VALUES (?, ?, ?)
    """, (name, email, password_hash))

    connection.commit()
    connection.close()


def get_user_by_email(email):
    connection = get_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    connection.close()
    return user

    
def mark_lesson_completed(user_id, lesson_id):
    connection = get_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS completed_lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                UNIQUE(user_id, lesson_id)
            )
        """)

        connection.execute("""
            INSERT OR IGNORE INTO completed_lessons
            (user_id, lesson_id)
            VALUES (?, ?)
        """, (user_id, lesson_id))

        connection.commit()

    finally:
        connection.close()

def get_completed_lesson_ids(user_id):
    connection = get_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS completed_lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                UNIQUE(user_id, lesson_id)
            )
        """)

        completed = connection.execute("""
            SELECT lesson_id FROM completed_lessons
            WHERE user_id = ?
        """, (user_id,)).fetchall()

        return [row["lesson_id"] for row in completed]

    finally:
        connection.close()
    # Save quiz score
def save_quiz_score(user_id, score):
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL
        )
    """)

    connection.execute("""
        INSERT INTO quiz_results (user_id, score)
        VALUES (?, ?)
    """, (user_id, score))

    connection.commit()
    connection.close()


# Get the latest quiz score
def get_quiz_score(user_id):
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL
        )
    """)

    result = connection.execute("""
        SELECT score FROM quiz_results
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,)).fetchone()

    connection.close()

    return result["score"] if result else 0
    # Get quiz attempt history
def get_quiz_history(user_id):
    connection = get_connection()

    history = connection.execute("""
        SELECT score FROM quiz_results
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,)).fetchall()

    connection.close()

    return history

    return result["score"] if result else 0


def get_user_by_id(user_id):
    connection = get_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    connection.close()
    return user    
