/**
 * admin.js — KPI cards, canvas bar chart, user management table
 */
let adminPage = 1;

document.addEventListener("pageChanged", ({ detail }) => {
  if (detail.page === "admin") {
    if (App.user?.role !== "admin") { navigateTo("home"); return; }
    loadDashboard();
    loadUsers();
  }
});

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("adminUserSearch")?.addEventListener("input", debounce(() => {
    adminPage = 1; loadUsers();
  }, 400));
});

function debounce(fn, ms) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }

// ── Dashboard ─────────────────────────────────────────────────────────────────
async function loadDashboard() {
  try {
    const data = await apiFetch("/api/admin/stats");
    setKPIs(data.stats);
    drawChart(data.volume_chart);
    drawPairs(data.top_pairs);
  } catch (err) { showToast("Admin error", err.message, "danger"); }
}

function setKPIs(s) {
  if (!s) return;
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
  set("kpiUsers",        s.total_users ?? "—");
  set("kpiUsersSub",     `+${s.new_users_this_week ?? 0} this week`);
  set("kpiTranslations", s.daily_translations ?? "—");
  set("kpiResponseTime", s.avg_response_time ? `${s.avg_response_time}s` : "—");
  set("kpiFailed",       s.failed_translations ?? "—");
}

// ── Bar chart (pure Canvas) ───────────────────────────────────────────────────
function drawChart(data) {
  const canvas = document.getElementById("volumeChart");
  if (!canvas) return;
  const ctx   = canvas.getContext("2d");
  const dark  = document.documentElement.getAttribute("data-theme") === "dark";
  const W     = canvas.parentElement?.clientWidth || 500;
  const H     = 200;
  canvas.width = W; canvas.height = H;
  ctx.clearRect(0, 0, W, H);

  if (!data?.length) {
    ctx.fillStyle = dark ? "#64748b" : "#94a3b8";
    ctx.font = "14px Inter,sans-serif"; ctx.textAlign = "center";
    ctx.fillText("No data yet", W / 2, H / 2); return;
  }

  const counts = data.map(d => d.count);
  const labels = data.map(d => (d._id || "").slice(5));
  const max    = Math.max(...counts, 1);
  const pL = 40, pR = 16, pT = 16, pB = 36;
  const cW = W - pL - pR, cH = H - pT - pB;
  const bW = Math.max(6, (cW / data.length) * 0.55);
  const gap = cW / data.length;

  // Grid
  ctx.strokeStyle = dark ? "#334155" : "#e2e8f0"; ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pT + (cH / 4) * i;
    ctx.beginPath(); ctx.moveTo(pL, y); ctx.lineTo(pL + cW, y); ctx.stroke();
    ctx.fillStyle = dark ? "#64748b" : "#94a3b8";
    ctx.font = "10px Inter,sans-serif"; ctx.textAlign = "right";
    ctx.fillText(Math.round(max - (max / 4) * i), pL - 6, y + 4);
  }

  // Bars
  data.forEach((d, i) => {
    const bH = (d.count / max) * cH;
    const x  = pL + gap * i + gap / 2 - bW / 2;
    const y  = pT + cH - bH;
    const r  = Math.min(4, bW / 2);
    const g  = ctx.createLinearGradient(0, y, 0, y + bH);
    g.addColorStop(0, "#6366f1"); g.addColorStop(1, "#4f46e5");
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.moveTo(x + r, y); ctx.lineTo(x + bW - r, y);
    ctx.quadraticCurveTo(x + bW, y, x + bW, y + r);
    ctx.lineTo(x + bW, y + bH); ctx.lineTo(x, y + bH); ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y); ctx.closePath(); ctx.fill();
    if (i % 2 === 0) {
      ctx.fillStyle = dark ? "#64748b" : "#94a3b8";
      ctx.font = "10px Inter,sans-serif"; ctx.textAlign = "center";
      ctx.fillText(labels[i], x + bW / 2, pT + cH + 18);
    }
  });
}

// ── Top pairs ─────────────────────────────────────────────────────────────────
function drawPairs(pairs) {
  const el = document.getElementById("topPairsList");
  if (!el) return;
  if (!pairs?.length) { el.innerHTML = `<div style="padding:2rem;text-align:center;color:var(--text-tertiary)">No data yet.</div>`; return; }
  const max = pairs[0]?.count || 1;
  el.innerHTML = pairs.map(p => `
    <div style="padding:.75rem 1.5rem;border-bottom:1px solid var(--border)">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.375rem">
        <span style="font-size:.875rem;font-weight:600;color:var(--text-primary)">${escHtml(p.pair)}</span>
        <span style="font-size:.75rem;color:var(--text-tertiary)">${p.count.toLocaleString()}</span>
      </div>
      <div style="height:5px;background:var(--border);border-radius:999px;overflow:hidden">
        <div style="height:100%;width:${Math.round(p.count/max*100)}%;background:linear-gradient(90deg,#6366f1,#4f46e5);border-radius:999px;transition:width .6s ease"></div>
      </div>
    </div>`).join("");
}

