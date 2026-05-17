// IntelliExpert AI - Premium Dashboard Javascript

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    loadSymptoms();
    loadKnowledgeBase();
    setupDiagnosis();
    setupChatbot();
    setupReports();
    setupSettings();
    updateDashboardStats();
});

// ── Tab Management ───────────────────────────────────────────────────────────
function initTabs() {
    const navItems = document.querySelectorAll(".nav-item");
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const tabId = item.getAttribute("data-tab");
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    // Update sidebar buttons
    document.querySelectorAll(".nav-item").forEach(btn => {
        btn.classList.remove("active");
        if (btn.getAttribute("data-tab") === tabId) {
            btn.classList.add("active");
        }
    });

    // Update main panels
    document.querySelectorAll(".tab-pane").forEach(pane => {
        pane.classList.remove("active");
    });
    const activePane = document.getElementById(`tab-${tabId}`);
    if (activePane) {
        activePane.classList.add("active");
    }

    // Set page header title
    const headerTitle = document.getElementById("page-title");
    headerTitle.innerText = tabId.charAt(0).toUpperCase() + tabId.slice(1) + " Panel";

    // Lazy load logic
    if (tabId === "analysis") {
        renderCharts();
    } else if (tabId === "reports" || tabId === "history") {
        loadHistoryTable();
    }
}

// ── Load symptoms dynamically from API ──────────────────────────────────────
async function loadSymptoms() {
    try {
        const response = await fetch("/api/symptoms");
        const symptoms = await response.json();
        const container = document.getElementById("symptom-checkboxes");
        container.innerHTML = "";

        symptoms.forEach(symptom => {
            const label = symptom.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
            const chip = document.createElement("label");
            chip.className = "symptom-chip";
            chip.innerHTML = `
                <input type="checkbox" value="${symptom}">
                <span>${label}</span>
            `;
            
            const checkbox = chip.querySelector("input");
            checkbox.addEventListener("change", () => {
                if (checkbox.checked) {
                    chip.classList.add("selected");
                } else {
                    chip.classList.remove("selected");
                }
            });

            container.appendChild(chip);
        });
    } catch (e) {
        console.error("Failed to load symptoms", e);
    }
}

// ── Setup Logic for Diagnosis Engine ───────────────────────────────────────
function setupDiagnosis() {
    const btn = document.getElementById("btn-run-diagnosis");
    const progressContainer = document.getElementById("diagnosis-progress");
    const progressFill = progressContainer.querySelector(".progress-bar-fill");
    const resultsContainer = document.getElementById("diagnosis-results");
    const cardsList = document.getElementById("results-cards-list");

    btn.addEventListener("click", async () => {
        const selectedCheckboxes = document.querySelectorAll("#symptom-checkboxes input:checked");
        const symptoms = Array.from(selectedCheckboxes).map(cb => cb.value);

        if (symptoms.length === 0) {
            alert("Please select at least one symptom to analyze.");
            return;
        }

        // Reset display
        resultsContainer.style.display = "none";
        cardsList.innerHTML = "";
        btn.disabled = true;
        progressContainer.style.display = "block";
        progressFill.style.width = "0%";

        // Animate simulated scanner
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            progressFill.style.width = `${progress}%`;
            if (progress >= 100) {
                clearInterval(interval);
            }
        }, 100);

        try {
            const response = await fetch("/api/diagnose", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ symptoms })
            });

            const data = await response.json();
            clearInterval(interval);
            progressFill.style.width = "100%";

            setTimeout(() => {
                progressContainer.style.display = "none";
                btn.disabled = false;

                if (!data.success) {
                    cardsList.innerHTML = `<div class="card">${data.message}</div>`;
                } else if (data.diagnoses.length === 0) {
                    cardsList.innerHTML = `<div class="card">No matching diseases found in our rule-base. Please consult a professional.</div>`;
                } else {
                    data.diagnoses.forEach(diag => {
                        const recs = diag.details.recommendations.map(r => `<li>${r}</li>`).join("");
                        const meds = diag.details.medicines.map(m => `<span>${m}</span>`).join(" ");
                        const precautions = diag.details.precautions.map(p => `<li>${p}</li>`).join("");

                        const card = document.createElement("div");
                        card.className = "results-card";
                        card.innerHTML = `
                            <div class="results-header">
                                <h3>${diag.disease.toUpperCase()}</h3>
                                <span class="confidence-badge">${diag.confidence.toFixed(1)}% Match Confidence</span>
                            </div>
                            <div class="reasoning-box">${diag.explanation}</div>
                            <div style="margin-top: 15px;">
                                <strong>Suggested Care Protocols:</strong>
                                <ul>${recs}</ul>
                            </div>
                            <div style="margin-top: 12px;">
                                <strong>Safety Precautions:</strong>
                                <ul>${precautions}</ul>
                            </div>
                            <div style="margin-top: 15px;">
                                <strong>Knowledge Base Suggested Medicines:</strong>
                                <div style="margin-top: 5px;">${meds}</div>
                            </div>
                        `;
                        cardsList.appendChild(card);
                    });
                }
                resultsContainer.style.display = "block";
                updateDashboardStats();
            }, 1000);

        } catch (e) {
            clearInterval(interval);
            progressContainer.style.display = "none";
            btn.disabled = false;
            alert("Error connecting to Prolog Inference Server.");
        }
    });
}

