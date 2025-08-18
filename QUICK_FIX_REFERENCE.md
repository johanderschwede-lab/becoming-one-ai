# QUICK FIX REFERENCE
**Immediate Solutions for Common Issues**

## 🚨 **RAILWAY DEPLOYMENT ERRORS**

### **Import Error Fix:**
```bash
# Error: "attempted relative import beyond top-level package"
# Fix: Convert relative imports to absolute in these files:
sed -i 's/from \.\.\./from /g' src/bots/telegram/enhanced_telegram_bot.py
sed -i 's/from \.\./from /g' src/core/ai_engine.py
```

### **Dependency Conflict Fix:**
```bash
# Error: "ERROR: ResolutionImpossible" with httpx versions
# Fix: Use compatible versions in requirements.txt:
# supabase==2.6.0 (not 2.7.4)
# python-telegram-bot==20.7
# DO NOT pin httpx explicitly
```

### **Deploy Commands:**
```bash
# Normal deployment
git add . && git commit -m "fix: Apply proven Railway fixes" && git push origin main

# Force Railway deployment (if no build starts)
git commit --allow-empty -m "trigger: Manual Railway deployment trigger" && git push origin main
```

## 🏛️ **SACRED LIBRARY STATUS**

### **Check Quote Count:**
```python
# Should return 4,871
from database.operations import db
result = db.client.table('teaching_materials').select('count', count='exact').eq('material_type', 'sacred_quote').execute()
print(result.count)
```

### **Test Bot Response:**
Send: `"What does Laurency say about consciousness?"`
Expect: Authentic quotes with citations

## 📍 **PROJECT INFO**
- **Railway:** web-production-048a5.up.railway.app
- **Repo:** johanderschwede-lab/becoming-one-ai.git
- **Sacred Quotes:** 4,871 in Supabase `teaching_materials`
- **Commands:** `/sacred`, `/study`, `/hylozoic`