// ── Users table ───────────────────────────────────────────────────────────────
async function loadUsers() {
  const tbody = document.getElementById("usersTableBody");
  if (!tbody) return;
  tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:2rem"><div class="spinner"></div></td></tr>`;

  const search = document.getElementById("adminUserSearch")?.value.trim() || "";
  const p = new URLSearchParams({ page: adminPage, per_page: 20 });

  try {
    const data = await apiFetch(`/api/admin/users?${p}`);
    let users = data.users || [];
    if (search) {
      const q = search.toLowerCase();
      users = users.filter(u => u.name?.toLowerCase().includes(q) || u.email?.toLowerCase().includes(q));
    }
    if (!users.length) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:2rem;color:var(--text-tertiary)">No users found.</td></tr>`;
      return;
    }
    tbody.innerHTML = users.map(renderUserRow).join("");
    renderAdminPagination(data.page, data.pages);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:2rem;color:var(--color-danger)">${escHtml(err.message)}</td></tr>`;
  }
}

function renderUserRow(u) {
  const ini = initials(u.name || u.email);
  const statusColor = u.is_active ? "var(--color-success)" : "var(--color-danger)";
  const statusLabel = u.is_active ? "Active" : "Inactive";
  const roleColor   = u.role === "admin" ? "var(--color-primary)" : "var(--text-tertiary)";
  return `
  <tr>
    <td>
      <div style="display:flex;align-items:center;gap:.75rem">
        <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#4f46e5);display:flex;align-items:center;justify-content:center;color:#fff;font-size:.7rem;font-weight:700;flex-shrink:0">${escHtml(ini)}</div>
        <div>
          <div style="font-size:.875rem;font-weight:500;color:var(--text-primary)">${escHtml(u.name||"—")}</div>
          <div style="font-size:.7rem;color:${roleColor};font-weight:600;text-transform:uppercase;letter-spacing:.05em">${u.role}</div>
        </div>
      </div>
    </td>
    <td style="font-size:.8rem;color:var(--text-secondary)">${escHtml(u.email)}</td>
    <td style="font-size:.875rem;color:var(--text-primary)">${(u.translation_count||0).toLocaleString()}</td>
    <td style="font-size:.8rem;color:var(--text-secondary)">${fmtDate(u.created_at)}</td>
    <td><span style="font-size:.75rem;font-weight:600;color:${statusColor};background:${statusColor}20;padding:.2rem .6rem;border-radius:999px">${statusLabel}</span></td>
    <td style="text-align:right">
      <button class="btn btn-ghost btn-sm" onclick="toggleStatus('${u.id}',${!u.is_active})">${u.is_active?"Deactivate":"Activate"}</button>
      ${u.role!=="admin"?`<button class="btn btn-ghost btn-sm" onclick="promoteUser('${u.id}')">Make Admin</button>`:""}
    </td>
  </tr>`;
}

function renderAdminPagination(cur, total) {
  const el = document.getElementById("adminPagination");
  if (!el || total <= 1) { if (el) el.innerHTML = ""; return; }
  let h = `<div style="display:flex;gap:.5rem;justify-content:center;padding:1rem 1.5rem;flex-wrap:wrap">`;
  h += `<button class="btn btn-outline btn-sm" ${cur===1?"disabled":""} onclick="goAdminPage(${cur-1})">‹</button>`;
  for (let i=1;i<=total;i++) {
    if (i===1||i===total||Math.abs(i-cur)<=1)
      h += `<button class="btn btn-sm ${i===cur?"btn-primary":"btn-outline"}" onclick="goAdminPage(${i})">${i}</button>`;
    else if (Math.abs(i-cur)===2) h += `<span style="padding:.375rem .5rem;color:var(--text-tertiary)">…</span>`;
  }
  h += `<button class="btn btn-outline btn-sm" ${cur===total?"disabled":""} onclick="goAdminPage(${cur+1})">›</button></div>`;
  el.innerHTML = h;
}

function goAdminPage(p) { adminPage = p; loadUsers(); }
window.goAdminPage = goAdminPage;

async function toggleStatus(id, active) {
  try {
    await apiFetch(`/api/admin/users/${id}`, { method:"PUT", body: JSON.stringify({ is_active: active }) });
    showToast("Updated", `User ${active?"activated":"deactivated"}.`, "success");
    loadUsers();
  } catch (err) { showToast("Error", err.message, "danger"); }
}

async function promoteUser(id) {
  showConfirm("Promote this user to Admin?", async () => {
    try {
      await apiFetch(`/api/admin/users/${id}`, { method:"PUT", body: JSON.stringify({ role:"admin" }) });
      showToast("Promoted", "User is now an admin.", "success");
      loadUsers();
    } catch (err) { showToast("Error", err.message, "danger"); }
  });
}

window.toggleStatus = toggleStatus;
window.promoteUser  = promoteUser;

// Redraw chart on theme change
new MutationObserver(() => { if (App.currentPage === "admin") loadDashboard(); })
  .observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