// ── Setup RAG AI Chatbot ───────────────────────────────────────────────────
function setupChatbot() {
    const input = document.getElementById("chat-input");
    const btn = document.getElementById("btn-send-chat");
    const container = document.getElementById("chat-messages-container");

    const welcome = `👋 Hello! I am <b>IntelliBot</b>, your offline hybrid AI assistant. 
    I can answer detailed medical questions based on our integrated Prolog rule-base and clinical history. 
    <br><br>
    Feel free to query me about symptoms, precautions, treatments or medicines!`;
    appendChatMessage("bot", welcome);

    btn.addEventListener("click", () => sendChat());
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendChat();
    });

    async function sendChat() {
        const message = input.value.trim();
        if (!message) return;

        appendChatMessage("user", message);
        input.value = "";

        // Show loading indicator
        const loadingDiv = document.createElement("div");
        loadingDiv.className = "message bot";
        loadingDiv.innerText = "IntelliBot is thinking...";
        container.appendChild(loadingDiv);
        container.scrollTop = container.scrollHeight;

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message })
            });
            const data = await response.json();
            container.removeChild(loadingDiv);
            appendChatMessage("bot", data.reply);
        } catch (e) {
            container.removeChild(loadingDiv);
            appendChatMessage("bot", "Sorry, I am having trouble fetching a response.");
        }
    }

    function appendChatMessage(sender, text) {
        const msg = document.createElement("div");
        msg.className = `message ${sender}`;
        msg.innerHTML = text;
        container.appendChild(msg);
        container.scrollTop = container.scrollHeight;
    }
}

// ── Setup Analytics Dashboard Charts ────────────────────────────────────────
let chartDiseaseInstance = null;
let chartConfidenceInstance = null;

