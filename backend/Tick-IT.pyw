"""Tick-IT desktop task manager."""
import importlib.util
import os
import sqlite3
import subprocess
import sys
import threading
import time
import traceback
import webbrowser
import tkinter.messagebox as messagebox


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(PROJECT_DIR, "backend", "tasks.db")


def ensure_flask():
    if importlib.util.find_spec("flask") is None:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "Flask"],
            check=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )


def connect_database():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialise_database():
    with connect_database() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                priority TEXT DEFAULT 'medium',
                due_date TEXT,
                category TEXT DEFAULT 'Personal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def get_tasks():
    with connect_database() as connection:
        rows = connection.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    return [dict(row) for row in rows]


def create_task(data):
    with connect_database() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (title, description, due_date, category)
            VALUES (?, ?, ?, ?)
            """,
            (
                data["title"],
                data.get("description", ""),
                data.get("due_date"),
                data.get("category", "Personal"),
            ),
        )
        return cursor.lastrowid


def update_task(task_id, data):
    allowed_fields = {"title", "description", "status", "priority", "due_date", "category"}
    changes = {field: value for field, value in data.items() if field in allowed_fields}
    if not changes:
        return False

    fields = ", ".join(f"{field} = ?" for field in changes)
    with connect_database() as connection:
        cursor = connection.execute(
            f"UPDATE tasks SET {fields} WHERE id = ?",
            [*changes.values(), task_id],
        )
        return cursor.rowcount > 0


def delete_task(task_id):
    with connect_database() as connection:
        cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0


def find_browser(name):
    locations = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        os.path.expandvars(r"%LocalAppData%"),
    ]
    vendors = {
        "brave.exe": "BraveSoftware",
        "chrome.exe": "Google",
        "msedge.exe": "Microsoft",
    }

    for location in locations:
        folder = os.path.join(location, vendors[name])
        if not os.path.exists(folder):
            continue
        for current_folder, _, files in os.walk(folder):
            if name in files:
                return os.path.join(current_folder, name)
    return None


def open_window():
    time.sleep(1)
    url = "http://127.0.0.1:5000"
    for browser_name in ("brave.exe", "chrome.exe", "msedge.exe"):
        browser = find_browser(browser_name)
        if browser:
            subprocess.Popen([browser, f"--app={url}"])
            return
    webbrowser.open(url)


def start_app():
    ensure_flask()
    from flask import Flask, jsonify, request

    initialise_database()
    app = Flask(__name__, static_folder=os.path.join(PROJECT_DIR, "frontend"), static_url_path="")

    @app.get("/")
    def index():
        return app.send_static_file("index.html")

    @app.route("/api/tasks", methods=["GET", "POST"])
    def tasks():
        if request.method == "GET":
            return jsonify(get_tasks())

        data = request.get_json(silent=True) or {}
        if not data.get("title"):
            return jsonify({"error": "Missing title"}), 400
        return jsonify({"id": create_task(data), "message": "Created"}), 201

    @app.route("/api/tasks/<int:task_id>", methods=["PUT", "DELETE"])
    def task(task_id):
        if request.method == "DELETE":
            if delete_task(task_id):
                return jsonify({"message": "Deleted"})
            return jsonify({"error": "Not found"}), 404

        data = request.get_json(silent=True) or {}
        if update_task(task_id, data):
            return jsonify({"message": "Updated"})
        return jsonify({"error": "Not found"}), 404

    threading.Thread(target=open_window, daemon=True).start()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    try:
        start_app()
    except Exception:
        messagebox.showerror("Tick-IT could not start", traceback.format_exc())
