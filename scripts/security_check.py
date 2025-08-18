#!/usr/bin/env python3
"""
SECURITY CHECKER
Scan for accidentally committed secrets before git commits
"""

import os
import re
import sys
from pathlib import Path

# Patterns that indicate secrets
SECRET_PATTERNS = [
    r'ghp_[A-Za-z0-9_]{36}',  # GitHub Personal Access Token
    r'github_pat_[A-Za-z0-9_]{82}',  # GitHub Fine-grained PAT
    r'sk-[A-Za-z0-9]{48}',  # OpenAI API Key
    r'AKIA[0-9A-Z]{16}',  # AWS Access Key
    r'AIza[0-9A-Za-z_-]{35}',  # Google API Key
    r'ya29\.[0-9A-Za-z_-]+',  # Google OAuth Token
    r'[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com',  # Google OAuth Client
    r'xox[baprs]-[A-Za-z0-9-]+',  # Slack Token
    r'[a-f0-9]{40}',  # Generic 40-char hex (could be secret)
]

# Files to always check
ALWAYS_CHECK = [
    '*.py', '*.js', '*.ts', '*.json', '*.yaml', '*.yml', 
    '*.md', '*.txt', '*.sh', '*.env*'
]

# Directories to skip
SKIP_DIRS = [
    '.git', '__pycache__', 'node_modules', 'venv', '.venv',
    'sacred_library_files', 'laurency_ultimate', 'laurency_organized'
]

def scan_file(file_path):
    """Scan a file for potential secrets"""
    secrets_found = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        for i, line in enumerate(content.split('\n'), 1):
            for pattern in SECRET_PATTERNS:
                matches = re.finditer(pattern, line)
                for match in matches:
                    secrets_found.append({
                        'file': file_path,
                        'line': i,
                        'pattern': pattern,
                        'match': match.group(),
                        'context': line.strip()
                    })
    
    except Exception as e:
        print(f"⚠️  Could not scan {file_path}: {e}")
    
    return secrets_found

def should_skip_dir(dir_path):
    """Check if directory should be skipped"""
    dir_name = os.path.basename(dir_path)
    return dir_name in SKIP_DIRS or dir_name.startswith('.')

def scan_repository():
    """Scan entire repository for secrets"""
    repo_root = Path(__file__).parent.parent
    all_secrets = []
    
    print("🔍 Scanning repository for potential secrets...")
    
    for root, dirs, files in os.walk(repo_root):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not should_skip_dir(os.path.join(root, d))]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Check if file should be scanned
            if any(file.endswith(ext.replace('*', '')) for ext in ALWAYS_CHECK):
                secrets = scan_file(file_path)
                all_secrets.extend(secrets)
    
    return all_secrets

def main():
    """Main security check"""
    print("🔒 SECURITY CHECKER")
    print("=" * 30)
    
    secrets = scan_repository()
    
    if not secrets:
        print("✅ No potential secrets found!")
        return 0
    
    print(f"❌ Found {len(secrets)} potential secrets:")
    print()
    
    for secret in secrets:
        print(f"🚨 {secret['file']}:{secret['line']}")
        print(f"   Pattern: {secret['pattern']}")
        print(f"   Match: {secret['match'][:20]}...")
        print(f"   Context: {secret['context'][:100]}")
        print()
    
    print("🔒 SECURITY RECOMMENDATIONS:")
    print("1. Remove these secrets from files")
    print("2. Add them to .env files (not committed)")
    print("3. Use environment variables in code")
    print("4. Revoke any exposed tokens")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
