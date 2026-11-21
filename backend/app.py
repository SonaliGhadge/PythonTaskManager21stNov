import sqlite3

from flask import Flask, jsonify, request
from flask_cors import CORS

from database import get_connection, init_db
from models import Task, validate_task_payload

app = Flask(__name__)
CORS(app)
init_db()


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


@app.get("/api/tasks")
def get_tasks():
    try:
        with get_connection() as connection:
            rows = connection.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
        tasks = [Task(**dict(row)).to_dict() for row in rows]
        return jsonify(tasks), 200
    except sqlite3.Error:
        app.logger.exception("Database error while retrieving tasks")
        return jsonify({"error": "Could not retrieve tasks"}), 500


@app.post("/api/tasks")
def create_task():
    payload = request.get_json(silent=True)
    try:
        payload = validate_task_payload(payload, creating=True)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    task = Task(
        title=payload["title"].strip(),
        description=payload.get("description", "").strip(),
        status="pending",
    )

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title, description, status, created_at) VALUES (?, ?, ?, ?)",
                (task.title, task.description, task.status, task.created_at),
            )
            task.id = cursor.lastrowid
        return jsonify(task.to_dict()), 201
    except sqlite3.Error:
        app.logger.exception("Database error while creating task")
        return jsonify({"error": "Could not create task"}), 500


@app.put("/api/tasks/<int:task_id>")
def update_task(task_id):
    payload = request.get_json(silent=True)
    try:
        payload = validate_task_payload(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        with get_connection() as connection:
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if row is None:
                return jsonify({"error": "Task not found"}), 404

            current = dict(row)
            updates = {
                "title": payload.get("title", current["title"]),
                "description": payload.get("description", current["description"]),
                "status": payload.get("status", current["status"]),
            }
            if isinstance(updates["title"], str):
                updates["title"] = updates["title"].strip()
            if isinstance(updates["description"], str):
                updates["description"] = updates["description"].strip()

            connection.execute(
                "UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ?",
                (updates["title"], updates["description"], updates["status"], task_id),
            )
            updated = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

        return jsonify(Task(**dict(updated)).to_dict()), 200
    except sqlite3.Error:
        app.logger.exception("Database error while updating task")
        return jsonify({"error": "Could not update task"}), 500


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    try:
        with get_connection() as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404
        return jsonify({"message": "Task deleted successfully"}), 200
    except sqlite3.Error:
        app.logger.exception("Database error while deleting task")
        return jsonify({"error": "Could not delete task"}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
