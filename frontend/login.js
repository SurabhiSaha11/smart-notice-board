const API_URL = "http://127.0.0.1:5000";
let isRegister = false;

if (localStorage.getItem("token")) {
    window.location.href = "index.html";
}

const nameInput = document.getElementById("name");
const title = document.getElementById("auth-title");
const submitBtn = document.getElementById("auth-submit");
const toggleLink = document.getElementById("toggle-link");
const message = document.getElementById("auth-message");

function setMode(register) {
    isRegister = register;
    nameInput.style.display = register ? "block" : "none";
    nameInput.required = register;
    title.textContent = register ? "Register (Student)" : "Login";
    submitBtn.textContent = register ? "Register" : "Login";
    toggleLink.textContent = register ? "Already registered? Login" : "New student? Register here";
}

toggleLink.addEventListener("click", function (e) {
    e.preventDefault();
    message.textContent = "";
    setMode(!isRegister);
});

document.getElementById("auth-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    message.style.color = "#e74c3c";
    message.textContent = "";

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        if (isRegister) {
            const res = await fetch(`${API_URL}/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: nameInput.value, email, password })
            });
            const data = await res.json();
            if (!res.ok) { message.textContent = data.error; return; }

            setMode(false);
            message.style.color = "#27ae60";
            message.textContent = "Registered! Please log in.";
        } else {
            const res = await fetch(`${API_URL}/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            if (!res.ok) { message.textContent = data.error; return; }

            localStorage.setItem("token", data.token);
            localStorage.setItem("user", JSON.stringify(data.user));
            window.location.href = "index.html";
        }
    } catch (err) {
        message.textContent = "Cannot reach the server. Is Flask running?";
    }
});
