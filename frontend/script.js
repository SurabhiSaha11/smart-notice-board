const API_URL = "http://127.0.0.1:5000";
const token = localStorage.getItem("token");
const user = JSON.parse(localStorage.getItem("user") || "null");
const isAdmin = user && user.role === "admin";

let currentCategory = "";
let noticesById = {};

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "login.html";
}

function authHeaders(json = false) {
    const headers = { "Authorization": `Bearer ${token}` };
    if (json) headers["Content-Type"] = "application/json";
    return headers;
}

async function apiFetch(url, options = {}) {
    const res = await fetch(url, options);
    if (res.status === 401) {
        logout();
        throw new Error("Not authorised");
    }
    return res;
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

async function loadNotices() {
    const url = currentCategory
        ? `${API_URL}/notices?category=${currentCategory}`
        : `${API_URL}/notices`;

    const response = await apiFetch(url, { headers: authHeaders() });
    const notices = await response.json();

    const noticeList = document.getElementById("notice-list");
    noticeList.innerHTML = "";
    noticesById = {};

    if (notices.length === 0) {
        noticeList.innerHTML = "<p>No notices found.</p>";
        return;
    }

    notices.forEach(notice => {
        noticesById[notice.id] = notice;

        const actions = isAdmin
            ? `<div class="card-actions">
                   <button class="edit-btn" onclick="editNotice(${notice.id})">Edit</button>
                   <button class="delete-btn" onclick="deleteNotice(${notice.id})">Delete</button>
               </div>`
            : "";

        const expiry = notice.expiry_date
            ? `<p class="expiry-note">Expires: ${notice.expiry_date}</p>`
            : "";

        const attachment = notice.attachment_url
            ? `<p><a href="${notice.attachment_url}" target="_blank">📎 View attachment</a></p>`
            : "";

        const card = document.createElement("div");
        card.className = "notice-card";
        card.innerHTML = `
            <span class="notice-category">${escapeHtml(notice.category)}</span>
            <h3>${escapeHtml(notice.title)}</h3>
            <p>${escapeHtml(notice.description)}</p>
            ${expiry}
            ${attachment}
            ${actions}
        `;
        noticeList.appendChild(card);
    });
}

async function editNotice(id) {
    const notice = noticesById[id];
    const newTitle = prompt("Edit title:", notice.title);
    if (newTitle === null) return;
    const newDescription = prompt("Edit description:", notice.description);
    if (newDescription === null) return;

    const res = await apiFetch(`${API_URL}/notices/${id}`, {
        method: "PUT",
        headers: authHeaders(true),
        body: JSON.stringify({ title: newTitle, description: newDescription })
    });
    if (!res.ok) { alert("Could not update notice"); return; }
    loadNotices();
}

async function deleteNotice(id) {
    if (!confirm("Delete this notice?")) return;
    const res = await apiFetch(`${API_URL}/notices/${id}`, {
        method: "DELETE",
        headers: authHeaders()
    });
    if (!res.ok) { alert("Could not delete notice"); return; }
    loadNotices();
}

document.querySelectorAll(".filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        currentCategory = btn.dataset.category;
        document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        loadNotices();
    });
});

document.getElementById("logout-btn").addEventListener("click", logout);

const noticeForm = document.getElementById("notice-form");
noticeForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append("title", document.getElementById("title").value);
    formData.append("description", document.getElementById("description").value);
    formData.append("category", document.getElementById("category").value);

    const expiry = document.getElementById("expiry").value;
    if (expiry) formData.append("expiry_date", expiry);

    const file = document.getElementById("attachment").files[0];
    if (file) formData.append("attachment", file);

    const res = await apiFetch(`${API_URL}/notices`, {
        method: "POST",
        headers: authHeaders(),   // no Content-Type: the browser sets it for file uploads
        body: formData
    });

    if (!res.ok) {
        let msg = "Could not post notice";
        try { msg = (await res.json()).error || msg; } catch (e) {}
        alert(msg);
        return;
    }

    noticeForm.reset();
    loadNotices();
});

function init() {
    document.getElementById("user-info").textContent = `${user.name} (${user.role})`;
    if (isAdmin) {
        document.getElementById("post-section").style.display = "block";
    }
    loadNotices();
}

if (!token || !user) {
    window.location.href = "login.html";
} else {
    init();
}
