#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from pathlib import Path
import datetime

# --- CONFIGURATION ---
# Points to your main repo. Make sure your 'preferences', 'bind', etc., are in this repo!
GIT_REPO_URL = "https://github.com/StupidityInc/AutoCustomLyX.git" 
FLATPAK_ID = "org.lyx.LyX"

# --- PATHS ---
USER_HOME = Path.home()
FLATPAK_CONFIG_DIR = USER_HOME / f".var/app/{FLATPAK_ID}/config/lyx"
BACKUP_DIR = USER_HOME / "LyX_Backups"

def run_command(command, check=True):
    """Utility to run shell commands."""
    try:
        subprocess.run(command, check=check, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running: {command}\n{e}")
        # Don't exit on all errors (some might be non-critical)

def ensure_dependencies():
    """Ensures Git and Flatpak are installed (Debian/Ubuntu/Mint)."""
    print("--- 🛠️ Checking System Dependencies ---")
    
    # Check Git
    if shutil.which("git") is None:
        print("📦 Git missing. Installing...")
        run_command("sudo apt update && sudo apt install -y git")
    
    # Check Flatpak
    if shutil.which("flatpak") is None:
        print("📦 Flatpak missing. Installing...")
        run_command("sudo apt update && sudo apt install -y flatpak")
        print("⚠️ Note: You might need to log out/in for Flatpak paths to update.")

def install_lyx_flatpak():
    """Installs LyX via Flatpak."""
    print(f"--- 📦 Setting up LyX Flatpak ---")
    run_command("flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo")
    run_command(f"flatpak install --user -y flathub {FLATPAK_ID}")
    
    # Grant filesystem access so LyX can see your local files and fonts
    run_command(f"flatpak override --user --filesystem=host {FLATPAK_ID}")

def sync_configuration():
    """Clones your Git repo into the LyX config folder."""
    print(f"\n--- 🔄 Syncing Config from {GIT_REPO_URL} ---")
    
    if not FLATPAK_CONFIG_DIR.parent.exists():
        FLATPAK_CONFIG_DIR.parent.mkdir(parents=True, exist_ok=True)

    # Handle existing data
    if (FLATPAK_CONFIG_DIR / ".git").exists():
        print("✅ Git repo detected. Pulling latest...")
        run_command(f"git -C {FLATPAK_CONFIG_DIR} pull")
    else:
        if FLATPAK_CONFIG_DIR.exists():
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = BACKUP_DIR / f"lyx_old_{timestamp}"
            BACKUP_DIR.mkdir(exist_ok=True)
            print(f"p 🗄️ Moving existing config to {backup_path}")
            shutil.move(str(FLATPAK_CONFIG_DIR), str(backup_path))
        
        print(f"⬇️ Cloning into {FLATPAK_CONFIG_DIR}...")
        run_command(f"git clone {GIT_REPO_URL} {FLATPAK_CONFIG_DIR}")

def fix_fonts():
    """Exposes host fonts to the Flatpak container."""
    font_paths = [USER_HOME / ".fonts", USER_HOME / ".local/share/fonts", Path("/usr/share/fonts")]
    for p in font_paths:
        if p.exists():
            run_command(f"flatpak override --user --filesystem={p} {FLATPAK_ID}")

def main():
    print("🚀 AutoCustomLyX Installer Starting...")
    
    ensure_dependencies()
    install_lyx_flatpak()
    sync_configuration()
    fix_fonts()
    
    print("\n" + "="*40)
    print("✅ DEPLOYMENT SUCCESSFUL")
    print(f"Config: {FLATPAK_CONFIG_DIR}")
    print("Next Step: Launch LyX and run 'Tools > Reconfigure'")
    print("="*40)

if __name__ == "__main__":
    main()