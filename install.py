#!/usr/bin/env python3
import os
import shutil
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# --- CONFIGURATION ---
# UPDATED: Points to 'AutoCustomLyX' on 'master' branch based on your link
REPO_BASE_URL = "https://raw.githubusercontent.com/StupidityInc/AutoCustomLyX/master"

# Files to fetch based on your uploaded file structure.
# FORMAT: "Remote Path in Repo" : "Local Path in LyX Config"
FILES_TO_FETCH = {
    "preferences": "preferences",
    "bind/user.bind": "bind/user.bind",
    "Macros/Macros_Standard.lyx": "Macros/Macros_Standard.lyx", 
    "Templates/Assignments.lyx": "templates/Assignments.lyx"
}

FLATPAK_ID = "org.lyx.LyX"
FLATPAK_CONFIG_DIR = Path.home() / f".var/app/{FLATPAK_ID}/config/lyx"

def run_cmd(cmd):
    print(f"Executing: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def ensure_flatpak():
    if shutil.which("flatpak") is None:
        print("📦 Flatpak not found. Installing...")
        run_cmd("sudo apt update && sudo apt install -y flatpak")

def install_lyx():
    print(f"--- 📦 Setting up {FLATPAK_ID} ---")
    run_cmd("flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo")
    run_cmd(f"flatpak install --user -y flathub {FLATPAK_ID}")
    
    print("🔓 Unlocking filesystem permissions...")
    run_cmd(f"flatpak override --user --filesystem=host {FLATPAK_ID}")
    
    # Expose fonts
    font_paths = [Path.home() / ".fonts", Path.home() / ".local/share/fonts", Path("/usr/share/fonts")]
    for fp in font_paths:
        if fp.exists():
            run_cmd(f"flatpak override --user --filesystem={fp} {FLATPAK_ID}")

def scrape_config():
    print("\n--- 📥 Scraping Configuration ---")
    if not FLATPAK_CONFIG_DIR.exists():
        FLATPAK_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    for remote_path, local_rel_path in FILES_TO_FETCH.items():
        url = f"{REPO_BASE_URL}/{remote_path}"
        dest = FLATPAK_CONFIG_DIR / local_rel_path
        
        print(f"⬇️  Fetching: {url}")
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(url, dest)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"❌ 404 Not Found: {url}")
                print(f"   (Make sure '{remote_path}' exists in your GitHub repo!)")
            else:
                print(f"❌ HTTP Error {e.code}: {url}")
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    print("🚀 Starting AutoCustomLyX Installer...")
    try:
        ensure_flatpak()
        install_lyx()
        scrape_config()
        print("\n✅ Done. Launch LyX and run 'Tools > Reconfigure'.")
    except Exception as e:
        print(f"\n❌ Script Failed: {e}")

if __name__ == "__main__":
    main()