import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app import app
from database import get_connection, reset_db


@pytest.fixture(autouse=True)
def clean_database():
    reset_db()
    yield
    reset_db()


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    return app.test_client()


def test_create_task(client):
    response = client.post("/api/tasks", json={
        "title": "Prepare report",
        "description": "Compile the monthly metrics",
        "status": "pending",
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] > 0
    assert data["title"] == "Prepare report"
    assert data["status"] == "pending"


def test_retrieve_tasks(client):
    client.post("/api/tasks", json={"title": "Task one"})
    client.post("/api/tasks", json={"title": "Task two", "status": "completed"})

    response = client.get("/api/tasks")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert {task["title"] for task in data} == {"Task one", "Task two"}


def test_update_task(client):
    created = client.post("/api/tasks", json={"title": "Draft", "description": "First draft"})
    task_id = created.get_json()["id"]

    response = client.put(f"/api/tasks/{task_id}", json={
        "title": "Final draft",
        "description": "Reviewed draft",
        "status": "in_progress",
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Final draft"
    assert data["description"] == "Reviewed draft"
    assert data["status"] == "in_progress"


def test_delete_task(client):
    created = client.post("/api/tasks", json={"title": "Temporary task"})
    task_id = created.get_json()["id"]

    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200

    tasks = client.get("/api/tasks").get_json()
    assert all(task["id"] != task_id for task in tasks)


def test_create_preserves_requested_status(client):
    response = client.post("/api/tasks", json={
        "title": "Completed immediately",
        "status": "completed",
    })
    assert response.status_code == 201
    assert response.get_json()["status"] == "completed"


def test_title_length_limit(client):
    at_limit = client.post("/api/tasks", json={"title": "A" * 120})
    assert at_limit.status_code == 201

    over_limit = client.post("/api/tasks", json={"title": "A" * 121})
    assert over_limit.status_code == 400


def test_reset_db_recreates_tasks_table():
    reset_db()
    with get_connection() as connection:
        row = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'"
        ).fetchone()
    assert row is not None


def test_create_requires_title(client):
    response = client.post("/api/tasks", json={"description": "Missing title"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_rejects_invalid_status(client):
    response = client.post("/api/tasks", json={"title": "Bad status", "status": "unknown"})
    assert response.status_code == 400


def test_create_rejects_non_object_json(client):
    response = client.post("/api/tasks", json=["not", "an", "object"])
    assert response.status_code == 400


def test_update_missing_task(client):
    response = client.put("/api/tasks/9999", json={"status": "completed"})
    assert response.status_code == 404


def test_delete_missing_task(client):
    response = client.delete("/api/tasks/9999")
    assert response.status_code == 404