async function renderCharts() {
    try {
        const response = await fetch("/api/history");
        const history = await response.json();

        if (history.length === 0) return;

        const diseaseCounts = {};
        const confidences = [];

        history.forEach(item => {
            diseaseCounts[item.diagnosis] = (diseaseCounts[item.diagnosis] || 0) + 1;
            confidences.push(parseFloat(item.confidence));
        });

        // 1. Render Disease Donut Chart
        const ctxD = document.getElementById("chart-diseases").getContext("2d");
        if (chartDiseaseInstance) chartDiseaseInstance.destroy();
        chartDiseaseInstance = new Chart(ctxD, {
            type: 'doughnut',
            data: {
                labels: Object.keys(diseaseCounts),
                datasets: [{
                    data: Object.values(diseaseCounts),
                    backgroundColor: ['#2563EB', '#60A5FA', '#93C5FD', '#BFDBFE', '#A78BFA', '#F59E0B']
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom' } }
            }
        });

        // 2. Render Confidence Scatter/Bar Chart
        const ctxC = document.getElementById("chart-confidence").getContext("2d");
        if (chartConfidenceInstance) chartConfidenceInstance.destroy();
        chartConfidenceInstance = new Chart(ctxC, {
            type: 'bar',
            data: {
                labels: history.map((_, i) => `Case #${i+1}`),
                datasets: [{
                    label: 'Confidence Certainty (%)',
                    data: confidences,
                    backgroundColor: '#3B82F6',
                    borderColor: '#2563EB',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: { y: { min: 0, max: 100 } }
            }
        });

    } catch (e) {
        console.error("Failed to load charts", e);
    }
}

// ── Setup Audit Reports Table ──────────────────────────────────────────────
async function loadHistoryTable() {
    try {
        const response = await fetch("/api/history");
        const history = await response.json();

        // Update tables
        const reportTable = document.querySelector("#table-reports tbody");
        const historyTable = document.querySelector("#table-history tbody");

        const updateTable = (tbody) => {
            if (!tbody) return;
            tbody.innerHTML = "";
            if (history.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align: center;">No diagnostic data found in SQLite system logs.</td></tr>`;
                return;
            }
            history.forEach(item => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${item.id}</td>
                    <td>${item.timestamp}</td>
                    <td>${item.symptoms}</td>
                    <td><b>${item.diagnosis}</b></td>
                    <td>${item.confidence}</td>
                `;
                tbody.appendChild(tr);
            });
        };

        updateTable(reportTable);
        updateTable(historyTable);

    } catch (e) {
        console.error("Failed to load history table", e);
    }
}

function setupReports() {
    const btn = document.getElementById("btn-download-pdf");
    btn.addEventListener("click", () => {
        window.open("/api/export_pdf", "_blank");
    });

    const btnClear = document.getElementById("btn-clear-history");
    if (btnClear) {
        btnClear.addEventListener("click", async () => {
            if (confirm("Are you sure you want to completely erase SQLite diagnostic logs?")) {
                await fetch("/api/clear_history", { method: "POST" });
                loadHistoryTable();
                updateDashboardStats();
            }
        });
    }
}

// ── Setup Knowledge Base Section ────────────────────────────────────────────
async function loadKnowledgeBase() {
    try {
        const response = await fetch("/api/knowledge_base");
        const kb = await response.json();
        const container = document.getElementById("kb-cards-container");
        container.innerHTML = "";

        Object.entries(kb).forEach(([disease, info]) => {
            const card = document.createElement("div");
            card.className = "kb-card";
            card.setAttribute("data-search", `${disease} ${info.full_name} ${info.symptoms.join(" ")}`.toLowerCase());
            card.innerHTML = `
                <h3>${info.full_name}</h3>
                <p>${info.description}</p>
                <div class="kb-card-sections">
                    <div><b>Symptoms:</b> ${info.symptoms.join(", ")}</div>
                    <div><b>Prescriptions:</b> ${info.medicines.join(", ")}</div>
                    <div><b>Care Recommendations:</b> ${info.recommendations.join(", ")}</div>
                    <div><b>Precautions:</b> ${info.precautions.join(", ")}</div>
                </div>
            `;
            container.appendChild(card);
        });

        // Search trigger
        const searchInput = document.getElementById("kb-search");
        searchInput.addEventListener("input", (e) => {
            const q = e.target.value.toLowerCase().trim();
            document.querySelectorAll(".kb-card").forEach(card => {
                if (card.getAttribute("data-search").includes(q)) {
                    card.style.display = "block";
                } else {
                    card.style.display = "none";
                }
            });
        });
    } catch (e) {
        console.error("Failed to load knowledge base", e);
    }
}

// ── Setup Settings Interface ───────────────────────────────────────────────
function setupSettings() {
    const themeSelect = document.getElementById("settings-theme");
    
    // Save theme
    themeSelect.addEventListener("change", (e) => {
        const theme = e.target.value;
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("theme", theme);
    });

    // Load theme
    const savedTheme = localStorage.getItem("theme") || "light";
    themeSelect.value = savedTheme;
    document.documentElement.setAttribute("data-theme", savedTheme);
}

// ── Update General Dashboard Statistics ─────────────────────────────────────
async function updateDashboardStats() {
    try {
        const response = await fetch("/api/history");
        const history = await response.json();

        document.getElementById("stat-count").innerText = history.length;

        if (history.length > 0) {
            const totalConfidence = history.reduce((sum, item) => sum + parseFloat(item.confidence), 0);
            const avg = totalConfidence / history.length;
            document.getElementById("stat-avg-confidence").innerText = `${avg.toFixed(1)}%`;
        } else {
            document.getElementById("stat-avg-confidence").innerText = "0%";
        }
    } catch (e) {
        console.error("Failed to update stats", e);
    }
}
