/**
 * auth.js — Login / Register modal forms
 * Handles form submission, API calls, session saving, and redirect to translate page.
 */
document.addEventListener("DOMContentLoaded", () => {
  initLogin();
  initRegister();
});

// ── Login ─────────────────────────────────────────────────────────────────────
function initLogin() {
  const form = document.getElementById("loginForm");
  if (!form) return;

  form.addEventListener("submit", async e => {
    e.preventDefault();

    const email    = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value;
    const errEl    = document.getElementById("loginError");
    const btn      = document.getElementById("btnLoginSubmit");

    // Clear previous error
    setFormError(errEl, "");

    // Client-side validation
    if (!email)    { setFormError(errEl, "Email is required.");    return; }
    if (!password) { setFormError(errEl, "Password is required."); return; }

    setBtnLoading(btn, true);

    try {
      const data = await apiFetch("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      // 1. Save session (updates App.token, App.user, localStorage, nav UI)
      saveSession(data.token, data.user);

      // 2. Close modal
      closeModal("modalLogin");
      form.reset();

      // 3. Navigate to translate dashboard
      //    Use setTimeout so the modal close animation finishes first
      setTimeout(() => {
        showPage("translate");
        showToast("Welcome back!", `Hello, ${data.user.name || data.user.email} 👋`, "success");
      }, 150);

    } catch (err) {
      setFormError(errEl, err.message || "Login failed. Please try again.");
    } finally {
      setBtnLoading(btn, false);
    }
  });
}

// ── Register ──────────────────────────────────────────────────────────────────
function initRegister() {
  const form = document.getElementById("registerForm");
  if (!form) return;

  form.addEventListener("submit", async e => {
    e.preventDefault();

    const name     = document.getElementById("registerName").value.trim();
    const email    = document.getElementById("registerEmail").value.trim();
    const password = document.getElementById("registerPassword").value;
    const confirm  = document.getElementById("registerConfirm").value;
    const errEl    = document.getElementById("registerError");
    const btn      = document.getElementById("btnRegisterSubmit");

    // Clear previous error
    setFormError(errEl, "");

    // Client-side validation
    if (!name)                        { setFormError(errEl, "Full name is required.");                    return; }
    if (!email)                       { setFormError(errEl, "Email is required.");                        return; }
    if (!password)                    { setFormError(errEl, "Password is required.");                     return; }
    if (password.length < 8)          { setFormError(errEl, "Password must be at least 8 characters.");  return; }
    if (!/[A-Z]/.test(password))      { setFormError(errEl, "Password needs at least one uppercase letter."); return; }
    if (!/[0-9]/.test(password))      { setFormError(errEl, "Password needs at least one number.");      return; }
    if (password !== confirm)         { setFormError(errEl, "Passwords do not match.");                   return; }

    setBtnLoading(btn, true);

    try {
      const data = await apiFetch("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({ name, email, password }),
      });

      // 1. Save session
      saveSession(data.token, data.user);

      // 2. Close modal
      closeModal("modalRegister");
      form.reset();

      // 3. Navigate to translate dashboard
      setTimeout(() => {
        showPage("translate");
        showToast("Account created!", `Welcome to LinguaFlow, ${data.user.name}! 🎉`, "success");
      }, 150);

    } catch (err) {
      setFormError(errEl, err.message || "Registration failed. Please try again.");
    } finally {
      setBtnLoading(btn, false);
    }
  });
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function setFormError(el, msg) {
  if (!el) return;
  if (msg) {
    el.textContent = msg;
    el.classList.remove("hidden");
    el.style.display = "block";
  } else {
    el.textContent = "";
    el.classList.add("hidden");
    el.style.display = "none";
  }
}
