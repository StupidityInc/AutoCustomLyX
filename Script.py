#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from pathlib import Path
import datetime

# --- CONFIGURATION ---
# REPLACE THIS with your actual Git repo URL for your LyX config
GIT_REPO_URL = "https://github.com/StupidityInc/lyx-config.git" 

# Flatpak ID for LyX
FLATPAK_ID = "org.lyx.LyX"
FLATPAK_BRANCH = "stable"  # Usually tracks the latest (2.4.4)

# --- PATHS ---
USER_HOME = Path.home()
# Flatpak stores user config here on the host machine
FLATPAK_CONFIG_DIR = USER_HOME / ".var/app/org.lyx.LyX/config/lyx" 
# Backup directory for safety
BACKUP_DIR = USER_HOME / "LyX_Backups"

def run_command(command, check=True):
    """Runs a shell command and prints output."""
    try:
        subprocess.run(command, check=check, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}\n{e}")
        sys.exit(1)

def install_lyx_flatpak():
    """Installs or Updates LyX via Flatpak."""
    print(f"--- 📦 Checking Flatpak: {FLATPAK_ID} ---")
    
    # 1. Check if Flatpak is installed
    if shutil.which("flatpak") is None:
        print("Error: Flatpak is not installed. Please install Flatpak first.")
        sys.exit(1)

    # 2. Add Flathub if missing
    run_command("flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo", check=False)

    # 3. Install specific version/branch
    # Note: Flathub 'stable' usually tracks the very latest. 
    # If you specifically need 2.4.4 and stable is behind, we might need a specific commit, 
    # but currently 2.4.x is the active stable.
    print(f"Installing/Updating {FLATPAK_ID}...")
    run_command(f"flatpak install -y flathub {FLATPAK_ID}")

    # 4. Grant File Permissions (Crucial for Git & Fonts)
    # Allows LyX to see your home dir (for git repos) and system fonts (for Hebrew)
    print("Configuring Flatpak permissions...")
    run_command(f"flatpak override --user --filesystem=host {FLATPAK_ID}")
    run_command(f"flatpak override --user --filesystem=xdg-config/git {FLATPAK_ID}") 

def sync_configuration():
    """Clones or Pulls the Git configuration."""
    print(f"\n--- 🔄 Syncing Configuration from {GIT_REPO_URL} ---")
    
    # Ensure the parent directory exists
    if not FLATPAK_CONFIG_DIR.parent.exists():
        print(f"Creating parent directory: {FLATPAK_CONFIG_DIR.parent}")
        FLATPAK_CONFIG_DIR.parent.mkdir(parents=True, exist_ok=True)

    # If directory exists and has .git, pull. If regular dir, backup and clone.
    if (FLATPAK_CONFIG_DIR / ".git").exists():
        print("Git repository detected. Pulling latest changes...")
        os.chdir(FLATPAK_CONFIG_DIR)
        run_command("git pull")
    else:
        if FLATPAK_CONFIG_DIR.exists():
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = BACKUP_DIR / f"lyx_backup_{timestamp}"
            print(f"Existing config found (not a git repo). Backing up to: {backup_path}")
            BACKUP_DIR.mkdir(exist_ok=True)
            shutil.move(str(FLATPAK_CONFIG_DIR), str(backup_path))
        
        print("Cloning fresh repository...")
        run_command(f"git clone {GIT_REPO_URL} {FLATPAK_CONFIG_DIR}")

def setup_hebrew_support():
    """Ensures Hebrew fonts are visible to Flatpak."""
    print("\n--- 🇮🇱 Verifying Hebrew Font Access ---")
    # Flatpak isolation sometimes hides user fonts. 
    # We explicitly expose the .fonts or .local/share/fonts directory.
    
    font_paths = [USER_HOME / ".fonts", USER_HOME / ".local/share/fonts"]
    for path in font_paths:
        if path.exists():
            print(f"Exposing font path: {path}")
            run_command(f"flatpak override --user --filesystem={path} {FLATPAK_ID}")

def main():
    print("### StupidityInc LyX Deployer ###")
    install_lyx_flatpak()
    sync_configuration()
    setup_hebrew_support()
    
    print("\n✅ Deployment Complete.")
    print(f"LyX Config is now live at: {FLATPAK_CONFIG_DIR}")
    print("Launch LyX using: flatpak run org.lyx.LyX")

if __name__ == "__main__":
    main()
