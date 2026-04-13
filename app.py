import os
from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def get_db():
    return psycopg2.connect(os.environ["DATABASE_URL"], cursor_factory=RealDictCursor)

def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB init: {e}")

init_db()

@app.route("/")
def home():
    return jsonify({"app": "test-flask-app", "status": "running", "database": "postgresql"})

@app.route("/health")
def health():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return jsonify({"healthy": True, "database": "connected"})
    except Exception as e:
        return jsonify({"healthy": False, "database": str(e)}), 503

@app.route("/notes", methods=["GET"])
def list_notes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notes ORDER BY created_at DESC LIMIT 50")
    notes = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(notes)

@app.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO notes (title, content) VALUES (%s, %s) RETURNING *",
        (data["title"], data.get("content", ""))
    )
    note = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(dict(note)), 201
