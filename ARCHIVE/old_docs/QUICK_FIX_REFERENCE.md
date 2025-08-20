# Quick Fix Reference

Quick reference for common deployment fixes. For detailed explanations, see PROVEN_DEPLOYMENT_FIXES.md.

## Common Issues & Fixes

### Import Errors
```python
# ❌ DON'T use relative imports
from ...database.operations import db

# ✅ DO use absolute imports
from database.operations import db

# ✅ DO add in command files:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
```

### Dependency Conflicts
```txt
# ✅ DO use flexible version ranges
python-telegram-bot>=20.0,<21.0
openai>=1.0,<2.0
supabase>=2.0,<3.0
passlib==1.7.4
```

### Railway Deployment
```bash
# ✅ DO trigger deployment with empty commit
git commit --allow-empty -m "trigger: Manual Railway deployment trigger"
git push origin main
```

### Code Organization
- Check for duplicate methods
- Merge similar functionality
- Use consistent import patterns
- Follow project structure

### Quick Test
```bash
# ✅ DO test locally first
python scripts/test_railway_locally.py

# ✅ DO use quick deploy script
python scripts/quick_railway_deploy.py
```

## Project Info

- Railway Project: energetic-upliftment
- Service: becoming-one-ai
- Environment: production
- Web URL: web-production-048a5.up.railway.app