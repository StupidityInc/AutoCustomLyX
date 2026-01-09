#!/usr/bin/env python3
"""
LyX Hebrew Full Installer (StupidityInc)
1. Installs TeXLive (Latest).
2. Installs LyX (Flatpak preferred on Linux).
3. Scrapes & Configures Preferences, Shortcuts, Macros, and Templates.
"""

import os
import sys
import shutil
import time
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from shutil import which

# --- CONFIGURATION FROM YOUR GITHUB ---
REPO_BASE = "https://raw.githubusercontent.com/StupidityInc/lyx-config/main"
CONFIG_URLS = {
    "preferences": f"{REPO_BASE}/preferences",
    "bind/user.bind": f"{REPO_BASE}/bind/user.bind",
    "Macros/Macros_Standard.lyx": f"{REPO_BASE}/Macros/Macros_Standard.lyx",
    "templates/Assignments.lyx": f"{REPO_BASE}/Templates/Assignments.lyx"
}

# --- SYSTEM UTILITIES ---

def is_windows() -> bool:
    return sys.platform == "win32"

def is_mac() -> bool:
    return sys.platform == "darwin"

def sudo():
    return "" if is_windows() else "sudo "

def run(cmd):
    """Runs a shell command and prints it."""
    print(f"[LyX Installer] Executing: {cmd}")
    if os.system(cmd) != 0:
        print(f"[LyX Installer] ⚠️ Warning: Command failed: {cmd}")

def fetch_content(url):
    """Downloads text content from a URL."""
    try:
        print(f"[LyX Installer] Downloading: {url}")
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"[LyX Installer] ❌ Error fetching {url}: {e}")
        return None

# --- TEXLIVE INSTALLATION ---

def get_texlive_install_dir():
    return "C:\\texlive" if is_windows() else "/usr/local/texlive"

def get_texlive_bin_dir():
    """Finds the binary directory of the latest TeXLive installation."""
    base = get_texlive_install_dir()
    if not os.path.exists(base):
        return None
    
    try:
        # Find the folder with the highest number (year)
        years = sorted([d for d in os.listdir(base) if d.isdigit()], key=int)
        if not years: return None
        latest_year = years[-1]
        
        bin_root = os.path.join(base, latest_year, "bin")
        if not os.path.exists(bin_root): return None

        # Inside 'bin', there is usually one folder for the architecture (e.g., x86_64-linux)
        arch_dirs = [d for d in os.listdir(bin_root) if os.path.isdir(os.path.join(bin_root, d))]
        if len(arch_dirs) == 1:
            return os.path.join(bin_root, arch_dirs[0])
        return None
    except Exception:
        return None

def install_texlive():
    """Downloads and installs the latest TeXLive."""
    print("\n--- 1. Checking TeXLive ---")
    
    # If using Flatpak LyX, we might not strictly need system TeXLive, 
    # but for a "from 0" robust install, we install it.
    if which("flatpak") and not is_windows():
        print("[LyX Installer] Flatpak detected. Flatpak LyX usually bundles its own TeX dependencies.")
        print("[LyX Installer] Skipping System TeXLive install to save time/space.")
        return None

    if get_texlive_bin_dir():
        print(f"[LyX Installer] TeXLive already found at: {get_texlive_bin_dir()}")
        return get_texlive_bin_dir()

    print("[LyX Installer] Downloading TeXLive Installer (netinstall)...")
    
    url = "https://mirror.ctan.org/systems/texlive/tlnet/install-tl.zip" if is_windows() else \
          "https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz"
    
    archive_name = "install-tl.zip" if is_windows() else "install-tl.tar.gz"
    
    # Download
    try:
        with urllib.request.urlopen(url) as res, open(archive_name, 'wb') as f:
            f.write(res.read())
    except Exception as e:
        print(f"❌ Download failed: {e}")
        sys.exit(1)

    # Extract & Install
    extract_cmd = f"tar -xf {archive_name}" if not is_windows() else f"powershell Expand-Archive -Path {archive_name} -DestinationPath ."
    run(extract_cmd)
    
    # Find extracted folder (it usually has a variable name like install-tl-20240101)
    extracted_folder = next((d for d in os.listdir(".") if d.startswith("install-tl") and os.path.isdir(d)), None)
    
    if not extracted_folder:
        print("❌ Could not find extracted TeXLive folder.")
        sys.exit(1)

    print("[LyX Installer] Running TeXLive Installer (this may take a while)...")
    install_script = os.path.join(extracted_folder, "install-tl-windows.bat") if is_windows() else \
                     os.path.join(extracted_folder, "install-tl")
    
    # Run non-interactive installation
    run(f"{sudo()}{install_script} --scheme basic --no-interaction")
    
    # Cleanup
    if os.path.exists(archive_name): os.remove(archive_name)
    if os.path.exists(extracted_folder): shutil.rmtree(extracted_folder)
    
    # Post-Install: Install Hebrew Packages
    bin_dir = get_texlive_bin_dir()
    if bin_dir:
        tlmgr = os.path.join(bin_dir, "tlmgr")
        print("[LyX Installer] Installing Hebrew support packages...")
        run(f"{sudo()}{tlmgr} install babel-hebrew hebrew-fonts culmus")
    
    return bin_dir

