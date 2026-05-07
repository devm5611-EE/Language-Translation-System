# Git Setup Guide

## ✅ Issue Fixed

The Git remote URL has been updated to your account:
- **Old:** `https://github.com/devm5611-EE/Language-Translation-System.git`
- **New:** `https://github.com/abhirajsingh524/Language-Translation-System.git`

---

## 🚀 Next Steps

### 1. Create Repository on GitHub

If you haven't already:
1. Go to [github.com](https://github.com)
2. Click "New repository"
3. Name it: `Language-Translation-System`
4. **Don't** initialize with README (we already have one)
5. Click "Create repository"

### 2. Push Your Code

```bash
# Add all files
git add .

# Commit changes
git commit -m "Initial commit: LinguaFlow AI Translation Application"

# Push to GitHub
git push -u origin main
```

If you get a 403 error, you need to authenticate.

---

## 🔐 Authentication Options

### Option 1: Personal Access Token (Recommended)

1. **Generate Token:**
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Name: `LinguaFlow`
   - Expiration: 90 days (or custom)
   - Scopes: Check `repo` (full control of private repositories)
   - Click "Generate token"
   - **Copy the token** (you won't see it again!)

2. **Use Token:**
   ```bash
   # When prompted for password, use the token instead
   git push -u origin main
   
   # Username: abhirajsingh524
   # Password: <paste-your-token>
   ```

3. **Save Credentials (Optional):**
   ```bash
   # Windows
   git config --global credential.helper wincred
   
   # macOS
   git config --global credential.helper osxkeychain
   
   # Linux
   git config --global credential.helper store
   ```

### Option 2: SSH Key (More Secure)

1. **Generate SSH Key:**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # Press Enter to accept default location
   # Enter passphrase (optional)
   ```

2. **Add SSH Key to GitHub:**
   ```bash
   # Copy public key
   cat ~/.ssh/id_ed25519.pub
   # Or on Windows:
   type %USERPROFILE%\.ssh\id_ed25519.pub
   ```
   
   - Go to GitHub → Settings → SSH and GPG keys
   - Click "New SSH key"
   - Paste the key
   - Click "Add SSH key"

3. **Update Remote URL:**
   ```bash
   git remote set-url origin git@github.com:abhirajsingh524/Language-Translation-System.git
   ```

4. **Push:**
   ```bash
   git push -u origin main
   ```

---

## 📝 Common Git Commands

### Check Status
```bash
git status
```

### Add Files
```bash
# Add all files
git add .

# Add specific file
git add filename.py
```

### Commit Changes
```bash
git commit -m "Your commit message"
```

### Push Changes
```bash
# First time
git push -u origin main

# After that
git push
```

### Pull Changes
```bash
git pull origin main
```

### Check Remote
```bash
git remote -v
```

### View Commit History
```bash
git log --oneline
```

---

## 🔧 Troubleshooting

### Issue: "fatal: not a git repository"
**Solution:**
```bash
git init
git remote add origin https://github.com/abhirajsingh524/Language-Translation-System.git
```

### Issue: "Updates were rejected"
**Solution:**
```bash
# Pull first, then push
git pull origin main --rebase
git push origin main
```

### Issue: "Permission denied (publickey)"
**Solution:** Use HTTPS instead of SSH, or add SSH key to GitHub

### Issue: "Authentication failed"
**Solution:** Use Personal Access Token instead of password

---

## 📦 What to Commit

### Include:
- ✅ Source code (`linguaflow/`)
- ✅ README.md
- ✅ requirements.txt
- ✅ .gitignore
- ✅ Dockerfile
- ✅ docker-compose.yml
- ✅ test_translation.py
- ✅ check_groq_models.py

### Exclude (already in .gitignore):
- ❌ `.env` (contains secrets!)
- ❌ `venv/` or `__pycache__/`
- ❌ `logs/`
- ❌ `.pyc` files

---

## 🎯 Quick Start

```bash
# 1. Check current status
git status

# 2. Add all files
git add .

# 3. Commit
git commit -m "Initial commit: LinguaFlow AI Translation Application"

# 4. Push (will prompt for credentials)
git push -u origin main
```

**When prompted:**
- Username: `abhirajsingh524`
- Password: `<your-personal-access-token>`

---

## ✅ Verification

After pushing, verify on GitHub:
1. Go to `https://github.com/abhirajsingh524/Language-Translation-System`
2. You should see all your files
3. README.md should display automatically

---

## 📞 Need Help?

If you still have issues:
1. Check GitHub status: [githubstatus.com](https://www.githubstatus.com/)
2. Verify your username: `git config user.name`
3. Verify your email: `git config user.email`
4. Check remote URL: `git remote -v`

---

**Last Updated:** May 7, 2026  
**Status:** ✅ Remote URL Updated
