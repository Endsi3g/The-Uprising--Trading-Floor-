import subprocess
import sys
import re
from pathlib import Path

CHANGELOG_PATH = Path("trading-ai-suite/CHANGELOG.md")

def get_latest_version():
    """Extracts the latest version from CHANGELOG.md."""
    if not CHANGELOG_PATH.exists():
        print(f"❌ Changelog not found at {CHANGELOG_PATH}")
        return None
    
    with open(CHANGELOG_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r"## \[(.*?)\]", content)
        if match:
            return match.group(1)
    return None

def create_github_release(version):
    """Creates a GitHub release using the 'gh' CLI."""
    print(f"🚀 Preparing GitHub release for v{version}...")
    
    # Try to extract the notes for this version
    with open(CHANGELOG_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        # Find content between the latest version header and the next version header
        pattern = rf"## \[{re.escape(version)}\].*?\n(.*?)(?=\n## \[|$)"
        match = re.search(pattern, content, re.DOTALL)
        notes = match.group(1).strip() if match else "New release: " + version

    tag = f"v{version}"
    cmd = [
        "gh", "release", "create", tag,
        "--title", f"Release {tag}",
        "--notes", notes,
        "--target", "main"
    ]

    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print(f"✅ GitHub Release {tag} created successfully!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create GitHub release: {e.stderr}")
    except FileNotFoundError:
        print("❌ 'gh' CLI not found. Please install GitHub CLI to use this feature.")

if __name__ == "__main__":
    version = get_latest_version()
    if version:
        create_github_release(version)
    else:
        print("❌ Could not determine version.")
