#!/usr/bin/env python3
"""
Quick Railway Deployment Helper
Handles common deployment tasks and verifies state before pushing
"""
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

def run_cmd(cmd: str) -> Tuple[int, str, str]:
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

def verify_git_state() -> bool:
    """Check git state and stash any changes"""
    print("Checking git state...")
    
    # Check if we have changes
    code, out, err = run_cmd("git status --porcelain")
    if out.strip():
        print("Stashing changes...")
        run_cmd("git stash")
        return True
    return False

def run_local_tests() -> bool:
    """Run the local Railway environment tests"""
    print("Running local Railway tests...")
    code, out, err = run_cmd("python scripts/test_railway_locally.py")
    if code != 0:
        print("Local tests failed!")
        print(out)
        print(err, file=sys.stderr)
        return False
    return True

def trigger_deployment() -> bool:
    """Push an empty commit to trigger Railway deployment"""
    print("Triggering Railway deployment...")
    cmds = [
        "git commit --allow-empty -m 'trigger: Manual Railway deployment trigger'",
        "git push origin main"
    ]
    
    for cmd in cmds:
        code, out, err = run_cmd(cmd)
        if code != 0:
            print(f"Failed to run: {cmd}")
            print(err, file=sys.stderr)
            return False
    return True

def main():
    # Store if we stashed changes
    had_changes = verify_git_state()
    
    # Run local tests
    if not run_local_tests():
        print("Fix local test failures before deploying!")
        return False
    
    # Trigger deployment
    if not trigger_deployment():
        print("Failed to trigger deployment!")
        return False
    
    print("✓ Deployment triggered successfully!")
    
    # Remind about stashed changes
    if had_changes:
        print("\nNOTE: You had local changes that were stashed.")
        print("Run 'git stash pop' to restore them.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
