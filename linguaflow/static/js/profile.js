/**
 * profile.js — Profile form, preferences, danger zone
 */
document.addEventListener("DOMContentLoaded", initProfile);
document.addEventListener("pageChanged", ({ detail }) => { if (detail.page === "profile") loadProfile(); });

function initProfile() {
  document.getElementById("profileForm")?.addEventListener("submit", saveProfile);
  document.getElementById("btnDeleteAccount")?.addEventListener("click", () =>
    showConfirm("Permanently delete your account and ALL data? This cannot be undone.", deleteAccount)
  );
  ["prefDarkMode","prefAutoDetect","prefSaveHistory","prefEmailNotif"].forEach(id =>
    document.getElementById(id)?.addEventListener("change", savePrefs)
  );
}

async function loadProfile() {
  if (!App.token) return;
  try {
    const u = await apiFetch("/api/profile");
    App.user = u; localStorage.setItem("lf_user", JSON.stringify(u));

    const set = (id, v) => { const el = document.getElementById(id); if (el) el.value = v || ""; };
    set("profileNameInput",  u.name);
    set("profileEmailInput", u.email);

    const av = document.getElementById("profileAvatar");
    const nm = document.getElementById("profileName");
    const em = document.getElementById("profileEmail");
    if (av) av.textContent = initials(u.name || u.email);
    if (nm) nm.textContent = u.name || "—";
    if (em) em.textContent = u.email || "—";

    const prefs = u.preferences || {};
    const chk = (id, v) => { const el = document.getElementById(id); if (el) el.checked = !!v; };
    chk("prefDarkMode",    prefs.dark_mode);
    chk("prefAutoDetect",  prefs.auto_detect !== false);
    chk("prefSaveHistory", prefs.save_history !== false);
    chk("prefEmailNotif",  prefs.email_notifications !== false);

    if (prefs.dark_mode !== undefined) {
      const theme = prefs.dark_mode ? "dark" : "light";
      applyTheme(theme); localStorage.setItem("lf_theme", theme);
    }
  } catch (err) { showToast("Error", "Could not load profile.", "danger"); }
}

async function saveProfile(e) {
  e.preventDefault();
  const errEl = document.getElementById("profileError");
  const btn   = e.target.querySelector('[type="submit"]');
  errEl?.classList.add("hidden");

  const updates = {};
  const name  = document.getElementById("profileNameInput")?.value.trim();
  const email = document.getElementById("profileEmailInput")?.value.trim();
  const pw    = document.getElementById("profilePasswordInput")?.value;
  if (name)  updates.name     = name;
  if (email) updates.email    = email;
  if (pw)    updates.password = pw;

  if (!Object.keys(updates).length) {
    if (errEl) { errEl.textContent = "No changes to save."; errEl.classList.remove("hidden"); }
    return;
  }

  setBtnLoading(btn, true);
  try {
    const u = await apiFetch("/api/profile", { method: "PUT", body: JSON.stringify(updates) });
    App.user = u; localStorage.setItem("lf_user", JSON.stringify(u));
    const pwEl = document.getElementById("profilePasswordInput");
    if (pwEl) pwEl.value = "";
    const av = document.getElementById("userAvatar");
    if (av) av.textContent = initials(u.name || u.email);
    showToast("Saved!", "Profile updated.", "success");
  } catch (err) {
    if (errEl) { errEl.textContent = err.message; errEl.classList.remove("hidden"); }
  } finally { setBtnLoading(btn, false); }
}

async function savePrefs() {
  const prefs = {
    dark_mode:           document.getElementById("prefDarkMode")?.checked    || false,
    auto_detect:         document.getElementById("prefAutoDetect")?.checked  !== false,
    save_history:        document.getElementById("prefSaveHistory")?.checked !== false,
    email_notifications: document.getElementById("prefEmailNotif")?.checked  !== false,
  };
  applyTheme(prefs.dark_mode ? "dark" : "light");
  localStorage.setItem("lf_theme", prefs.dark_mode ? "dark" : "light");
  try {
    await apiFetch("/api/profile", { method: "PUT", body: JSON.stringify({ preferences: prefs }) });
    showToast("Preferences saved", "", "success");
  } catch { showToast("Error", "Could not save preferences.", "danger"); }
}

async function deleteAccount() {
  try {
    await apiFetch("/api/profile", { method: "DELETE" });
    clearSession(); navigateTo("home");
    showToast("Account deleted", "Your account has been removed.", "info");
  } catch (err) { showToast("Error", err.message, "danger"); }
}
