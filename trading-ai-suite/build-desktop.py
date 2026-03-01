"""
The Uprising Trading Floor - Desktop App Build Orchestrator
Generates .exe (Windows) and .dmg (macOS) desktop applications.
"""
import subprocess
import sys
import os
import platform

ROOT = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(ROOT, "dashboard")

def run(cmd, cwd=None):
    """Execute a command and stream output."""
    print(f"\n>>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd or DASHBOARD_DIR)
    if result.returncode != 0:
        print(f"[ERROR] Command failed with exit code {result.returncode}")
        sys.exit(1)

def build_next():
    """Build the Next.js production bundle."""
    print("\n=== Step 1: Building Next.js Production Bundle ===")
    run("npm run build")

def build_electron():
    """Package the Electron app for the current platform."""
    current_os = platform.system()
    
    if current_os == "Windows":
        print("\n=== Step 2: Packaging for Windows (.exe) ===")
        run("npx electron-builder --win --x64")
    elif current_os == "Darwin":
        print("\n=== Step 2: Packaging for macOS (.dmg) ===")
        run("npx electron-builder --mac --x64")
    else:
        print(f"\n=== Step 2: Packaging for {current_os} ===")
        run("npx electron-builder --linux")

    print("\n=== BUILD COMPLETE ===")
    
    dist_dir = os.path.join(DASHBOARD_DIR, "dist")
    if os.path.exists(dist_dir):
        print(f"\nOutput artifacts in: {dist_dir}")
        for f in os.listdir(dist_dir):
            fpath = os.path.join(dist_dir, f)
            if os.path.isfile(fpath):
                size_mb = os.path.getsize(fpath) / (1024 * 1024)
                print(f"  -> {f} ({size_mb:.1f} MB)")
    else:
        print("[WARNING] dist/ directory not found. Check build output above.")

def main():
    print("=" * 50)
    print("THE UPRISING TRADING FLOOR")
    print("Desktop Application Builder")
    print("=" * 50)
    
    build_next()
    build_electron()

if __name__ == "__main__":
    main()
