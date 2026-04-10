from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Hello from Leash!</h1><p>Flask app deployed via Cloud Build + Cloud Run.</p>"

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "runtime": "python/flask"})

@app.route("/api/greet/<name>")
def greet(name):
    return jsonify({"message": f"Hello, {name}!", "from": "leash-flask-test"})
