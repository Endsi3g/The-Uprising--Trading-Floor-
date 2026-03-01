import subprocess
import sys
import os
from pathlib import Path

# Configuration
TEST_SCRIPT = "scripts/test_app_full.py"
REMOTE = "origin"
BRANCH_MAP = "master:main"

def run_command(command, description):
    """Run a shell command and return its exit code and output."""
    print(f"\n--- {description} ---")
    try:
        result = subprocess.run(command, shell=True, check=False, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode
    except Exception as e:
        print(f"Execution Error: {e}", file=sys.stderr)
        return 1

def main():
    root_dir = Path(__file__).parent
    os.chdir(root_dir)

    # 1. Run Integrity Tests
    print("--- Initializing Shipping Protocol ---")
    test_rc = run_command(f"{sys.executable} {TEST_SCRIPT}", "Running Master Integrity Tests")
    
    if test_rc != 0:
        print("\nABORTED: Integrity tests failed. Fix errors before shipping.")
        sys.exit(1)

    # 2. Git Automation
    commit_msg = input("\nEnter commit message (or press Enter for default): ").strip()
    if not commit_msg:
        commit_msg = "Automated ship: project update and integrity verified"

    print(f"\nPreparing Package...")
    run_command("git add .", "Staging changes")
    
    # Check if there are changes to commit
    status_rc = run_command("git diff --cached --quiet", "Checking for changes")
    if status_rc == 0:
        print("\nNo changes to commit. Proceeding to push...")
    else:
        run_command(f'git commit -m "{commit_msg}"', "Committing changes")

    # 3. Push to Main
    print(f"\nDeploying to {REMOTE}/{BRANCH_MAP}...")
    push_rc = run_command(f"git push {REMOTE} {BRANCH_MAP}", "Pushing to repository")

    if push_rc == 0:
        print("\nMISSION ACCOMPLISHED: Project is shipped and integrity is verified.")
    else:
        print("\nERROR: Push failed. Check your internet connection or git permissions.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Shipping cancelled by user.")
        sys.exit(1)
