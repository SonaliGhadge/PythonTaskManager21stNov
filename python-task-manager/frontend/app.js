const API_URL = "http://127.0.0.1:5000/api/tasks";

const elements = {
  formSection: document.getElementById("taskFormSection"),
  form: document.getElementById("taskForm"),
  alert: document.getElementById("alert"),
  loading: document.getElementById("loadingState"),
  empty: document.getElementById("emptyState"),
  tableWrapper: document.getElementById("taskTableWrapper"),
  tableBody: document.getElementById("taskTableBody")
};

function showAlert(message, type = "success") {
  elements.alert.textContent = message;
  elements.alert.className = `alert ${type}`;
  window.clearTimeout(showAlert.timeout);
  showAlert.timeout = window.setTimeout(() => { elements.alert.className = "alert hidden"; }, 4000);
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) }
  });
  let data;
  try { data = await response.json(); } catch (_) { data = {}; }
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}

function escapeHtml(value) {
  const node = document.createTextNode(value == null ? "" : String(value));
  const span = document.createElement("span");
  span.appendChild(node);
  return span.innerHTML;
}

function renderStats(tasks) {
  document.getElementById("totalCount").textContent = tasks.length;
  document.getElementById("pendingCount").textContent = tasks.filter(task => task.status === "pending").length;
  document.getElementById("progressCount").textContent = tasks.filter(task => task.status === "in_progress").length;
  document.getElementById("completedCount").textContent = tasks.filter(task => task.status === "completed").length;
}

function renderTasks(tasks) {
  renderStats(tasks);
  elements.loading.classList.add("hidden");
  elements.empty.classList.toggle("hidden", tasks.length !== 0);
  elements.tableWrapper.classList.toggle("hidden", tasks.length === 0);

  elements.tableBody.innerHTML = tasks.map(task => `
    <tr>
      <td><div class="task-title">${escapeHtml(task.title)}</div><div class="task-description">${escapeHtml(task.description || "No description")}</div></td>
      <td><select class="status-select status-${task.status}" data-action="status" data-id="${task.id}" aria-label="Status for ${escapeHtml(task.title)}">
        <option value="pending" ${task.status === "pending" ? "selected" : ""}>Pending</option>
        <option value="in_progress" ${task.status === "in_progress" ? "selected" : ""}>In progress</option>
        <option value="completed" ${task.status === "completed" ? "selected" : ""}>Completed</option>
      </select></td>
      <td>${new Date(task.created_at).toLocaleDateString(undefined, { year:"numeric", month:"short", day:"numeric" })}</td>
      <td><button class="delete-button" data-action="delete" data-id="${task.id}" type="button">Delete</button></td>
    </tr>`).join("");
}

async function loadTasks() {
  elements.loading.classList.remove("hidden");
  elements.tableWrapper.classList.add("hidden");
  elements.empty.classList.add("hidden");
  try {
    const tasks = await apiRequest(API_URL);
    renderTasks(tasks);
  } catch (error) {
    elements.loading.classList.add("hidden");
    showAlert(error.message, "error");
  }
}

function openForm() { elements.formSection.classList.remove("hidden"); document.getElementById("title").focus(); }
function closeForm() { elements.formSection.classList.add("hidden"); elements.form.reset(); }

document.getElementById("showFormButton").addEventListener("click", openForm);
document.getElementById("closeFormButton").addEventListener("click", closeForm);
document.getElementById("cancelFormButton").addEventListener("click", closeForm);
document.getElementById("refreshButton").addEventListener("click", loadTasks);

elements.form.addEventListener("submit", async event => {
  event.preventDefault();
  const submitButton = elements.form.querySelector("button[type='submit']");
  submitButton.disabled = true;
  const payload = { title: document.getElementById("title").value, description: document.getElementById("description").value, status: document.getElementById("status").value };
  try {
    await apiRequest(API_URL, { method:"POST", body:JSON.stringify(payload) });
    closeForm();
    showAlert("Task created successfully.");
    await loadTasks();
  } catch (error) {
    showAlert(error.message, "error");
  } finally {
    submitButton.disabled = false;
  }
});

elements.tableBody.addEventListener("change", async event => {
  if (event.target.dataset.action !== "status") return;
  const id = event.target.dataset.id;
  try {
    await apiRequest(`${API_URL}/${id}`, { method:"PUT", body:JSON.stringify({ status:event.target.value }) });
    showAlert("Task status updated.");
    await loadTasks();
  } catch (error) {
    showAlert(error.message, "error");
    await loadTasks();
  }
});

elements.tableBody.addEventListener("click", async event => {
  if (event.target.dataset.action !== "delete") return;
  if (!window.confirm("Delete this task?")) return;
  const id = event.target.dataset.id;
  try {
    await apiRequest(`${API_URL}/${id}`, { method:"DELETE" });
    showAlert("Task deleted successfully.");
    await loadTasks();
  } catch (error) {
    showAlert(error.message, "error");
  }
});

loadTasks();
