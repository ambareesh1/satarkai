"use strict";
const $ = (id) => document.getElementById(id);

let channel = "sms";
let lastId = null;
let inbox = [];
let currentMsg = null;

const CHAN_ICON = { call: "📞", sms: "💬", whatsapp: "🟢", notification: "🔔", email: "✉️" };
const APP_CHANNEL = { messages: "sms", whatsapp: "whatsapp", mail: "email", phone: "call", notifications: "notification" };

/* ================= iPhone clock ================= */
function tickClock() {
    const now = new Date();
    const t = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const d = now.toLocaleDateString([], { weekday: "long", day: "numeric", month: "long" });
    $("iosTime").textContent = t;
    $("homeTime").textContent = t;
    $("homeDate").textContent = d;
}

/* ================= Phone navigation ================= */
function showView(name) {
    ["phoneHome", "phoneApp", "phoneMsg"].forEach((id) =>
        $(id).classList.toggle("hidden", id !== "phone" + name.charAt(0).toUpperCase() + name.slice(1)));
}

async function loadPhone() {
    try {
        const [appsRes, inboxRes] = await Promise.all([
            fetch("/apps").then((r) => r.json()),
            fetch("/inbox").then((r) => r.json()),
        ]);
        inbox = inboxRes.items || [];
        renderAppGrid(appsRes.apps || []);
    } catch (e) { /* ignore */ }
}

function renderAppGrid(apps) {
    const grid = $("appGrid");
    grid.innerHTML = "";
    apps.forEach((a) => {
        const el = document.createElement("div");
        el.className = "app-ico";
        el.innerHTML = `
            <div class="glyph" style="background:${a.color}">${a.icon}</div>
            <span class="lbl">${a.name}</span>
            ${a.badge ? `<span class="badge">${a.badge}</span>` : ""}`;
        el.addEventListener("click", () => openApp(a.app, a.name));
        grid.appendChild(el);
    });
}

function openApp(app, name) {
    $("appTitle").textContent = name;
    const list = $("appList");
    list.innerHTML = "";
    const items = inbox.filter((m) => m.app === app);
    if (!items.length) { list.innerHTML = '<p class="ios-hint">No messages.</p>'; }
    items.forEach((m) => {
        const row = document.createElement("div");
        row.className = "msg-row";
        row.innerHTML = `
            <div class="av">${m.avatar || "👤"}</div>
            <div class="mid">
                <div class="nm"><b>${escapeHtml(m.name || m.sender)}</b><span class="tm">${m.time || ""}</span></div>
                <div class="pv">${escapeHtml(m.preview || m.text.slice(0, 50))}</div>
            </div>
            ${m.scam ? '<div class="warn-dot" title="SatarkAI flagged"></div>' : ""}`;
        row.addEventListener("click", () => openMessage(m));
        list.appendChild(row);
    });
    showView("app");
}

function openMessage(m) {
    currentMsg = m;
    $("msgTitle").textContent = m.name || m.sender;
    const body = $("msgBody");
    const isMail = m.app === "mail";
    const isCall = !!m.call;
    body.innerHTML = `
        <div class="msg-meta">From: ${escapeHtml(m.sender)} · ${m.time || ""}</div>
        ${isMail && m.subject ? `<div class="bubble mail-head"><div class="subj">${escapeHtml(m.subject)}</div><div class="frm">${escapeHtml(m.sender)}</div></div>` : ""}
        <div class="bubble">${isCall ? "📞 Call transcript:<br>" : ""}${escapeHtml(m.text)}</div>`;
    $("playCallBtn").classList.toggle("hidden", !isCall);

    // Fill the analyzer form (per the requested flow).
    fillForm(m.channel, m.sender, m.subject || "", m.text);
    showView("msg");
}

/* ================= Fill + analyze ================= */
function fillForm(chan, sender, subject, text) {
    channel = chan;
    document.querySelectorAll(".chan-tab").forEach((t) => t.classList.toggle("active", t.dataset.channel === chan));
    $("subjectWrap").classList.toggle("hidden", chan !== "email");
    $("senderInput").value = sender || "";
    $("subjectInput").value = subject || "";
    $("msgInput").value = text || "";
}

async function analyze(showPhoneAlert) {
    const text = $("msgInput").value.trim();
    if (!text) { $("msgInput").focus(); return null; }
    const btn = $("analyzeBtn");
    btn.disabled = true; btn.textContent = "Analyzing…";
    try {
        const res = await fetch("/analyze", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text, channel,
                sender: $("senderInput").value.trim(),
                subject: $("subjectInput").value.trim(),
            }),
        });
        const data = await res.json();
        if (data.ok) {
            renderResult(data.result);
            if (showPhoneAlert) showAlert(data.result);
            refresh();
            return data.result;
        }
        alert(data.error || "Analysis failed");
    } catch (e) { alert("Request failed: " + e.message); }
    finally { btn.disabled = false; btn.textContent = "🔍 Analyze"; }
    return null;
}

