const API_URL = "http://127.0.0.1:5000";
let currentCategory = "";
let noticesById = {};

async function loadNotices() {
    const url = currentCategory
        ? `${API_URL}/notices?category=${currentCategory}`
        : `${API_URL}/notices`;

    const response = await fetch(url);
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

        const card = document.createElement("div");
        card.className = "notice-card";
        card.innerHTML = `
            <span class="notice-category">${notice.category}</span>
            <h3>${notice.title}</h3>
            <p>${notice.description}</p>
            <div class="card-actions">
                <button class="edit-btn" onclick="editNotice(${notice.id})">Edit</button>
                <button class="delete-btn" onclick="deleteNotice(${notice.id})">Delete</button>
            </div>
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

    await fetch(`${API_URL}/notices/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: newTitle, description: newDescription })
    });
    loadNotices();
}

async function deleteNotice(id) {
    if (!confirm("Delete this notice?")) return;
    await fetch(`${API_URL}/notices/${id}`, { method: "DELETE" });
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

document.getElementById("notice-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;
    const category = document.getElementById("category").value;

    await fetch(`${API_URL}/notices`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, description, category, posted_by: 1 })
    });

    document.getElementById("notice-form").reset();
    loadNotices();
});

loadNotices();
