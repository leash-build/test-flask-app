import os
from flask import Flask, jsonify, request
import psycopg
from psycopg.rows import dict_row

app = Flask(__name__)

def get_db():
    return psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)

def init_db():
    try:
        conn = get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
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
        conn.execute("SELECT 1")
        conn.close()
        return jsonify({"healthy": True, "database": "connected"})
    except Exception as e:
        return jsonify({"healthy": False, "database": str(e)}), 503

@app.route("/notes", methods=["GET"])
def list_notes():
    conn = get_db()
    notes = conn.execute("SELECT * FROM notes ORDER BY created_at DESC LIMIT 50").fetchall()
    conn.close()
    return jsonify(notes)

@app.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400
    conn = get_db()
    note = conn.execute(
        "INSERT INTO notes (title, content) VALUES (%s, %s) RETURNING *",
        (data["title"], data.get("content", ""))
    ).fetchone()
    conn.commit()
    conn.close()
    return jsonify(dict(note)), 201
