import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "tasks.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(database_path=None):
    path = Path(database_path) if database_path else DATABASE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL
            )
            """
        )


def reset_db(database_path=None):
    path = Path(database_path) if database_path else DATABASE_PATH
    with sqlite3.connect(path) as connection:
        connection.execute("DROP TABLE IF EXISTS tasks")