# --- LYX INSTALLATION ---

def install_lyx_app():
    print("\n--- 2. Installing LyX ---")
    
    if is_windows():
        if which("winget"):
            run("winget install lyx.lyx")
        else:
            print("❌ Please install LyX manually or install Winget.")
    elif is_mac():
        if which("brew"):
            run("brew install --cask lyx")
        else:
            print("❌ Brew not found. Install Homebrew first.")
    else:
        # Linux
        if which("flatpak"):
            print("[LyX Installer] Installing via Flatpak (Preferred)...")
            run("flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo")
            run("flatpak install --user -y flathub org.lyx.LyX")
            # Permissions
            run("flatpak override --user --filesystem=host org.lyx.LyX")
            # Expose Fonts
            for font_path in [Path.home()/".fonts", Path.home()/".local/share/fonts", "/usr/share/fonts"]:
                if os.path.exists(font_path):
                    run(f"flatpak override --user --filesystem={font_path} org.lyx.LyX")
        else:
            run(f"{sudo()}apt-get update && {sudo()}apt-get install -y lyx")

def get_lyx_user_dir():
    """Determines where LyX stores user config."""
    # 1. Flatpak Check
    flatpak_path = Path.home() / ".var/app/org.lyx.LyX/config/lyx"
    if flatpak_path.exists():
        return flatpak_path

    # 2. Native OS Paths
    if is_windows():
        roaming = os.environ.get("APPDATA")
        if roaming:
            # Look for existing folder
            candidates = sorted([d for d in os.listdir(roaming) if d.startswith("LyX")])
            if candidates: return Path(roaming) / candidates[-1]
            return Path(roaming) / "LyX2.4"
    elif is_mac():
        support = Path(os.path.expanduser("~/Library/Application Support"))
        candidates = sorted([d for d in os.listdir(support) if d.startswith("LyX")])
        if candidates: return support / candidates[-1]
        return support / "LyX-2.4"
    else:
        return Path.home() / ".lyx"
    
    return None

def init_lyx_folder():
    """Runs LyX briefly to ensure folder structure exists."""
    print("[LyX Installer] Initializing LyX folder structure...")
    
    if is_windows():
        # Windows initialization is tricky without path, relying on folder creation
        pass 
    elif which("flatpak") and (Path.home() / ".var/app/org.lyx.LyX").exists():
        # Run dummy command in flatpak
        try:
            subprocess.run(["flatpak", "run", "--command=lyx", "org.lyx.LyX", "-e", "info"], timeout=10)
        except: pass
    else:
        # Native Linux/Mac
        if which("lyx"):
            try:
                subprocess.run(["lyx", "-e", "info"], timeout=10)
            except: pass

# --- CONFIGURATION SCRAPING ---

def setup_configs(tex_bin_path):
    print("\n--- 3. Configuring LyX (Scraping from GitHub) ---")
    
    user_dir = get_lyx_user_dir()
    if not user_dir:
        print("❌ Could not determine LyX user directory.")
        return

    # Ensure main dir exists
    if not user_dir.exists():
        user_dir.mkdir(parents=True, exist_ok=True)

    print(f"[LyX Installer] User Directory: {user_dir}")

    # Process each file
    for local_rel_path, url in CONFIG_URLS.items():
        # Determine local destination
        dest_path = user_dir / local_rel_path
        
        # Create parent directories (bind, Macros, templates)
        if not dest_path.parent.exists():
            print(f"[LyX Installer] Creating folder: {dest_path.parent.name}")
            dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download Content
        content = fetch_content(url)
        if content:
            # SPECIAL CASE: Preferences
            # We need to inject the TeXLive path if we installed it manually
            if "preferences" in local_rel_path and tex_bin_path:
                if "\\path_prefix" not in content:
                    print(f"[LyX Installer] Injecting TeXLive path into preferences: {tex_bin_path}")
                    content += f'\n\\path_prefix "{tex_bin_path}"\n'
            
            # Write to file
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[LyX Installer] ✅ Installed: {local_rel_path}")

# --- MAIN ---

if __name__ == "__main__":
    print("=== StupidityInc LyX Installer (Zero-to-Hero) ===")
    
    # 1. Install TeXLive (returns path to binaries)
    tex_path = install_texlive()
    
    # 2. Install LyX Application
    install_lyx_app()
    
    # 3. Initialize & Configure
    init_lyx_folder()
    
    # Wait a moment for folder generation if it was just created
    time.sleep(2)
    
    setup_configs(tex_path)
    
    print("\n=== Installation Complete ===")
    print("1. Restart LyX.")
    print("2. Run 'Tools > Reconfigure'.")
    print("3. Enjoy Hebrew LyX!")