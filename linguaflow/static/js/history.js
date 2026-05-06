/**
 * history.js — History list, search/filter, pagination, delete/reuse
 */
let hPage = 1;
let hFilters = { search: "", lang: "", sort: "newest" };
let hDebounce = null;

document.addEventListener("DOMContentLoaded", initHistory);
document.addEventListener("pageChanged", ({ detail }) => {
  if (detail.page === "history") { hPage = 1; loadHistory(); fillLangFilter(); }
});

function initHistory() {
  document.getElementById("historySearch")?.addEventListener("input", e => {
    clearTimeout(hDebounce);
    hDebounce = setTimeout(() => { hFilters.search = e.target.value.trim(); hPage = 1; loadHistory(); }, 400);
  });
  document.getElementById("historyLangFilter")?.addEventListener("change", e => {
    hFilters.lang = e.target.value; hPage = 1; loadHistory();
  });
  document.getElementById("historySortFilter")?.addEventListener("change", e => {
    hFilters.sort = e.target.value; hPage = 1; loadHistory();
  });
  document.getElementById("btnClearHistory")?.addEventListener("click", () =>
    showConfirm("Delete ALL translation history? This cannot be undone.", clearAll)
  );
}

async function loadHistory() {
  if (!App.token) return;
  const el = document.getElementById("historyList");
  if (!el) return;
  el.innerHTML = `<div style="text-align:center;padding:3rem"><div class="spinner"></div><p style="margin-top:1rem;color:var(--text-tertiary)">Loading…</p></div>`;

  const p = new URLSearchParams({ page: hPage, per_page: 15, sort: hFilters.sort });
  if (hFilters.search) p.set("search", hFilters.search);
  if (hFilters.lang)   p.set("target_lang", hFilters.lang);

  try {
    const data = await apiFetch(`/api/history?${p}`);
    if (!data.items?.length) {
      el.innerHTML = `<div style="text-align:center;padding:4rem;color:var(--text-tertiary)">
        <div style="font-size:3rem;margin-bottom:1rem">📭</div>
        <div style="font-size:1.1rem;font-weight:600;color:var(--text-primary);margin-bottom:.5rem">No translations found</div>
        <div>${hFilters.search || hFilters.lang ? "Try adjusting your filters." : "Start translating to build your history."}</div>
      </div>`;
      document.getElementById("historyPagination").innerHTML = "";
      return;
    }
    el.innerHTML = data.items.map(renderCard).join("");
    renderPagination(data.page, data.pages);
  } catch (err) {
    el.innerHTML = `<div style="text-align:center;padding:3rem;color:var(--color-danger)">⚠️ ${escHtml(err.message)}</div>`;
  }
}

function renderCard(t) {
  const pct = Math.round((t.confidence || 0) * 100);
  const badgeColor = pct >= 80 ? "var(--color-success)" : pct >= 60 ? "var(--color-warning)" : "var(--color-danger)";
  return `
  <div class="history-card" id="hc-${t.id}">
    <div class="history-card-header">
      <span class="badge">${t.source_lang.toUpperCase()} → ${t.target_lang.toUpperCase()}</span>
      <span class="badge" style="background:${badgeColor}20;color:${badgeColor}">${pct}%</span>
      <span class="badge" style="background:var(--bg-surface-2);color:var(--text-tertiary)">${escHtml((t.model_used||"").split("-")[0])}</span>
      <span style="font-size:.75rem;color:var(--text-tertiary);margin-left:auto">${fmtRelative(t.created_at)}</span>
    </div>
    <div class="history-card-body">
      <div class="history-text">${escHtml(t.source_text)}</div>
      <div class="history-text" style="color:var(--color-primary)">${escHtml(t.translated_text)}</div>
    </div>
    <div class="history-card-actions">
      <button class="btn btn-ghost btn-sm" onclick="reuseItem('${t.id}','${escHtml(t.source_text).replace(/'/g,"\\'")}','${t.source_lang}','${t.target_lang}')">↩ Reuse</button>
      <button class="btn btn-ghost btn-sm" onclick="copyItem('${escHtml(t.translated_text).replace(/'/g,"\\'")}')">📋 Copy</button>
      <button class="btn btn-ghost btn-sm" style="color:var(--color-danger)" onclick="deleteItem('${t.id}')">🗑 Delete</button>
      <span style="font-size:.7rem;color:var(--text-tertiary);margin-left:auto">${t.char_count} chars · ${t.response_time_ms}ms</span>
    </div>
  </div>`;
}

function renderPagination(cur, total) {
  const el = document.getElementById("historyPagination");
  if (!el || total <= 1) { if (el) el.innerHTML = ""; return; }
  let h = `<div style="display:flex;gap:.5rem;justify-content:center;padding:1.5rem 0;flex-wrap:wrap">`;
  h += `<button class="btn btn-outline btn-sm" ${cur===1?"disabled":""} onclick="goPage(${cur-1})">‹ Prev</button>`;
  for (let i = 1; i <= total; i++) {
    if (i===1||i===total||Math.abs(i-cur)<=1)
      h += `<button class="btn btn-sm ${i===cur?"btn-primary":"btn-outline"}" onclick="goPage(${i})">${i}</button>`;
    else if (Math.abs(i-cur)===2) h += `<span style="padding:.375rem .5rem;color:var(--text-tertiary)">…</span>`;
  }
  h += `<button class="btn btn-outline btn-sm" ${cur===total?"disabled":""} onclick="goPage(${cur+1})">Next ›</button>`;
  h += "</div>";
  el.innerHTML = h;
}

function goPage(p) { hPage = p; loadHistory(); }
window.goPage = goPage;

function reuseItem(id, text, sl, tl) { navigateTo("translate"); setTimeout(() => reuseTranslation(text, sl, tl), 150); }
async function copyItem(text) {
  try { await navigator.clipboard.writeText(text); showToast("Copied!", "", "success"); }
  catch { showToast("Copy failed", "", "danger"); }
}
async function deleteItem(id) {
  showConfirm("Delete this translation?", async () => {
    try {
      await apiFetch(`/api/history/${id}`, { method: "DELETE" });
      document.getElementById(`hc-${id}`)?.remove();
      showToast("Deleted", "", "success");
    } catch (err) { showToast("Error", err.message, "danger"); }
  });
}
async function clearAll() {
  try {
    const d = await apiFetch("/api/history", { method: "DELETE" });
    showToast("Cleared", d.message || "", "success");
    loadHistory();
  } catch (err) { showToast("Error", err.message, "danger"); }
}

window.reuseItem  = reuseItem;
window.copyItem   = copyItem;
window.deleteItem = deleteItem;

function fillLangFilter() {
  const sel = document.getElementById("historyLangFilter");
  if (!sel || sel.options.length > 1) return;
  App.languages.forEach(({ code, name }) => {
    const o = document.createElement("option"); o.value = code; o.textContent = name; sel.appendChild(o);
  });
}
