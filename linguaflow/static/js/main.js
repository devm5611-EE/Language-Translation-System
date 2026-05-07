/**
 * main.js — Bootstrap, navigation, theme, toasts, API helper
 * Loads first. All other modules depend on globals defined here.
 */

// ── Global state ──────────────────────────────────────────────────────────────
window.App = { token: null, user: null, currentPage: "home", languages: [] };

// ── Boot ──────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  console.log("🚀 LinguaFlow initializing...");
  
  try {
    initTheme();
    console.log("✓ Theme initialized");
    
    restoreSession();   // must run before initNav so auth-required links are correct
    console.log("✓ Session restored");
    
    initNav();
    console.log("✓ Navigation initialized");
    
    initHamburger();
    console.log("✓ Hamburger menu initialized");
    
    bindGlobalButtons();
    console.log("✓ Global buttons bound");
    
    loadLanguages();
    console.log("✓ Languages loading...");
    
    // Show home page properly on first load
    showPage("home");
    console.log("✓ Home page displayed");
    
    console.log("🎉 LinguaFlow ready!");
  } catch (error) {
    console.error("❌ Initialization error:", error);
    // Show error to user
    document.body.innerHTML += `
      <div style="position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:#ef4444;color:#fff;padding:2rem;border-radius:1rem;text-align:center;z-index:9999;max-width:400px;">
        <h2 style="margin:0 0 1rem 0;">⚠️ Initialization Error</h2>
        <p style="margin:0;font-size:0.9rem;">${error.message}</p>
        <button onclick="location.reload()" style="margin-top:1rem;padding:0.5rem 1rem;background:#fff;color:#ef4444;border:none;border-radius:0.5rem;cursor:pointer;font-weight:600;">Reload Page</button>
      </div>
    `;
  }
});

// ── Theme ─────────────────────────────────────────────────────────────────────
function initTheme() {
  const saved = localStorage.getItem("lf_theme") || "light";
  applyTheme(saved);
  document.getElementById("themeToggle")?.addEventListener("click", () => {
    const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    applyTheme(next);
    localStorage.setItem("lf_theme", next);
  });
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const btn = document.getElementById("themeToggle");
  if (btn) btn.textContent = theme === "dark" ? "🌙" : "☀️";
}
window.applyTheme = applyTheme;

// ── Session ───────────────────────────────────────────────────────────────────
function restoreSession() {
  const token = localStorage.getItem("lf_token");
  const user  = JSON.parse(localStorage.getItem("lf_user") || "null");
  if (token && user) {
    App.token = token;
    App.user  = user;
  }
  syncNavUI();
}

function saveSession(token, user) {
  App.token = token;
  App.user  = user;
  localStorage.setItem("lf_token", token);
  localStorage.setItem("lf_user", JSON.stringify(user));
  syncNavUI();
}

function clearSession() {
  App.token = null;
  App.user  = null;
  localStorage.removeItem("lf_token");
  localStorage.removeItem("lf_user");
  syncNavUI();
}

window.saveSession  = saveSession;
window.clearSession = clearSession;

function syncNavUI() {
  const loggedIn = !!App.token;

  // Guest / user nav sections
  document.getElementById("navGuest")?.classList.toggle("hidden", loggedIn);
  document.getElementById("navUser")?.classList.toggle("hidden", !loggedIn);

  // Avatar initials
  const av = document.getElementById("userAvatar");
  if (av && App.user) av.textContent = initials(App.user.name || App.user.email);

  // Show/hide nav links that require auth
  document.querySelectorAll(".auth-required").forEach(el =>
    el.classList.toggle("hidden", !loggedIn)
  );

  // Show/hide admin-only links
  document.querySelectorAll(".admin-only").forEach(el =>
    el.classList.toggle("hidden", !(loggedIn && App.user?.role === "admin"))
  );
}

// ── Page switching (core fix) ─────────────────────────────────────────────────
/**
 * showPage — purely switches which <main> is visible.
 * Does NOT do auth checks. Call navigateTo() for user-triggered navigation.
 */
