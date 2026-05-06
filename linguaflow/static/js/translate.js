/**
 * translate.js — Translation UI, speech I/O, cache indicator
 */
let _mic = null;
let _speaking = false;

document.addEventListener("DOMContentLoaded", initTranslate);

document.addEventListener("languagesLoaded", () => {
  populateLangSelect(document.getElementById("sourceLangSelect"), true);
  populateLangSelect(document.getElementById("targetLangSelect"), false);
  const t = document.getElementById("targetLangSelect");
  if (t) t.value = "fr";
});

document.addEventListener("pageChanged", ({ detail }) => {
  if (detail.page === "translate") { loadStats(); loadRecent(); }
});

// ── Init ──────────────────────────────────────────────────────────────────────
function initTranslate() {
  const src = document.getElementById("sourceText");
  src?.addEventListener("input", () => {
    const n = src.value.length;
    const el = document.getElementById("charCount");
    if (el) el.textContent = n;
    el?.parentElement?.classList.toggle("warn", n > 4500);
  });
  src?.addEventListener("keydown", e => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); doTranslate(); }
  });

  document.getElementById("btnTranslate")?.addEventListener("click",    doTranslate);
  document.getElementById("btnSwapLangs")?.addEventListener("click",    swapLangs);
  document.getElementById("btnClearSource")?.addEventListener("click",  clearSrc);
  document.getElementById("btnCopyResult")?.addEventListener("click",   copyResult);
  document.getElementById("btnSpeakResult")?.addEventListener("click",  speakResult);
  document.getElementById("btnDownloadResult")?.addEventListener("click", downloadResult);
  document.getElementById("btnShareResult")?.addEventListener("click",  shareResult);
  document.getElementById("btnMic")?.addEventListener("click",          startMic);
  document.getElementById("btnStopMic")?.addEventListener("click",      stopMic);
}

// ── Translate ─────────────────────────────────────────────────────────────────
async function doTranslate() {
  if (!App.token) { openModal("modalLogin"); return; }

  const text       = document.getElementById("sourceText")?.value.trim();
  const sourceLang = document.getElementById("sourceLangSelect")?.value || "auto";
  const targetLang = document.getElementById("targetLangSelect")?.value;
  const model      = document.getElementById("modelSelect")?.value || "llama3-70b-8192";
  const btn        = document.getElementById("btnTranslate");

  if (!text)       { showToast("Empty text",        "Enter some text first.",          "warning"); return; }
  if (!targetLang) { showToast("No target language","Select a target language.",        "warning"); return; }

  setBtnLoading(btn, true);
  setLoading(true);
  setCacheStatus("loading");

  try {
    const res = await apiFetch("/api/translate", {
      method: "POST",
      body: JSON.stringify({ text, source_lang: sourceLang, target_lang: targetLang, model }),
    });
    showResult(res);
    setCacheStatus(res.cache_hit ? "hit" : "miss");
    loadStats();
    loadRecent();
  } catch (err) {
    showToast("Translation failed", err.message, "danger");
    setCacheStatus("error");
  } finally {
    setBtnLoading(btn, false);
    setLoading(false);
  }
}

function showResult(res) {
  const el = document.getElementById("translateResult");
  if (el) el.innerHTML = `<span>${escHtml(res.translation)}</span>`;

  const pct = Math.round((res.confidence || 0) * 100);
  const cv  = document.getElementById("confidenceValue");
  const cb  = document.getElementById("confidenceBar");
  if (cv) cv.textContent = `${pct}%`;
  if (cb) {
    cb.style.width = `${pct}%`;
    cb.style.background = pct >= 80 ? "linear-gradient(90deg,#6366f1,#10b981)"
                        : pct >= 60 ? "linear-gradient(90deg,#f59e0b,#6366f1)"
                        :             "linear-gradient(90deg,#ef4444,#f59e0b)";
  }
  // Update auto-detect label
  if (res.source_lang && res.source_lang !== "unknown") {
    const opt = document.querySelector('#sourceLangSelect option[value="auto"]');
    if (opt) opt.textContent = `🔍 Auto (${res.source_lang.toUpperCase()})`;
  }
}

