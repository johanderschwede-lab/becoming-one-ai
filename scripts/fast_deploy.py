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

def deploy_to_railway():
    """Deploy to Railway"""
    print("\n=== Deploying to Railway ===")
    
    # Commit any changes
    print("📝 Committing changes...")
    cmds = [
        "git add .",
        'git commit -m "deploy: Fast deploy with verified changes"',
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
