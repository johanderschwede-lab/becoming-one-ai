# DEPLOYMENT SAFETY TEMPLATE

## PRE-DEPLOYMENT CHECKLIST

### 1. STATE ASSESSMENT
- [ ] Read PROJECT_STATE_LOCK.md
- [ ] Check which Railway project is active: `railway status`
- [ ] Verify no conflicts with existing services
- [ ] Confirm target project is correct

### 2. ISOLATION VERIFICATION
- [ ] Work in separate directory/branch for new features
- [ ] Use unique file names to avoid conflicts
- [ ] Test locally before deployment
- [ ] Use Railway local development: `railway run`

### 3. DEPLOYMENT SAFETY
- [ ] Create backup of working configurations
- [ ] Use feature flags for new functionality
- [ ] Deploy to staging/test environment first
- [ ] Monitor logs during deployment

## TEMPLATE FOR NEW FEATURES

### Step 1: Create Isolated Environment
```bash
# Create new directory for feature
mkdir new-feature-name
cd new-feature-name

# Copy only necessary files
cp ../compass_management_api.py .
cp ../requirements.txt .
```

### Step 2: Test Locally
```bash
# Test without affecting production
railway run python new_feature.py

# Or use local testing
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
python new_feature.py
```

### Step 3: Safe Deployment
```bash
# Deploy only to target project
railway link --project target-project-name
railway up
```

## EMERGENCY PROCEDURES

### If Production Breaks:
1. **STOP**: Don't make more changes
2. **ASSESS**: Check PROJECT_STATE_LOCK.md
3. **ROLLBACK**: `git revert HEAD`
4. **RESTORE**: Deploy working version
5. **DOCUMENT**: Update PROJECT_STATE_LOCK.md

### Communication Protocol:
- Always state which project you're working on
- Confirm before making changes to working systems
- Use clear commit messages with project names
- Update PROJECT_STATE_LOCK.md after changes

## PLUGINS/TOOLS RECOMMENDATIONS

### For Cursor/VS Code:
- **GitLens**: Track file changes and history
- **Railway**: Official Railway extension
- **Docker**: For local container testing
- **Environment Variables**: Manage .env files

### For Terminal:
- **tmux**: Multiple terminal sessions
- **htop**: Monitor system resources
- **jq**: Parse JSON responses
- **curl**: Test APIs locally

### For Deployment:
- **Railway CLI**: Local development
- **Docker**: Containerized testing
- **Git hooks**: Pre-commit checks
- **CI/CD**: Automated testing

## TEMPLATE USAGE

Before starting ANY new work:
1. Copy this template
2. Fill out the checklist
3. Follow the isolation steps
4. Update PROJECT_STATE_LOCK.md
5. Document any changes

---
**TEMPLATE VERSION**: 1.0
**CREATED**: 2025-08-20
**PURPOSE**: Prevent overwriting working systems
