# Bug Report

## Prioritized Bugs

| Bug ID | File Path | Error Type | Description | Priority |
|---|---|---|---|---|
| BUG-1 | `frontend/app.js` | Syntax | Missing closing parenthesis prevents the entire JavaScript file from executing. | Critical |
| BUG-2 | `frontend/app.js` | API / Integration | The API base URL uses `/api/task` instead of the backend's `/api/tasks` endpoint. | Critical |
| BUG-3 | `backend/app.py` | Logical | Task creation ignores a valid supplied status and always stores `pending`. | High |
| BUG-4 | `backend/database.py` | Database | `reset_db()` drops the table but does not recreate it. | High |
| BUG-5 | `backend/models.py` | Validation / Logical | Title validation accepts 121 characters, despite the application limit being 120. | Medium |
| BUG-6 | `frontend/app.js` | Runtime / Rendering | Task titles may be unsafe when interpolated into an HTML attribute. | Medium |
| BUG-7 | `tests/test_api.py` | Test Coverage | Tests do not verify title length boundaries or creation with non-default statuses. | Medium |

## Detailed Findings

### BUG-1 — JavaScript syntax error

- **Location:** `frontend/app.js:80`
- **Function:** `showFormButton` click-handler setup
- **Error category:** Syntax
- **Explanation:** The `addEventListener` call is missing a closing parenthesis:
  `document.getElementById("showFormButton").addEventListener("click", openForm;`
- **Expected application behavior:** Clicking “New task” should open the form.
- **Actual behavior:** The JavaScript parser rejects the script, preventing initial task loading and all frontend interactions.
- **Recommended correction:** Restore the closing parenthesis: `addEventListener("click", openForm);`

### BUG-2 — Incorrect frontend API endpoint

- **Location:** `frontend/app.js:1`
- **Function:** `API_URL`
- **Error category:** API / Integration
- **Explanation:** The frontend sends requests to `/api/task`, while all backend routes use `/api/tasks`.
- **Expected application behavior:** Frontend actions should call `/api/tasks`.
- **Actual behavior:** Loading, creating, updating, and deleting tasks receive 404 responses.
- **Recommended correction:** Change `API_URL` to `http://127.0.0.1:5000/api/tasks`.

### BUG-3 — Requested task status is ignored

- **Location:** `backend/app.py:44-48`
- **Function:** `create_task()`
- **Error category:** Logical
- **Explanation:** Although validation accepts `pending`, `in_progress`, and `completed`, creation constructs the `Task` with `status="pending"` and ignores `payload["status"]`.
- **Expected application behavior:** A task created with `status="completed"` should be stored and returned as completed.
- **Actual behavior:** Every newly created task is stored as pending.
- **Recommended correction:** Use `status=payload.get("status", "pending")`.

### BUG-4 — Reset operation leaves database unusable

- **Location:** `backend/database.py:30-34`
- **Function:** `reset_db()`
- **Error category:** Database
- **Explanation:** The function executes `DROP TABLE IF EXISTS tasks` but no longer calls `init_db(path)` afterward.
- **Expected application behavior:** Resetting should recreate an empty tasks table.
- **Actual behavior:** Database operations raise `no such table: tasks` after reset. This can also cause the API test fixture to leave every test database unusable.
- **Recommended correction:** Recreate the schema after dropping the table by calling `init_db(path)`.

### BUG-5 — Title length boundary is incorrect

- **Location:** `backend/models.py:42-45`
- **Function:** `validate_task_payload()`
- **Error category:** Validation / Logical
- **Explanation:** The check rejects titles longer than 121 characters, so a 121-character title is accepted. The frontend and documented API limit specify 120 characters.
- **Expected application behavior:** Titles of 121 or more characters should be rejected.
- **Actual behavior:** 121-character titles pass backend validation.
- **Recommended correction:** Reject lengths greater than 120 and return a 120-character limit message.

### BUG-6 — Task titles may be unsafe in HTML attributes

- **Location:** `frontend/app.js:44-54`
- **Function:** `renderTasks()`
- **Error category:** Runtime / Rendering
- **Explanation:** The title is placed into `aria-label="Status for ..."` after HTML escaping. Some quote characters can corrupt an attribute unless handled in attribute context.
- **Expected application behavior:** Any valid task title should render safely.
- **Actual behavior:** Titles containing quote characters or specially formed markup may corrupt the select element’s HTML.
- **Recommended correction:** Avoid interpolating task data into HTML attributes or construct DOM elements and set the `aria-label` property directly.

### BUG-7 — Test suite misses key affected behaviors

- **Location:** `tests/test_api.py:26-36` and `tests/test_api.py:77-79`
- **Function:** `test_create_task()` and validation tests
- **Error category:** Test Coverage
- **Explanation:** The suite verifies a default-pending creation but does not verify a caller-provided status, and no test exercises the 120/121-character title boundary.
- **Expected application behavior:** Tests should prove status preservation and title length validation.
- **Actual behavior:** The injected logical and validation bugs remain undetected.
- **Recommended correction:** Add boundary tests for 120/121-character titles and create-task tests for `completed` or `in_progress` statuses.