function setLoading(on) {
  document.getElementById("translateLoading")?.classList.toggle("hidden", !on);
}

// ── Cache badge ───────────────────────────────────────────────────────────────
function setCacheStatus(s) {
  const badge = document.getElementById("cacheBadge");
  const text  = document.getElementById("cacheStatus");
  if (!badge || !text) return;
  const map = {
    hit:     { label: "🟢 Cache hit",   color: "#10b981" },
    miss:    { label: "🔴 Cache miss",  color: "#ef4444" },
    loading: { label: "⏳ Translating…", color: "#f59e0b" },
    error:   { label: "❌ Error",        color: "#ef4444" },
    ready:   { label: "Ready",           color: "#94a3b8" },
  };
  const m = map[s] || map.ready;
  text.textContent = m.label;
  const dot = badge.querySelector(".cache-dot");
  if (dot) dot.style.background = m.color;
}

// ── Swap ──────────────────────────────────────────────────────────────────────
function swapLangs() {
  const srcSel = document.getElementById("sourceLangSelect");
  const tgtSel = document.getElementById("targetLangSelect");
  const srcTxt = document.getElementById("sourceText");
  const resTxt = document.getElementById("translateResult");

  const sv = srcSel?.value === "auto" ? "" : srcSel?.value;
  const tv = tgtSel?.value;
  if (sv && tgtSel) tgtSel.value = sv;
  if (tv && srcSel) srcSel.value = tv;

  const resultText = resTxt?.querySelector("span")?.textContent || "";
  if (resultText && srcTxt) {
    srcTxt.value = resultText;
    srcTxt.dispatchEvent(new Event("input"));
    if (resTxt) resTxt.innerHTML = `<span class="result-placeholder">Translation will appear here...</span>`;
  }
}

// ── Clear ─────────────────────────────────────────────────────────────────────
function clearSrc() {
  const src = document.getElementById("sourceText");
  if (src) { src.value = ""; src.dispatchEvent(new Event("input")); src.focus(); }
  const res = document.getElementById("translateResult");
  if (res) res.innerHTML = `<span class="result-placeholder">Translation will appear here...</span>`;
  const cv = document.getElementById("confidenceValue");
  const cb = document.getElementById("confidenceBar");
  if (cv) cv.textContent = "—";
  if (cb) cb.style.width = "0%";
  setCacheStatus("ready");
}

// ── Copy ──────────────────────────────────────────────────────────────────────
async function copyResult() {
  const text = document.getElementById("translateResult")?.querySelector("span:not(.result-placeholder)")?.textContent;
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    const btn = document.getElementById("btnCopyResult");
    if (btn) { const orig = btn.textContent; btn.textContent = "✅"; setTimeout(() => btn.textContent = orig, 2000); }
    showToast("Copied!", "", "success");
  } catch { showToast("Copy failed", "", "danger"); }
}

// ── Speak ─────────────────────────────────────────────────────────────────────
function speakResult() {
  if (!window.speechSynthesis) { showToast("Not supported", "TTS unavailable.", "warning"); return; }
  const text = document.getElementById("translateResult")?.querySelector("span:not(.result-placeholder)")?.textContent;
  const lang = document.getElementById("targetLangSelect")?.value || "en";
  if (!text) return;
  if (_speaking) { speechSynthesis.cancel(); _speaking = false; return; }
  const u = new SpeechSynthesisUtterance(text);
  u.lang = lang; u.rate = 0.9;
  u.onstart = () => _speaking = true;
  u.onend = u.onerror = () => _speaking = false;
  speechSynthesis.speak(u);
}

// ── Download ──────────────────────────────────────────────────────────────────
function downloadResult() {
  const src  = document.getElementById("sourceText")?.value || "";
  const res  = document.getElementById("translateResult")?.querySelector("span:not(.result-placeholder)")?.textContent || "";
  const sl   = document.getElementById("sourceLangSelect")?.value || "auto";
  const tl   = document.getElementById("targetLangSelect")?.value || "en";
  if (!res) return;
  const blob = new Blob([`LinguaFlow Translation\n${"=".repeat(40)}\nSource (${sl}):\n${src}\n\nTranslation (${tl}):\n${res}\n\nDate: ${new Date().toLocaleString()}`], { type: "text/plain" });
  const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: `translation_${tl}_${Date.now()}.txt` });
  a.click(); URL.revokeObjectURL(a.href);
}

