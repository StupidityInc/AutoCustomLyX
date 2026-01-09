#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from pathlib import Path

# --- CONFIG ---
GIT_REPO_URL = "https://github.com/StupidityInc/AutoCustomLyX.git" 
FLATPAK_ID = "org.lyx.LyX"
FLATPAK_CONFIG_DIR = Path.home() / f".var/app/{FLATPAK_ID}/config/lyx"

def run_cmd(cmd):
    """Run a command. Using shell=True allows sudo to prompt for a password."""
    print(f"Executing: {cmd}")
    # shell=True is needed here to allow the interactive sudo prompt
    subprocess.run(cmd, shell=True, check=True)

def main():
    print("--- 🛠️ Starting LyX Deployment ---")
    
    # 1. System Dependencies (Git & Flatpak)
    if not shutil.which("git") or not shutil.which("flatpak"):
        print("📦 Installing missing system tools...")
        run_cmd("sudo apt update && sudo apt install -y git flatpak")

    # 2. Install LyX via Flatpak
    print("📦 Installing LyX...")
    run_cmd("flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo")
    run_cmd(f"flatpak install --user -y flathub {FLATPAK_ID}")
    run_cmd(f"flatpak override --user --filesystem=host {FLATPAK_ID}")

    # 3. Clone/Sync Config
    if not FLATPAK_CONFIG_DIR.parent.exists():
        FLATPAK_CONFIG_DIR.parent.mkdir(parents=True, exist_ok=True)

    if (FLATPAK_CONFIG_DIR / ".git").exists():
        print("🔄 Pulling latest config...")
        run_cmd(f"git -C {FLATPAK_CONFIG_DIR} pull")
    else:
        print("⬇️ Cloning fresh config...")
        # If directory exists but isn't git, we remove it to clone fresh
        if FLATPAK_CONFIG_DIR.exists():
            shutil.rmtree(FLATPAK_CONFIG_DIR)
        run_cmd(f"git clone {GIT_REPO_URL} {FLATPAK_CONFIG_DIR}")

    print("\n✅ Setup finished! Launch LyX via your app menu or 'flatpak run org.lyx.LyX'")

if __name__ == "__main__":
    main()