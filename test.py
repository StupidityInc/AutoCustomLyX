import os
import sys
import urllib.request
from pathlib import Path

# --- CONFIGURATION ---
LYX_PREFRENCES_URL = (
    "https://raw.githubusercontent.com/StupidityInc/lyx-config/main/preferences"
)
LYX_BIND_URL = (
    "https://raw.githubusercontent.com/StupidityInc/lyx-config/main/bind/user.bind"
)
LYX_MACROS_URL = (
    "https://raw.githubusercontent.com/StupidityInc/lyx-config/main/Macros/Macros_Standard.lyx"
)
LYX_TEMPLATE_URL = (
    "https://raw.githubusercontent.com/StupidityInc/lyx-config/main/Templates/Assignments.lyx"
)

### UTILITIES ###

def get_lyx_user_directory():
    """Locates the LyX user configuration directory on Windows, Mac, or Linux (including Flatpak)."""
    # 1. Check Flatpak (Common on modern Linux)
    flatpak_path = Path.home() / ".var/app/org.lyx.LyX/config/lyx"
    if flatpak_path.exists():
        return str(flatpak_path)

    # 2. Check Standard OS Paths
    if sys.platform == "win32":
        roaming = os.environ.get("APPDATA")
        if roaming:
            # Try to find an existing LyX folder
            contents = os.listdir(roaming)
            latest_lyx = sorted([f for f in contents if f.startswith("LyX")])
            if latest_lyx:
                return os.path.join(roaming, latest_lyx[-1])
            # Fallback if not yet created but we are on Windows
            return os.path.join(roaming, "LyX2.4") 
    elif sys.platform == "darwin":
        app_support = os.path.expanduser("~/Library/Application Support")
        if os.path.exists(app_support):
            contents = os.listdir(app_support)
            latest_lyx = sorted([f for f in contents if f.startswith("LyX")])
            if latest_lyx:
                return os.path.join(app_support, latest_lyx[-1])
            return os.path.join(app_support, "LyX-2.4")
    else:
        # Standard Linux
        return os.path.expanduser("~/.lyx")
    
    return None

def download_file(github_raw_url, destination_folder, file_name):
    """Downloads a file from a URL to a local destination, creating folders if needed."""
    full_path = os.path.join(destination_folder, file_name)
    
    # Ensure the destination folder exists
    if not os.path.exists(destination_folder):
        print(f"[LyX Hebrew] Creating folder: {destination_folder}")
        try:
            os.makedirs(destination_folder, exist_ok=True)
        except OSError as e:
            print(f"[LyX Hebrew] Error creating directory {destination_folder}: {e}")
            return

    print(f"[LyX Hebrew] Downloading {file_name}...")
    try:
        # Download the file
        with urllib.request.urlopen(github_raw_url) as response:
            content = response.read()
            with open(full_path, 'wb') as f:
                f.write(content)
        print(f"[LyX Hebrew] Successfully saved to {full_path}")
    except Exception as e:
        print(f"[LyX Hebrew] ❌ Error downloading {file_name}: {e}")

### MAIN EXECUTION ###

if __name__ == "__main__":
    print("[LyX Hebrew] Starting configuration setup...")

    # 1. Find the LyX User Directory
    lyx_user_directory = get_lyx_user_directory()
    
    if not lyx_user_directory:
        print("[LyX Hebrew] ❌ Could not determine LyX user directory.")
        sys.exit(1)
        
    # Ensure the main directory exists (if LyX was never run)
    if not os.path.exists(lyx_user_directory):
        print(f"[LyX Hebrew] User directory not found at {lyx_user_directory}. Creating it...")
        os.makedirs(lyx_user_directory, exist_ok=True)
        
    print(f"[LyX Hebrew] configuring directory: {lyx_user_directory}")

    # 2. Download Preferences (Root of user dir)
    download_file(LYX_PREFRENCES_URL, lyx_user_directory, "preferences")

    # 3. Download Bindings (bind/user.bind)
    bind_dir = os.path.join(lyx_user_directory, "bind")
    download_file(LYX_BIND_URL, bind_dir, "user.bind")

    # 4. Download Macros (Macros/Macros_Standard.lyx)
    macros_dir = os.path.join(lyx_user_directory, "Macros")
    download_file(LYX_MACROS_URL, macros_dir, "Macros_Standard.lyx")

    # 5. Download Templates (templates/Assignments.lyx)
    # Note: LyX standard folder is lowercase "templates"
    templates_dir = os.path.join(lyx_user_directory, "templates")
    download_file(LYX_TEMPLATE_URL, templates_dir, "Assignments.lyx")

    print("\n[LyX Hebrew] Configuration download complete!")
    print("[LyX Hebrew] Please restart LyX and run 'Tools > Reconfigure'.")