// ── Share ─────────────────────────────────────────────────────────────────────
async function shareResult() {
  const text = document.getElementById("translateResult")?.querySelector("span:not(.result-placeholder)")?.textContent;
  if (!text) return;
  if (navigator.share) { try { await navigator.share({ title: "LinguaFlow", text }); } catch (_) {} }
  else { await copyResult(); }
}

// ── Mic ───────────────────────────────────────────────────────────────────────
function startMic() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { showToast("Not supported", "Speech recognition unavailable.", "warning"); return; }
  _mic = new SR();
  _mic.continuous = false; _mic.interimResults = true;
  _mic.lang = document.getElementById("sourceLangSelect")?.value || "en";
  _mic.onresult = e => {
    const t = Array.from(e.results).map(r => r[0].transcript).join("");
    const src = document.getElementById("sourceText");
    if (src) { src.value = t; src.dispatchEvent(new Event("input")); }
  };
  _mic.onend = stopMic;
  _mic.onerror = e => { showToast("Mic error", e.error, "danger"); stopMic(); };
  _mic.start();
  document.getElementById("btnMic")?.classList.add("hidden");
  document.getElementById("btnStopMic")?.classList.remove("hidden");
  showToast("Listening…", "Speak now.", "info", 3000);
}

function stopMic() {
  _mic?.stop(); _mic = null;
  document.getElementById("btnMic")?.classList.remove("hidden");
  document.getElementById("btnStopMic")?.classList.add("hidden");
}

// ── Stats ─────────────────────────────────────────────────────────────────────
async function loadStats() {
  if (!App.token) return;
  try {
    const s = await apiFetch("/api/history/stats");
    const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
    set("statToday",        s.count ?? 0);
    set("statConfidence",   s.avg_confidence ? `${s.avg_confidence}%` : "—");
    set("statResponseTime", s.last_response_time || "—");
    set("statChars",        s.total_chars ?? 0);
  } catch (_) {}
}

// ── Recent ────────────────────────────────────────────────────────────────────
async function loadRecent() {
  if (!App.token) return;
  const el = document.getElementById("recentList");
  if (!el) return;
  try {
    const data = await apiFetch("/api/history?per_page=3");
    if (!data.items?.length) {
      el.innerHTML = `<div style="text-align:center;padding:2rem;color:var(--text-tertiary)">📝 No translations yet.</div>`;
      return;
    }
    el.innerHTML = data.items.map(t => `
      <div class="history-card" onclick="reuseTranslation('${escHtml(t.source_text).replace(/'/g,"\\'")}','${t.source_lang}','${t.target_lang}')" style="cursor:pointer">
        <div class="history-card-header">
          <span class="badge">${t.source_lang.toUpperCase()} → ${t.target_lang.toUpperCase()}</span>
          <span class="badge badge-success">${Math.round(t.confidence*100)}%</span>
          <span style="font-size:.75rem;color:var(--text-tertiary);margin-left:auto">${fmtRelative(t.created_at)}</span>
        </div>
        <div class="history-card-body">
          <div class="history-text">${escHtml(t.source_text)}</div>
          <div class="history-text" style="color:var(--color-primary)">${escHtml(t.translated_text)}</div>
        </div>
      </div>`).join("");
  } catch (_) {}
}

function reuseTranslation(text, sl, tl) {
  const src = document.getElementById("sourceText");
  const ss  = document.getElementById("sourceLangSelect");
  const ts  = document.getElementById("targetLangSelect");
  if (src) { src.value = text; src.dispatchEvent(new Event("input")); }
  if (ss && sl !== "unknown") ss.value = sl;
  if (ts) ts.value = tl;
}
window.reuseTranslation = reuseTranslation;
