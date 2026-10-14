const API_URL = "http://127.0.0.1:5000";

async function loadNotices() {
    const response = await fetch(`${API_URL}/notices`);
    const notices = await response.json();

    const noticeList = document.getElementById("notice-list");
    noticeList.innerHTML = "";

    notices.forEach(notice => {
        const card = document.createElement("div");
        card.className = "notice-card";

        card.innerHTML = `
            <span class="notice-category">${notice.category}</span>
            <h3>${notice.title}</h3>
            <p>${notice.description}</p>
        `;

        noticeList.appendChild(card);
    });
}

loadNotices();

document.getElementById("notice-form").addEventListener("submit", async function(event) {
    event.preventDefault();

    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;
    const category = document.getElementById("category").value;

    await fetch(`${API_URL}/notices`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            title: title,
            description: description,
            category: category,
            posted_by: 1
        })
    });

    document.getElementById("notice-form").reset();
    loadNotices();
});
