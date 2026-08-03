"use strict";
const $ = (id) => document.getElementById(id);

let channel = "sms";
let lastId = null;

const CHAN_ICON = { call: "📞", sms: "💬", whatsapp: "🟢", notification: "🔔", email: "✉️" };

// ---------- Channel tabs ---------- //
document.querySelectorAll(".chan-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
        document.querySelectorAll(".chan-tab").forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        channel = tab.dataset.channel;
        $("subjectWrap").classList.toggle("hidden", channel !== "email");
    });
});

// ---------- Analyze ---------- //
async function analyze() {
    const text = $("msgInput").value.trim();
    if (!text) { $("msgInput").focus(); return; }
    const btn = $("analyzeBtn");
    btn.disabled = true; btn.textContent = "Analyzing…";
    try {
        const res = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text, channel,
                sender: $("senderInput").value.trim(),
                subject: $("subjectInput").value.trim(),
            }),
        });
        const data = await res.json();
        if (data.ok) { renderResult(data.result); refresh(); }
        else { alert(data.error || "Analysis failed"); }
    } catch (e) {
        alert("Request failed: " + e.message);
    } finally {
        btn.disabled = false; btn.textContent = "🔍 Analyze";
    }
}

function renderResult(r) {
    lastId = r.id;
    const card = $("resultCard");
    card.classList.remove("hidden");

    // gauge
    const arc = $("gaugeArc");
    const circ = 327;
    arc.style.strokeDashoffset = circ - (circ * r.risk) / 100;
    const color = r.level === "SCAM" ? "#ff5470" : r.level === "SUSPICIOUS" ? "#ffb020" : "#2fd18a";
    arc.style.stroke = color;
    animateNum($("riskNum"), r.risk);

    const badge = $("levelBadge");
    badge.textContent = r.level;
    badge.className = "level-badge " + r.level;
    $("categoryLabel").textContent = r.category_label || "—";
    $("confidence").textContent = `Confidence ${Math.round(r.confidence * 100)}% · ${r.channel_label}`;
    $("engineTag").textContent = r.engine === "rules+llm" ? "Analyzed by rules + LLM" : "Analyzed by rule engine";
    $("adviceBox").textContent = r.advice;

    const rl = $("reasonsList");
    rl.innerHTML = "";
    (r.reasons || []).forEach((x) => { const li = document.createElement("li"); li.textContent = x; rl.appendChild(li); });

    renderEntities(r.entities);
    $("fbMsg").textContent = "";
    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function renderEntities(e) {
    const box = $("entitiesBox");
    box.innerHTML = "";
    const add = (label, arr, bad) => {
        (arr || []).forEach((v) => {
            const s = document.createElement("span");
            s.className = "chip" + (bad ? " bad" : "");
            s.textContent = `${label}: ${v}`;
            box.appendChild(s);
        });
    };
    add("UPI", e.upi, true);
    add("Link", e.urls, true);
    add("Phone", e.phones, false);
    add("Amount", e.amounts, false);
    if (e.otp_terms && e.otp_terms.length) add("OTP/PIN", e.otp_terms, true);
    if (!box.children.length) {
        const s = document.createElement("span"); s.className = "empty"; s.textContent = "No risky entities found."; box.appendChild(s);
    }
}

function animateNum(el, target) {
    let cur = 0; const step = Math.max(1, Math.round(target / 24));
    const t = setInterval(() => { cur += step; if (cur >= target) { cur = target; clearInterval(t); } el.textContent = cur; }, 18);
}

// ---------- Samples ---------- //
async function loadSamples() {
    try {
        const res = await fetch("/samples");
        const data = await res.json();
        const box = $("sampleChips");
        box.innerHTML = "";
        (data.samples || []).forEach((s) => {
            const chip = document.createElement("button");
            chip.className = "sample-chip";
            chip.innerHTML = `<span class="ic">${CHAN_ICON[s.channel] || "•"}</span>${s.label}`;
            chip.addEventListener("click", () => applySample(s));
            box.appendChild(chip);
        });
    } catch (e) { /* ignore */ }
}

function applySample(s) {
    channel = s.channel;
    document.querySelectorAll(".chan-tab").forEach((t) => t.classList.toggle("active", t.dataset.channel === s.channel));
    $("subjectWrap").classList.toggle("hidden", s.channel !== "email");
    $("senderInput").value = s.sender || "";
    $("subjectInput").value = s.subject || "";
    $("msgInput").value = s.text || "";
    analyze();
}

// ---------- Stats + history ---------- //
async function refresh() {
    try {
        const [st, hist] = await Promise.all([
            fetch("/stats").then((r) => r.json()),
            fetch("/history").then((r) => r.json()),
        ]);
        renderStats(st);
        renderHistory(hist.items || []);
    } catch (e) { /* ignore */ }
}

function renderStats(st) {
    $("stScams").textContent = st.scams || 0;
    $("stSusp").textContent = st.suspicious || 0;
    $("stSafe").textContent = st.safe || 0;
    $("stTotal").textContent = st.total || 0;

    const box = $("byChannel");
    box.innerHTML = "";
    const bc = st.by_channel || {};
    const max = Math.max(1, ...Object.values(bc));
    Object.keys(bc).forEach((k) => {
        const row = document.createElement("div"); row.className = "mini-bar";
        row.innerHTML = `<span class="lbl">${CHAN_ICON[k] || ""} ${k}</span>
            <span class="track"><span class="fill" style="width:${(bc[k] / max) * 100}%"></span></span>
            <span class="val">${bc[k]}</span>`;
        box.appendChild(row);
    });
}

function renderHistory(items) {
    const box = $("historyList");
    box.innerHTML = "";
    if (!items.length) { box.innerHTML = '<div class="empty">No messages analyzed yet.</div>'; return; }
    items.forEach((it) => {
        const div = document.createElement("div");
        div.className = "hist-item " + it.level;
        div.innerHTML = `<div class="hist-top">
                <span class="hist-chan">${CHAN_ICON[it.channel] || ""} ${it.channel}</span>
                <span class="hist-risk ${it.level}">${it.risk} · ${it.level}</span>
            </div>
            <div class="hist-text">${escapeHtml(it.text_preview || "")}</div>`;
        box.appendChild(div);
    });
}

function escapeHtml(s) {
    return (s || "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// ---------- Feedback ---------- //
document.querySelectorAll(".fb").forEach((b) => {
    b.addEventListener("click", async () => {
        if (lastId == null) return;
        await fetch("/feedback", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: lastId, label: b.dataset.fb }),
        });
        $("fbMsg").textContent = "Thanks — feedback saved.";
    });
});

$("analyzeBtn").addEventListener("click", analyze);
$("clearBtn").addEventListener("click", () => {
    $("msgInput").value = ""; $("senderInput").value = ""; $("subjectInput").value = "";
    $("resultCard").classList.add("hidden");
});
$("msgInput").addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") analyze();
});

loadSamples();
refresh();
