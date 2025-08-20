# Proven Deployment Fixes

This document tracks all confirmed working fixes for deployment issues. When encountering similar issues, try these solutions first.

## Import Fixes

1. **Relative Import Error**: "attempted relative import beyond top-level package"
   - **Fix**: Convert all relative imports (from ..module) to absolute imports (from module)
   - **Example**: Change `from ...database.operations import db` to `from database.operations import db`
   - **Files Affected**: All Python files in src/ directory
   - **Status**: CONFIRMED WORKING

2. **Module Resolution**: "No module named 'src'"
   - **Fix**: Add `sys.path.insert(0, str(Path(__file__).parent.parent.parent))` in command files
   - **Location**: Top of each command file
   - **Status**: CONFIRMED WORKING

## Dependency Conflicts

1. **Supabase Client Error**: "Client.__init__() got an unexpected keyword argument 'proxy'"
   - **Fix**: Use flexible version ranges in requirements.txt:
     ```
     python-telegram-bot>=20.0,<21.0
     openai>=1.0,<2.0
     supabase>=2.0,<3.0
     ```
   - **Status**: CONFIRMED WORKING

2. **Missing Dependencies**:
   - **Fix**: Add required dependencies to requirements.txt:
     ```
     passlib==1.7.4  # For RBAC system
     ```
   - **Status**: CONFIRMED WORKING

## Code Organization

1. **Duplicate Methods**: "unexpected indent" or duplicate functionality
   - **Fix**: Merge duplicate methods and ensure proper integration
   - **Example**: Merged duplicate `handle_message` methods in enhanced_telegram_bot.py
   - **Status**: CONFIRMED WORKING

## Railway Deployment

1. **Deployment Trigger**: Railway not auto-deploying after push
   - **Fix**: Use empty commit to trigger deployment:
     ```bash
     git commit --allow-empty -m "trigger: Manual Railway deployment trigger"
     git push origin main
     ```
   - **Status**: CONFIRMED WORKING

2. **Project Organization**: Multiple projects causing confusion
   - **Fix**: Use single Railway project:
     - Project: energetic-upliftment
     - Service: becoming-one-ai
     - Environment: production
   - **Status**: CONFIRMED WORKING

## Testing and Verification

1. **Local Testing**: Test deployment environment locally
   - **Tool**: `scripts/test_railway_locally.py`
   - **Purpose**: Catch common deployment issues before pushing
   - **Status**: IMPLEMENTED

2. **Quick Deployment**: Streamlined deployment process
   - **Tool**: `scripts/quick_railway_deploy.py`
   - **Purpose**: Handle common deployment tasks and verify state
   - **Status**: IMPLEMENTED

## Remember

1. Always document new fixes here when confirmed working
2. Update version ranges rather than pinning exact versions
3. Test locally before pushing to Railway
4. Use the quick deployment script for consistent deployments