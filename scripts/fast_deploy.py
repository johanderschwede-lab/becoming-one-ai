#!/usr/bin/env python3
"""
Fast Deploy Script
Verifies and deploys in one step
"""
import os
import sys
import asyncio
import subprocess
from pathlib import Path

def run_cmd(cmd: str) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr"""
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr

async def verify_locally():
    """Run local verification"""
    print("\n=== Running Local Verification ===")
    
    # Run the debug script
    cmd = "python3 scripts/debug_bot_locally.py"
    code, out, err = run_cmd(cmd)
    
    if code != 0:
        print("❌ Local verification failed:")
        print(err)
        return False
        
    print("✅ Local verification passed")
    return True

def get_deploy_version():
    """Get the next deployment version"""
    try:
        with open('.deploy_version', 'r') as f:
            version = int(f.read().strip())
    except:
        version = 0
    
    version += 1
    with open('.deploy_version', 'w') as f:
        f.write(str(version))
    
    return version

def get_changes_summary():
    """Get a summary of changes since last commit"""
    code, out, err = run_cmd("git diff --cached --name-only")
    if code != 0:
        return "unknown changes"
    
    files = out.strip().split('\n')
    if not files or files == ['']:
        return "no file changes"
    
    categories = {
        'bot': [],
        'core': [],
        'scripts': [],
        'other': []
    }
    
    for file in files:
        if 'bot' in file:
            categories['bot'].append(file)
        elif 'core' in file:
            categories['core'].append(file)
        elif 'scripts' in file:
            categories['scripts'].append(file)
        else:
            categories['other'].append(file)
    
    summary = []
    if categories['bot']: summary.append('bot')
    if categories['core']: summary.append('core')
    if categories['scripts']: summary.append('scripts')
    if categories['other']: summary.append('other')
    
    return ' + '.join(summary) + ' changes'

def deploy_to_railway():
    """Deploy to Railway"""
    print("\n=== Deploying to Railway ===")
    
    # Get deployment version and changes
    version = get_deploy_version()
    changes = get_changes_summary()
    
    # Commit any changes
    print(f"📝 Committing changes (v{version})...")
    cmds = [
        "git add .",
        f'git commit -m "deploy v{version}: {changes}"',
        "git push origin main"
    ]
    
    for cmd in cmds:
        code, out, err = run_cmd(cmd)
        if code != 0:
            print(f"❌ Failed to run: {cmd}")
            print(err)
            return False
    
    print("✅ Changes pushed to Railway")
    return True

async def main():
    # First verify locally
    if not await verify_locally():
        print("\n❌ Deployment aborted due to verification failure")
        return
    
    # Then deploy
    if not deploy_to_railway():
        print("\n❌ Deployment failed")
        return
    
    print("\n✅ Deployment complete!")
    print("→ Check Railway logs for deployment status")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n● Deployment stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
