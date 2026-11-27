async function checkServer() {
    const status = document.getElementById("status");
    try {
        const response = await fetch("/api/health");
        if (!response.ok) throw new Error("Request failed");
        const data = await response.json();
        status.textContent = data.status === "ok" ? "Server connected" : "Server unavailable";
    } catch (error) {
        status.textContent = "Server unavailable";
    }
}
checkServer();