function showPage(page) {
  console.log(`📄 Showing page: ${page}`);
  
  // Hide all pages
  document.querySelectorAll("main.page").forEach(p => {
    p.style.display = "none";
    p.classList.remove("active");
  });

  // Show target page
  const pageId = "page" + page.charAt(0).toUpperCase() + page.slice(1);
  const target = document.getElementById(pageId);
  
  if (!target) {
    console.error(`❌ Page element not found: ${pageId}`);
    return;
  }
  
  target.style.display = "block";
  target.classList.add("active");
  console.log(`✓ Page ${page} is now visible`);

  App.currentPage = page;

  // Update active nav link
  document.querySelectorAll(".nav-link").forEach(l =>
    l.classList.toggle("active", l.dataset.page === page)
  );

  // Scroll to top — use setTimeout to let the DOM paint first
  setTimeout(() => window.scrollTo({ top: 0, behavior: "instant" }), 0);

  // Notify other modules
  document.dispatchEvent(new CustomEvent("pageChanged", { detail: { page } }));
}

/**
 * navigateTo — auth-guarded navigation called by user interactions.
 */
function navigateTo(page) {
  // Auth guard
  if (["translate", "history", "profile"].includes(page) && !App.token) {
    openModal("modalLogin");
    return;
  }
  if (page === "admin" && App.user?.role !== "admin") {
    showToast("Access denied", "Admin access only.", "danger");
    return;
  }

  closeMobileNav();
  showPage(page);
}

window.navigateTo = navigateTo;
window.showPage   = showPage;

// ── Navigation init ───────────────────────────────────────────────────────────
function initNav() {
  document.querySelectorAll("[data-page]").forEach(el => {
    el.addEventListener("click", e => {
      e.preventDefault();
      navigateTo(el.dataset.page);
    });
  });
}

// ── Hamburger / mobile nav ────────────────────────────────────────────────────
function initHamburger() {
  const btn = document.getElementById("hamburger");
  if (!btn) return;

  let mobileNav = document.getElementById("mobileNav");
  if (!mobileNav) {
    mobileNav = document.createElement("nav");
    mobileNav.id = "mobileNav";
    mobileNav.style.cssText = [
      "display:none",
      "position:fixed",
      "top:64px",
      "left:0",
      "right:0",
      "bottom:0",
      "background:var(--bg-surface)",
      "border-top:1px solid var(--border)",
      "z-index:300",
      "padding:1rem",
      "flex-direction:column",
      "gap:0.25rem",
      "overflow-y:auto",
      "box-shadow:0 20px 40px rgba(0,0,0,.15)",
    ].join(";");

    const linkStyle = "display:flex;align-items:center;gap:.75rem;padding:.75rem 1rem;border-radius:.5rem;font-size:.9rem;font-weight:500;color:var(--text-secondary);text-decoration:none;";
    mobileNav.innerHTML = `
      <a href="#" data-page="home"      style="${linkStyle}">🏠 Home</a>
      <a href="#" data-page="translate" style="${linkStyle}" class="auth-required">🌐 Translate</a>
      <a href="#" data-page="history"   style="${linkStyle}" class="auth-required">📚 History</a>
      <a href="#" data-page="admin"     style="${linkStyle}" class="admin-only">📊 Admin</a>
      <a href="#" data-page="profile"   style="${linkStyle}" class="auth-required">👤 Profile</a>
    `;
    document.body.appendChild(mobileNav);

    mobileNav.querySelectorAll("[data-page]").forEach(el =>
      el.addEventListener("click", e => { e.preventDefault(); navigateTo(el.dataset.page); })
    );
  }

  btn.addEventListener("click", () => {
    const isOpen = mobileNav.style.display !== "flex";
    mobileNav.style.display = isOpen ? "flex" : "none";
    btn.classList.toggle("open", isOpen);
  });
}

function closeMobileNav() {
  const nav = document.getElementById("mobileNav");
  if (nav) nav.style.display = "none";
  document.getElementById("hamburger")?.classList.remove("open");
}

// ── Global buttons ────────────────────────────────────────────────────────────
function bindGlobalButtons() {
  document.getElementById("btnHeroStart")?.addEventListener("click", () =>
    App.token ? navigateTo("translate") : openModal("modalLogin")
  );
  document.getElementById("btnHeroRegister")?.addEventListener("click", () =>
    openModal("modalRegister")
  );
  document.getElementById("btnCtaStart")?.addEventListener("click", () =>
    App.token ? navigateTo("translate") : openModal("modalRegister")
  );
  document.getElementById("btnNavLogin")?.addEventListener("click", () =>
    openModal("modalLogin")
  );
  document.getElementById("btnNavRegister")?.addEventListener("click", () =>
    openModal("modalRegister")
  );
  document.getElementById("btnLogout")?.addEventListener("click", doLogout);
}

async function doLogout() {
  try { await apiFetch("/api/auth/logout", { method: "POST" }); } catch (_) {}
  clearSession();
  showPage("home");
  showToast("Logged out", "See you next time!", "success");
}

