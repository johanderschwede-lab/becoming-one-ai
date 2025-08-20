# 🔒 SECURE GITHUB TOKEN SETUP GUIDE

## ⚠️ NEVER SHARE TOKENS IN CHAT, FILES, OR COMMITS!

### Step 1: Generate New Token Securely
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token with these permissions:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
3. **COPY TOKEN IMMEDIATELY** - you won't see it again

### Step 2: Configure Git Securely (DO THIS IN TERMINAL)
```bash
# Remove any existing remote with embedded token
git remote remove origin

# Add remote with your username only (no token)
git remote add origin https://github.com/johanderschwede-lab/becoming-one-ai.git

# Configure git to use credential helper (will prompt for token)
git config credential.helper store

# OR use SSH instead (recommended)
git remote set-url origin git@github.com:johanderschwede-lab/becoming-one-ai.git
```

### Step 3: Test Push Securely
```bash
# When you push, git will prompt for credentials
# Username: your-github-username
# Password: paste-your-token-here (NOT in chat!)
git push origin main
```

### Step 4: Configure Railway
1. Go to Railway dashboard
2. Connect your GitHub repo
3. Railway will handle GitHub authentication automatically

## 🔒 SECURITY RULES GOING FORWARD:

1. **NEVER** share tokens in chat messages
2. **NEVER** commit tokens to git
3. **ALWAYS** use environment variables for secrets
4. **ALWAYS** add sensitive files to .gitignore
5. **REVOKE** any token that gets exposed immediately

## ✅ Safe Practices:
- Use SSH keys for git authentication
- Use Railway's built-in GitHub integration
- Store secrets in Railway environment variables
- Use credential helpers that don't expose tokens