function renderResult(r) {
    lastId = r.id;
    $("resultCard").classList.remove("hidden");
    const arc = $("gaugeArc"); const circ = 327;
    arc.style.strokeDashoffset = circ - (circ * r.risk) / 100;
    arc.style.stroke = colorFor(r.level);
    animateNum($("riskNum"), r.risk);
    const badge = $("levelBadge");
    badge.textContent = r.level; badge.className = "level-badge " + r.level;
    $("categoryLabel").textContent = r.category_label || "—";
    $("confidence").textContent = `Confidence ${Math.round(r.confidence * 100)}% · ${r.channel_label}`;
    $("engineTag").textContent = r.engine === "rules+llm" ? "Analyzed by rules + LLM" : "Analyzed by rule engine";
    $("adviceBox").textContent = r.advice;
    const rl = $("reasonsList"); rl.innerHTML = "";
    (r.reasons || []).forEach((x) => { const li = document.createElement("li"); li.textContent = x; rl.appendChild(li); });
    renderEntities(r.entities);
    $("fbMsg").textContent = "";
}

function renderEntities(e) {
    const box = $("entitiesBox"); box.innerHTML = "";
    const add = (label, arr, bad) => (arr || []).forEach((v) => {
        const s = document.createElement("span"); s.className = "chip" + (bad ? " bad" : "");
        s.textContent = `${label}: ${v}`; box.appendChild(s);
    });
    add("UPI", e.upi, true); add("Link", e.urls, true); add("Phone", e.phones, false);
    add("Amount", e.amounts, false);
    if (e.otp_terms && e.otp_terms.length) add("OTP/PIN", e.otp_terms, true);
    if (!box.children.length) { const s = document.createElement("span"); s.className = "empty"; s.textContent = "No risky entities found."; box.appendChild(s); }
}

/* ================= In-phone alert + voice ================= */
const VOICE_KEY = "satark-voice";
const voiceEngine = ($("voiceToggle") && $("voiceToggle").dataset.voiceEngine) || "web";
let voiceOn = localStorage.getItem(VOICE_KEY) !== "off";

function stopVoice() {
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    const audio = $("ttsAudio");
    if (audio) {
        audio.pause();
        audio.removeAttribute("src");
        audio.load();
    }
}

function renderVoiceToggle() {
    const btn = $("voiceToggle");
    const label = $("voiceToggleLabel");
    if (!btn || !label) return;
    btn.setAttribute("aria-pressed", voiceOn ? "true" : "false");
    btn.title = voiceOn ? "Turn voice alerts off" : "Turn voice alerts on";
    label.textContent = voiceOn
        ? (voiceEngine === "elevenlabs" ? "🔊 ElevenLabs" : "🔊 Web voice")
        : "🔇 Voice off";
}

function showAlert(r) {
    const el = $("phoneAlert");
    el.classList.remove("hidden");
    const color = colorFor(r.level);
    $("paIcon").textContent = r.level === "SAFE" ? "✅" : r.level === "SUSPICIOUS" ? "⚠️" : "🚨";
    const lvl = $("paLevel"); lvl.textContent = r.level; lvl.style.color = color;
    const rk = $("paRisk"); rk.textContent = r.risk; rk.style.color = color;
    $("paCat").textContent = r.category_label !== "None" ? r.category_label : "No known scam pattern";
    $("paAdvice").textContent = r.advice;
    if (r.level !== "SAFE") speak(`Warning. This looks like a ${r.level === "SCAM" ? "scam" : "suspicious message"}. ${r.advice}`);
}

async function speak(text) {
    if (!voiceOn) return;
    try {
        const res = await fetch("/tts", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });
        if (res.status === 200) {
            const buf = await res.blob();
            const audio = $("ttsAudio");
            audio.src = URL.createObjectURL(buf);
            audio.play().catch(() => {});
            return;
        }
    } catch (e) { /* fall through to web speech */ }
    if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(text);
        u.rate = 1; u.pitch = 1;
        window.speechSynthesis.speak(u);
    }
}

/* ================= Stats + history ================= */
async function refresh() {
    try {
        const [st, hist] = await Promise.all([
            fetch("/stats").then((r) => r.json()),
            fetch("/history").then((r) => r.json()),
        ]);
        renderStats(st); renderHistory(hist.items || []);
    } catch (e) { /* ignore */ }
}
function renderStats(st) {
    $("stScams").textContent = st.scams || 0; $("stSusp").textContent = st.suspicious || 0;
    $("stSafe").textContent = st.safe || 0; $("stTotal").textContent = st.total || 0;
    const box = $("byChannel"); box.innerHTML = "";
    const bc = st.by_channel || {}; const max = Math.max(1, ...Object.values(bc));
    Object.keys(bc).forEach((k) => {
        const row = document.createElement("div"); row.className = "mini-bar";
        row.innerHTML = `<span class="lbl">${CHAN_ICON[k] || ""} ${k}</span>
            <span class="track"><span class="fill" style="width:${(bc[k] / max) * 100}%"></span></span>
            <span class="val">${bc[k]}</span>`;
        box.appendChild(row);
    });
}
function renderHistory(items) {
    const box = $("historyList"); box.innerHTML = "";
    if (!items.length) { box.innerHTML = '<div class="empty">No messages analyzed yet.</div>'; return; }
    items.forEach((it) => {
        const div = document.createElement("div"); div.className = "hist-item " + it.level;
        div.innerHTML = `<div class="hist-top">
                <span class="hist-chan">${CHAN_ICON[it.channel] || ""} ${it.channel}</span>
                <span class="hist-risk ${it.level}">${it.risk} · ${it.level}</span></div>
            <div class="hist-text">${escapeHtml(it.text_preview || "")}</div>`;
        box.appendChild(div);
    });
}

