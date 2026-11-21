# TaskFlow — Python Task Management Web Application

TaskFlow is a responsive full-stack task management dashboard built with Flask, SQLite, HTML, CSS, and vanilla JavaScript.

## Architecture

```text
python-task-manager/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── models.py
│   └── requirements.txt
├── tests/
│   └── test_api.py
├── README.md
└── .gitignore
```

- `app.py` defines Flask routes and HTTP behavior.
- `database.py` owns SQLite connection and schema setup.
- `models.py` defines the task representation and payload validation.
- `frontend/app.js` communicates with the REST API.

## Prerequisites

- Python 3.10 or newer
- A modern browser

## Installation

Open a terminal in the project directory:

```powershell
cd python-task-manager
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

On macOS/Linux, activate the environment with `source .venv/bin/activate`.

## Start the Backend

From `python-task-manager`:

```powershell
cd backend
python app.py
```

The API runs at `http://127.0.0.1:5000`. SQLite creates `backend/tasks.db` automatically.

## Launch the Frontend

Because the frontend and backend are separate, open `frontend/index.html` directly in a browser. Alternatively, serve it with a simple static server:

```powershell
cd python-task-manager
python -m http.server 5500 --directory frontend
```

Then visit `http://127.0.0.1:5500`.

## API Endpoints

| Method | Endpoint | Description | Success status |
|---|---|---|---|
| GET | `/api/tasks` | Retrieve all tasks, newest first | 200 |
| POST | `/api/tasks` | Create a task | 201 |
| PUT | `/api/tasks/<id>` | Update one or more task fields | 200 |
| DELETE | `/api/tasks/<id>` | Delete a task | 200 |

Valid statuses: `pending`, `in_progress`, `completed`.

Create example:

```json
{
  "title": "Prepare presentation",
  "description": "Add final project metrics",
  "status": "pending"
}
```

Update example:

```json
{
  "status": "completed"
}
```

Invalid payloads return `400`; unknown task IDs return `404`.

## Run Tests

From `python-task-manager`:

```powershell
.venv\Scripts\Activate.ps1
python -m pytest tests/test_api.py -v
```

The test fixture resets the SQLite table before and after every test.
