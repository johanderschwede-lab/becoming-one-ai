#!/usr/bin/env python3
"""
Local Railway Environment Tester
Simulates Railway environment and catches common deployment issues before pushing
"""
import os
import sys
import importlib
import logging
from pathlib import Path
from typing import List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies() -> Tuple[bool, List[str]]:
    """Verify all dependencies can be imported"""
    required = [
        'telegram', 
        'openai',
        'supabase',
        'passlib',
        'pinecone',
        'loguru'
    ]
    
    missing = []
    for pkg in required:
        try:
            importlib.import_module(pkg)
            logger.info(f"✓ {pkg} imported successfully")
        except ImportError as e:
            missing.append(pkg)
            logger.error(f"✗ Failed to import {pkg}: {e}")
    
    return len(missing) == 0, missing

def check_environment() -> Tuple[bool, List[str]]:
    """Verify all required environment variables are set"""
    required = [
        'TELEGRAM_BOT_TOKEN',
        'OPENAI_API_KEY',
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY',
        'PINECONE_API_KEY',
        'PINECONE_ENVIRONMENT'
    ]
    
    missing = []
    for var in required:
        if not os.getenv(var):
            missing.append(var)
            logger.error(f"✗ Missing environment variable: {var}")
        else:
            logger.info(f"✓ Found {var}")
    
    return len(missing) == 0, missing

def test_imports() -> Tuple[bool, List[str]]:
    """Test importing our key modules"""
    errors = []
    
    try:
        from database.operations import db
        logger.info("✓ Database operations imported")
    except Exception as e:
        errors.append(f"Database operations: {str(e)}")
        logger.error(f"✗ Failed to import database operations: {e}")

    try:
        from core.ai_engine import AIEngine
        logger.info("✓ AI engine imported")
    except Exception as e:
        errors.append(f"AI engine: {str(e)}")
        logger.error(f"✗ Failed to import AI engine: {e}")

    try:
        from core.rbac_system import SimpleRBAC
        logger.info("✓ RBAC system imported")
    except Exception as e:
        errors.append(f"RBAC system: {str(e)}")
        logger.error(f"✗ Failed to import RBAC system: {e}")

    try:
        from bots.telegram.enhanced_telegram_bot import EnhancedBecomingOneTelegramBot
        logger.info("✓ Enhanced bot imported")
    except Exception as e:
        errors.append(f"Enhanced bot: {str(e)}")
        logger.error(f"✗ Failed to import Enhanced bot: {e}")

    return len(errors) == 0, errors

def main():
    logger.info("=== Testing Railway Environment ===")
    
    # Check dependencies
    deps_ok, missing_deps = check_dependencies()
    if not deps_ok:
        logger.error("✗ Missing dependencies:")
        for dep in missing_deps:
            logger.error(f"  - {dep}")
        return False

    # Check environment
    env_ok, missing_env = check_environment()
    if not env_ok:
        logger.error("✗ Missing environment variables:")
        for var in missing_env:
            logger.error(f"  - {var}")
        return False

    # Test imports
    imports_ok, import_errors = test_imports()
    if not imports_ok:
        logger.error("✗ Import errors:")
        for error in import_errors:
            logger.error(f"  - {error}")
        return False

    logger.info("✓ All checks passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