/* ================= Daily report ================= */
async function openReport() {
    $("reportModal").classList.remove("hidden");
    const body = $("reportBody");
    body.innerHTML = '<p class="hint">Loading…</p>';
    try {
        const rep = await fetch("/report/daily").then((r) => r.json());
        let threats = "";
        (rep.threats || []).forEach((t) => {
            threats += `<div class="rep-threat"><div class="rt-top">
                <span>${CHAN_ICON[t.channel] || ""} ${t.channel} · ${escapeHtml(t.sender)}</span>
                <span class="rt-risk" style="color:${t.level === "SCAM" ? "#ff5470" : "#ffb020"}">${t.risk} ${t.level}</span></div>
                <div class="hist-text">${escapeHtml(t.category)} — ${escapeHtml(t.preview)}</div></div>`;
        });
        body.innerHTML = `
            <p class="hint">${rep.date}</p>
            <div class="rep-stats">
                <div class="stat scam"><span>${rep.scams}</span><small>Scams</small></div>
                <div class="stat susp"><span>${rep.suspicious}</span><small>Suspicious</small></div>
                <div class="stat safe"><span>${rep.safe}</span><small>Safe</small></div>
                <div class="stat total"><span>${rep.total}</span><small>Total</small></div>
            </div>
            <div class="rep-section-title">Flagged today</div>
            <div class="rep-threats">${threats || '<p class="hint">No threats flagged yet today. Tap some phone messages to populate this. 🎉</p>'}</div>`;
        $("emailReportBtn").style.display = rep.email_available ? "" : "none";
        $("emailMsg").textContent = rep.email_available ? "" : "Add SMTP_* to .env to enable emailing.";
    } catch (e) { body.innerHTML = '<p class="hint">Failed to load report.</p>'; }
}

/* ================= Helpers ================= */
function colorFor(level) { return level === "SCAM" ? "#ff5470" : level === "SUSPICIOUS" ? "#ffb020" : "#2fd18a"; }
function animateNum(el, target) {
    let cur = 0; const step = Math.max(1, Math.round(target / 24));
    const t = setInterval(() => { cur += step; if (cur >= target) { cur = target; clearInterval(t); } el.textContent = cur; }, 18);
}
function escapeHtml(s) {
    return (s || "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

/* ================= Wiring ================= */
document.querySelectorAll(".chan-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
        document.querySelectorAll(".chan-tab").forEach((t) => t.classList.remove("active"));
        tab.classList.add("active"); channel = tab.dataset.channel;
        $("subjectWrap").classList.toggle("hidden", channel !== "email");
    });
});
document.querySelectorAll(".ios-back").forEach((b) =>
    b.addEventListener("click", () => showView(b.dataset.back)));
$("scanBtn").addEventListener("click", () => analyze(true));
$("playCallBtn").addEventListener("click", () => { if (currentMsg) speak(currentMsg.text); });
$("voiceToggle").addEventListener("click", () => {
    voiceOn = !voiceOn;
    localStorage.setItem(VOICE_KEY, voiceOn ? "on" : "off");
    if (!voiceOn) stopVoice();
    renderVoiceToggle();
});
$("paClose").addEventListener("click", () => { $("phoneAlert").classList.add("hidden"); stopVoice(); });
$("analyzeBtn").addEventListener("click", () => analyze(false));
$("clearBtn").addEventListener("click", () => {
    $("msgInput").value = ""; $("senderInput").value = ""; $("subjectInput").value = "";
    $("resultCard").classList.add("hidden");
});
$("msgInput").addEventListener("keydown", (e) => { if ((e.ctrlKey || e.metaKey) && e.key === "Enter") analyze(false); });
document.querySelectorAll(".fb").forEach((b) => b.addEventListener("click", async () => {
    if (lastId == null) return;
    await fetch("/feedback", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: lastId, label: b.dataset.fb }) });
    $("fbMsg").textContent = "Thanks — feedback saved.";
}));
$("reportBtn").addEventListener("click", openReport);
$("reportClose").addEventListener("click", () => $("reportModal").classList.add("hidden"));
$("emailReportBtn").addEventListener("click", async () => {
    $("emailMsg").textContent = "Sending…";
    try {
        const res = await fetch("/report/email", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) });
        const d = await res.json();
        $("emailMsg").textContent = d.ok ? "✅ Report emailed." : (d.error || "Failed to send.");
    } catch (e) { $("emailMsg").textContent = "Failed to send."; }
});

/* ================= Init ================= */
renderVoiceToggle();
tickClock(); setInterval(tickClock, 10000);
loadPhone();
refresh();
