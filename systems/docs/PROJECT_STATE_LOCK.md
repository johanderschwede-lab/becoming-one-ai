# PROJECT STATE LOCK - DO NOT OVERWRITE

## CURRENT WORKING SYSTEMS (LOCKED)

### 1. BRAVE-GRATITUDE PROJECT (EXISTING BOT)
- **Status**: ✅ WORKING - DO NOT TOUCH
- **URL**: web-production-048a5.up.railway.app
- **Service**: becoming-one-ai
- **Function**: Telegram bot (working_bot.py)
- **Token**: 8244158767:AAGJveKJcOwFO_PxaeROpiQ7FKGSv-0aFrQ
- **Railway Config**: railway.toml (brave-gratitude)
- **Environment**: Production

### 2. HEROIC-ENCHANTMENT PROJECT (COMPASS API)
- **Status**: 🔄 IN DEVELOPMENT
- **URL**: web-production-89e72.up.railway.app
- **Service**: web
- **Function**: Compass Management API
- **Railway Config**: railway-heroic.toml
- **Environment**: Production

## PROTECTION RULES

### ✅ ALLOWED ACTIONS
- Modify files in CompassBuilder_Phase2/
- Update compass_management_api.py
- Test new features in heroic-enchantment only
- Update documentation

### ❌ FORBIDDEN ACTIONS
- Modify railway.toml (brave-gratitude)
- Change working_bot.py
- Deploy to brave-gratitude project
- Overwrite existing bot configurations

## DEPLOYMENT WORKFLOW

### For New Features:
1. **ASSESS**: Check this file first
2. **ISOLATE**: Work only in heroic-enchantment
3. **TEST**: Use Railway local development
4. **DEPLOY**: Only to heroic-enchantment
5. **VERIFY**: Confirm no impact on brave-gratitude

### Before Any Changes:
```bash
# 1. Check current state
cat PROJECT_STATE_LOCK.md

# 2. Verify which project we're in
railway status

# 3. Test locally first
railway run python compass_management_api.py
```

## EMERGENCY ROLLBACK
If brave-gratitude breaks:
1. Check git history for working railway.toml
2. Restore from last working commit
3. Redeploy brave-gratitude only

---
**LAST UPDATED**: 2025-08-20
**LOCKED BY**: User request to prevent overwrites
