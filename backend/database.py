
import sqlite3
import json

DATABASE = "resume.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            linkedin TEXT,
            github TEXT,
            summary TEXT,
            education TEXT,
            skills TEXT,
            projects TEXT,
            experience TEXT,
            certifications TEXT,
            achievements TEXT,
            languages TEXT,
            selected_sections TEXT DEFAULT '[]',
            custom_sections TEXT DEFAULT '[]'
        )
    """)

    columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(resumes)").fetchall()
    }

    if "selected_sections" not in columns:
        conn.execute("""
            ALTER TABLE resumes
            ADD COLUMN selected_sections TEXT DEFAULT '[]'
        """)

    if "custom_sections" not in columns:
        conn.execute("""
            ALTER TABLE resumes
            ADD COLUMN custom_sections TEXT DEFAULT '[]'
        """)

    conn.commit()
    conn.close()


def save_resume(data):
    conn = get_connection()

    cursor = conn.execute("""
        INSERT INTO resumes (
            name, email, phone, address, linkedin, github,
            summary, education, skills, projects, experience,
            certifications, achievements, languages,
            selected_sections, custom_sections
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name", ""),
        data.get("email", ""),
        data.get("phone", ""),
        data.get("address", ""),
        data.get("linkedin", ""),
        data.get("github", ""),
        data.get("summary", ""),
        data.get("education", ""),
        data.get("skills", ""),
        data.get("projects", ""),
        data.get("experience", ""),
        data.get("certifications", ""),
        data.get("achievements", ""),
        data.get("languages", ""),
        json.dumps(data.get("selected_sections", [])),
        json.dumps(data.get("custom_sections", []))
    ))

    resume_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return resume_id


def get_resume(resume_id):
    conn = get_connection()

    row = conn.execute(
        "SELECT * FROM resumes WHERE id = ?",
        (resume_id,)
    ).fetchone()

    conn.close()

    if row is None:
        return None

    resume = dict(row)

    for field in ("selected_sections", "custom_sections"):
        try:
            resume[field] = json.loads(resume.get(field) or "[]")
        except (json.JSONDecodeError, TypeError):
            resume[field] = []

    return resume