// ── Modals ────────────────────────────────────────────────────────────────────
function openModal(id) {
  const el = document.getElementById(id);
  if (!el) return;

  // Remove hidden, show as flex
  el.classList.remove("hidden");
  el.style.display = "flex";

  // Focus first input after transition
  setTimeout(() => el.querySelector("input")?.focus(), 100);

  // Close on backdrop click (the overlay itself, not the modal card)
  const onBackdrop = e => {
    if (e.target === el) {
      closeModal(id);
      el.removeEventListener("click", onBackdrop);
    }
  };
  el.addEventListener("click", onBackdrop);
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.style.display = "none";
  el.classList.add("hidden");
}

window.openModal  = openModal;
window.closeModal = closeModal;
window.showModal  = openModal;   // alias
window.hideModal  = closeModal;  // alias

// Modal close buttons & switchers
document.addEventListener("click", e => {
  const id = e.target.id;
  if (id === "closeLogin")       closeModal("modalLogin");
  if (id === "closeRegister")    closeModal("modalRegister");
  if (id === "switchToRegister") { closeModal("modalLogin");    openModal("modalRegister"); }
  if (id === "switchToLogin")    { closeModal("modalRegister"); openModal("modalLogin"); }
});

document.addEventListener("keydown", e => {
  if (e.key === "Escape") {
    ["modalLogin", "modalRegister", "modalConfirm"].forEach(closeModal);
  }
});

// ── Confirm dialog ────────────────────────────────────────────────────────────
function showConfirm(message, onOk) {
  const msgEl = document.getElementById("confirmMessage");
  if (msgEl) msgEl.textContent = message;
  openModal("modalConfirm");

  const okBtn  = document.getElementById("btnConfirmOk");
  const canBtn = document.getElementById("btnConfirmCancel");

  const cleanup = () => {
    closeModal("modalConfirm");
    okBtn.removeEventListener("click",  yes);
    canBtn.removeEventListener("click", no);
  };
  const yes = () => { cleanup(); onOk(); };
  const no  = () => cleanup();

  okBtn.addEventListener("click",  yes, { once: true });
  canBtn.addEventListener("click", no,  { once: true });
}
window.showConfirm = showConfirm;

// ── Toast notifications ───────────────────────────────────────────────────────
const TOAST_ICONS = { success: "✅", danger: "❌", warning: "⚠️", info: "ℹ️" };

function showToast(title, message = "", type = "info", duration = 4500) {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const t = document.createElement("div");
  t.style.cssText = [
    "display:flex",
    "align-items:flex-start",
    "gap:.75rem",
    "padding:1rem 1.25rem",
    "background:var(--bg-surface)",
    "border:1px solid var(--border)",
    "border-radius:1rem",
    "box-shadow:0 10px 40px rgba(0,0,0,.15)",
    "margin-bottom:.5rem",
    "transform:translateX(110%)",
    "opacity:0",
    "transition:transform .35s cubic-bezier(.34,1.56,.64,1), opacity .2s ease",
    "max-width:360px",
    "width:100%",
    "position:relative",
    "overflow:hidden",
  ].join(";");

  // Colored left accent bar
  const accentColors = { success: "#10b981", danger: "#ef4444", warning: "#f59e0b", info: "#3b82f6" };
  const accent = accentColors[type] || accentColors.info;

  t.innerHTML = `
    <div style="position:absolute;left:0;top:0;bottom:0;width:4px;background:${accent};border-radius:1rem 0 0 1rem"></div>
    <span style="font-size:1.1rem;flex-shrink:0;margin-top:1px;margin-left:8px">${TOAST_ICONS[type] || "ℹ️"}</span>
    <div style="flex:1;min-width:0">
      <div style="font-size:.875rem;font-weight:600;color:var(--text-primary);margin-bottom:2px">${escHtml(title)}</div>
      ${message ? `<div style="font-size:.8rem;color:var(--text-secondary);line-height:1.4">${escHtml(message)}</div>` : ""}
    </div>
    <button style="font-size:.8rem;color:var(--text-tertiary);background:none;border:none;cursor:pointer;padding:0 0 0 .5rem;flex-shrink:0;line-height:1" aria-label="Dismiss">✕</button>
  `;

  container.appendChild(t);

  // Animate in
  requestAnimationFrame(() => requestAnimationFrame(() => {
    t.style.transform = "translateX(0)";
    t.style.opacity   = "1";
  }));

  // Auto dismiss
  const dismiss = () => {
    t.style.transform = "translateX(110%)";
    t.style.opacity   = "0";
    setTimeout(() => t.remove(), 350);
  };

  const timer = setTimeout(dismiss, duration);
  t.querySelector("button").addEventListener("click", () => { clearTimeout(timer); dismiss(); });
}
window.showToast = showToast;

