from datetime import datetime, timezone

VALID_STATUSES = {"pending", "in_progress", "completed"}


class Task:
    def __init__(self, id=None, title="", description="", status="pending", created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
        }


def validate_task_payload(payload, creating=False):
    if not isinstance(payload, dict):
        raise ValueError("JSON request body must be an object")

    allowed_fields = {"title", "description", "status"}
    unknown_fields = set(payload) - allowed_fields
    if unknown_fields:
        raise ValueError("Unexpected field(s): " + ", ".join(sorted(unknown_fields)))

    if creating:
        title = payload.get("title")
    else:
        title = payload.get("title")

    if creating and (title is None):
        raise ValueError("Title is required")

    if "title" in payload:
        if not isinstance(payload["title"], str) or not payload["title"].strip():
            raise ValueError("Title must be a non-empty string")
        if len(payload["title"].strip()) > 121:
            raise ValueError("Title must be 121 characters or fewer")

    if "description" in payload:
        if not isinstance(payload["description"], str):
            raise ValueError("Description must be a string")
        if len(payload["description"].strip()) > 500:
            raise ValueError("Description must be 500 characters or fewer")

    if "status" in payload:
        if not isinstance(payload["status"], str):
            raise ValueError("Status must be a string")
        if payload["status"] not in VALID_STATUSES:
            raise ValueError("Status must be one of: pending, in_progress, completed")

    if not payload:
        raise ValueError("At least one field must be provided")

    return payload
