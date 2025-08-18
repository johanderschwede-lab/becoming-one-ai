# PROVEN DEPLOYMENT FIXES
**Becoming One™ AI System - Railway Deployment Solutions**

> **CRITICAL:** These fixes are CONFIRMED WORKING. Apply them in sequence for successful Railway deployments.

---

## 🏛️ **RAILWAY DEPLOYMENT SUCCESS PATTERN**

### **STEP 1: Fix Relative Imports (CONFIRMED WORKING)**
**Problem:** `ImportError: attempted relative import beyond top-level package`

**Solution:** Convert ALL relative imports to absolute imports in these files:

```python
# ❌ BEFORE (Fails on Railway)
from ...database.operations import db
from ..integrations.pinecone_client import PineconeClient
from .becoming_one_method import BecomingOneMethod

# ✅ AFTER (Works on Railway)  
from database.operations import db
from integrations.pinecone_client import PineconeClient
from core.becoming_one_method import BecomingOneMethod
```

**Files to Fix:**
- `src/bots/telegram/enhanced_telegram_bot.py`
- `src/core/ai_engine.py`
- `src/core/sacred_library_integration.py`
- `src/bots/telegram/commands/hylozoic_study_commands.py`

**Command Files Pattern:**
```python
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from database.operations import db
from core.ai_engine import BecomingOneAI
```

---

### **STEP 2: Fix Dependency Conflicts (CONFIRMED WORKING)**
**Problem:** `ERROR: ResolutionImpossible` - httpx version conflicts between packages

**Root Cause:** 
- `python-telegram-bot==20.7` requires `httpx~=0.25.2`
- `supabase==2.7.4` conflicts with this httpx version

**Solution:** Use compatible package versions in `requirements.txt`:

```txt
python-telegram-bot==20.7
python-dotenv==1.0.0
requests==2.31.0
loguru==0.7.2
openai==1.51.0
supabase==2.6.0  # ← CRITICAL: Use 2.6.0 (not 2.7.4)
pinecone-client==5.0.1
PyPDF2==3.0.1
PyMuPDF==1.23.26
beautifulsoup4==4.12.2
# DO NOT pin httpx - let pip resolve compatible version
```

---

### **STEP 3: Single Railway Project (CONFIRMED WORKING)**
**Problem:** Multiple Railway projects cause deployment confusion

**Solution:** 
- Delete all Railway projects except the target one
- Use single project: `energetic-upliftment` / `becoming-one-ai` / `production`
- Repository: `johanderschwede-lab/becoming-one-ai.git`
- Deployment URL: `web-production-048a5.up.railway.app`

---

## 🏛️ **SACRED LIBRARY INTEGRATION**

### **Database Structure:**
- **Table:** `teaching_materials` (Supabase)
- **Sacred Quotes:** 4,871 authentic Hylozoics quotes
- **Filter:** `material_type = 'sacred_quote'`
- **Columns:** `material_id`, `content`, `title`, `metadata`

### **Search Methods:**
```python
# Keyword search
quotes = await ai.search_sacred_library("consciousness", limit=3)

# Vector search (semantic)
quotes = await ai.vector_search_sacred_library("meditation", limit=2)
```

### **Preferred Response Sequence:**
1. **Ask Permission:** "Would you like me to share authentic Hylozoics quotes?"
2. **Show Quotes:** With source citations (chapter, language)
3. **Vector Summary:** Zero-hallucination synthesis
4. **Soft Commentary:** Practical application

---

## 🚀 **DEPLOYMENT CHECKLIST**

### **Environment Variables Required:**
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
SUPABASE_URL=your_supabase_url  
SUPABASE_ANON_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key
```

### **Successful Startup Sequence:**
```
✅ OpenAI and Supabase modules available
✅ Enhanced Bot module imported successfully  
✅ Database operations imported
✅ AI engine imported
✅ RBAC system imported
✅ Enhanced Bot initialized successfully
✅ Sacred Library: INTEGRATED (4,871 quotes)
✅ AI Engine: FULL HYLOZOICS ACCESS
```

### **Files Structure:**
```
enhanced_railway_launcher.py  # Main launcher (no fallback)
src/
├── bots/telegram/
│   ├── enhanced_telegram_bot.py  # Main bot (absolute imports)
│   └── commands/
│       ├── sacred_library_commands.py
│       └── hylozoic_study_commands.py  # Study rooms
├── core/
│   ├── ai_engine.py  # Sacred Library integration
│   ├── sacred_library_integration.py
│   └── becoming_one_method.py
└── database/
    └── operations.py  # Supabase client
```

---

### **STEP 4: Railway Deployment Trigger (CONFIRMED WORKING)**
**Problem:** Railway doesn't start build process after push

**Solution:** Force deployment with empty commit:
```bash
git commit --allow-empty -m "trigger: Manual Railway deployment trigger"
git push origin main
```

This forces Railway to detect changes and start a new build.

---

## 🧠 **TROUBLESHOOTING**

### **Common Errors & Solutions:**

**Error:** `attempted relative import beyond top-level package`
**Fix:** Apply STEP 1 (convert relative imports)

**Error:** `Client.__init__() got an unexpected keyword argument 'proxy'`
**Fix:** Apply STEP 2 (pin httpx==0.24.1)

**Error:** `Healthcheck failure`
**Fix:** Check Railway logs for specific error, apply relevant steps above

**Error:** Bot responds but no Sacred Library quotes
**Fix:** Check Supabase connection, verify 4,871 quotes in `teaching_materials` table

---

## 📋 **VERIFICATION COMMANDS**

### **Test Sacred Library Access:**
```python
# Test locally
python3 -c "
import sys, os
sys.path.insert(0, 'src')
os.environ.update({k:v for k,v in [line.strip().split('=',1) for line in open('config/production.env') if '=' in line and not line.startswith('#')]})
from database.operations import db
result = db.client.table('teaching_materials').select('count', count='exact').eq('material_type', 'sacred_quote').execute()
print(f'Sacred Library quotes: {result.count}')
"
```

### **Test Bot Response:**
Send message: `"What does Laurency say about consciousness?"`
Expected: Authentic quotes with source citations

---

## 🎯 **SUCCESS METRICS**

### **Deployment Success:**
- ✅ Railway build completes without errors
- ✅ Health check passes
- ✅ Bot responds to `/start` command
- ✅ Sacred Library commands work (`/sacred`, `/study`)

### **Sacred Library Success:**
- ✅ Bot includes authentic Hylozoics quotes in responses
- ✅ Quotes have proper source citations (chapter, language)
- ✅ Study rooms provide focused Hylozoic learning
- ✅ Zero hallucinations in quote content

---

> **REMEMBER:** These fixes are proven and should be applied to ALL Railway deployments. Store this file in the project root and reference it in future sessions.

**Last Updated:** 2025-08-18
**Status:** CONFIRMED WORKING ✅