// ── API helper with timeout ───────────────────────────────────────────────────
async function apiFetch(url, opts = {}, timeout = 30000) {
  const headers = {
    "Content-Type": "application/json",
    ...(App.token ? { Authorization: `Bearer ${App.token}` } : {}),
    ...(opts.headers || {}),
  };

  // Create abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  let res, data;
  try {
    res  = await fetch(url, { ...opts, headers, signal: controller.signal });
    clearTimeout(timeoutId);
    
    // Try to parse JSON
    try {
      data = await res.json();
    } catch (parseErr) {
      throw new Error(`Invalid server response: ${res.status}`);
    }
  } catch (networkErr) {
    clearTimeout(timeoutId);
    
    // Handle timeout
    if (networkErr.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeout/1000}s - server not responding`);
    }
    
    throw new Error("Network error — is the server running?");
  }

  if (!res.ok) {
    throw Object.assign(
      new Error(data?.error || `Server error (${res.status})`),
      { status: res.status, data }
    );
  }
  return data;
}
window.apiFetch = apiFetch;

// ── Languages ─────────────────────────────────────────────────────────────────
async function loadLanguages() {
  try {
    const data = await apiFetch("/api/languages");
    App.languages = data.languages || [];
  } catch (_) {
    // Fallback list if API not ready yet
    App.languages = [
      { code: "en", name: "English" },   { code: "fr", name: "French" },
      { code: "es", name: "Spanish" },   { code: "de", name: "German" },
      { code: "zh", name: "Chinese" },   { code: "ja", name: "Japanese" },
      { code: "ar", name: "Arabic" },    { code: "pt", name: "Portuguese" },
      { code: "ru", name: "Russian" },   { code: "hi", name: "Hindi" },
      { code: "it", name: "Italian" },   { code: "ko", name: "Korean" },
      { code: "tr", name: "Turkish" },   { code: "nl", name: "Dutch" },
      { code: "pl", name: "Polish" },    { code: "sv", name: "Swedish" },
      { code: "uk", name: "Ukrainian" }, { code: "vi", name: "Vietnamese" },
      { code: "th", name: "Thai" },      { code: "id", name: "Indonesian" },
    ];
  }
  document.dispatchEvent(new CustomEvent("languagesLoaded", { detail: App.languages }));
}

function populateLangSelect(sel, includeAuto = false) {
  if (!sel) return;
  const prev = sel.value;
  sel.innerHTML = "";
  if (includeAuto) {
    const o = document.createElement("option");
    o.value = "auto"; o.textContent = "🔍 Auto Detect";
    sel.appendChild(o);
  }
  App.languages.forEach(({ code, name }) => {
    const o = document.createElement("option");
    o.value = code; o.textContent = name;
    sel.appendChild(o);
  });
  // Restore previous selection
  if (prev && sel.querySelector(`option[value="${prev}"]`)) sel.value = prev;
}
window.populateLangSelect = populateLangSelect;

// ── Utilities ─────────────────────────────────────────────────────────────────
function escHtml(s) {
  const d = document.createElement("div");
  d.textContent = String(s ?? "");
  return d.innerHTML;
}

function initials(name) {
  if (!name) return "?";
  return name.trim().split(/\s+/).map(w => w[0]).join("").toUpperCase().slice(0, 2);
}

function fmtDate(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  } catch { return iso; }
}

function fmtRelative(iso) {
  if (!iso) return "—";
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1)  return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  if (d < 7)  return `${d}d ago`;
  return fmtDate(iso);
}

function setBtnLoading(btn, on) {
  if (!btn) return;
  if (on) {
    btn._origText = btn.textContent;
    btn.classList.add("loading");
    btn.disabled = true;
  } else {
    btn.classList.remove("loading");
    btn.disabled = false;
    if (btn._origText !== undefined) btn.textContent = btn._origText;
  }
}

// Expose with all aliases other modules use
window.escHtml            = escHtml;
window.escapeHtml         = escHtml;
window.initials           = initials;
window.getInitials        = initials;
window.fmtDate            = fmtDate;
window.formatDate         = fmtDate;
window.fmtRelative        = fmtRelative;
window.formatRelativeTime = fmtRelative;
window.setBtnLoading      = setBtnLoading;
window.setButtonLoading   = setBtnLoading;
