"""
LyX Hebrew Hybrid Installer
1. Runs the Standard Installation (TeXLive + LyX).
2. Scrapes YOUR custom configs from GitHub and overwrites the defaults.
"""

import os
import subprocess
import sys
import time
import urllib.request
from shutil import rmtree, which
from urllib.request import urlopen
from pathlib import Path

# --- YOUR CUSTOM CONFIG ---
REPO_BASE = "https://raw.githubusercontent.com/StupidityInc/lyx-config/main"
CUSTOM_FILES = {
    "preferences": "preferences",
    "bind/user.bind": "bind/user.bind",
    "Macros/Macros_Standard.lyx": "Macros/Macros_Standard.lyx",
    "Templates/Assignments.lyx": "templates/Assignments.lyx"
}

### UTILITIES (Standard Script) ###

def is_windows() -> bool:
    return sys.platform == "win32"

def sudo():
    return "sudo " if not is_windows() else ""

def run(command: str):
    if os.system(command) != 0:
        print(f"[LyX Installer] Warning: Command failed: {command}")

### TEXLIVE & LYX INSTALLATION (Standard Script) ###

def download_texlive_installer() -> str:
    installer_url = "https://mirror.ctan.org/systems/texlive/tlnet/install-tl.zip" if is_windows() else \
                    "https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz"
    archive_name = "install-tl.zip" if is_windows() else "install-tl.tar.gz"
    
    with urlopen(installer_url) as res, open(archive_name, "wb") as f:
        f.write(res.read())

    if os.path.exists("install-tl"): rmtree("install-tl")
    
    run(f"mkdir install-tl && tar -xf {archive_name} -C install-tl --strip-components=1")
    os.remove(archive_name)
    
    return ".\\install-tl\\install-tl-windows.bat -no-gui" if is_windows() else "./install-tl/install-tl"

def cleanup_texlive():
    if os.path.exists("install-tl"): rmtree("install-tl")

def get_texlive_dir():
    return "C:\\texlive" if is_windows() else "/usr/local/texlive"

def get_texlive_bin_dir():
    # Helper to find the dynamic path (e.g., /2024/bin/x86_64-linux)
    base = get_texlive_dir()
    if not os.path.exists(base): return None
    try:
        years = sorted([d for d in os.listdir(base) if d.isdigit()], key=int)
        if not years: return None
        bin_root = os.path.join(base, years[-1], "bin")
        if not os.path.exists(bin_root): return None
        archs = [d for d in os.listdir(bin_root) if os.path.isdir(os.path.join(bin_root, d))]
        return os.path.join(bin_root, archs[0]) if archs else None
    except: return None

def install_lyx():
    # Your original logic (prioritizing Flatpak for Linux)
    if is_windows():
        if which("winget"): run("winget install lyx.lyx")
    elif sys.platform == "darwin":
        if which("brew"): run("brew install lyx")
    else:
        if which("flatpak"):
            run("flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo")
            run("flatpak install --user -y flathub org.lyx.LyX")
            run("flatpak override --user --filesystem=host org.lyx.LyX")
        elif which("apt-get"):
            run("sudo apt-get install -y lyx")

def get_lyx_user_dir():
    # 1. Check Flatpak
    fp = Path.home() / ".var/app/org.lyx.LyX/config/lyx"
    if fp.exists(): return str(fp)
    # 2. Native
    if is_windows():
        roaming = os.environ["APPDATA"]
        cands = sorted([f for f in os.listdir(roaming) if f.startswith("LyX")])
        return os.path.join(roaming, cands[-1]) if cands else None
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
        cands = sorted([f for f in os.listdir(base) if f.startswith("LyX")])
        return os.path.join(base, cands[-1]) if cands else None
    return os.path.expanduser("~/.lyx")

def init_lyx():
    # Runs LyX briefly to create folders
    if which("flatpak") and os.path.exists(Path.home() / ".var/app/org.lyx.LyX"):
        try: subprocess.run(["flatpak", "run", "--command=lyx", "org.lyx.LyX", "-e", "info"], timeout=10)
        except: pass
    elif which("lyx"):
        try: subprocess.run(["lyx", "-e", "info"], timeout=10)
        except: pass

### THE NEW PART: SCRAPER ###

def apply_custom_configs(tex_bin):
    print("\n[LyX Installer] Applying StupidityInc Configurations...")
    user_dir = get_lyx_user_dir()
    if not user_dir: return

    for remote, local in CUSTOM_FILES.items():
        url = f"{REPO_BASE}/{remote}"
        dest = os.path.join(user_dir, local)
        
        # Ensure folder exists
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        
        try:
            print(f"Downloading {local}...")
            with urllib.request.urlopen(url) as response:
                content = response.read().decode('utf-8')
                
                # MAGIC FIX: Inject the correct TeX path into preferences
                if "preferences" in local and tex_bin:
                    # Remove any existing path_prefix to avoid duplicates/conflicts
                    lines = [l for l in content.splitlines() if "\\path_prefix" not in l]
                    # Add the correct one
                    lines.append(f'\\path_prefix "{tex_bin}"')
                    content = "\n".join(lines)

                with open(dest, "w", encoding="utf-8") as f:
                    f.write(content)
        except Exception as e:
            print(f"❌ Error downloading {local}: {e}")

### MAIN ###

if __name__ == "__main__":
    # 1. Install TeXLive (Standard Logic)
    tex_bin = get_texlive_bin_dir()
    if not tex_bin:
        print("[LyX Installer] Installing TeXLive...")
        inst = download_texlive_installer()
        run(f"{sudo()}{inst} --scheme basic --no-interaction")
        cleanup_texlive()
        
        # Install Packages
        tex_bin = get_texlive_bin_dir()
        if tex_bin:
            tlmgr = os.path.join(tex_bin, "tlmgr")
            run(f"{sudo()}{tlmgr} install babel-hebrew hebrew-fonts culmus")

    # 2. Install LyX (Standard Logic)
    install_lyx()
    init_lyx()
    
    # 3. APPLY CUSTOM CONFIGS (The "Add at the end" part)
    # This overwrites the default files with your GitHub files
    apply_custom_configs(tex_bin)

    print("\n[LyX Installer] Done! Restart LyX and run Tools > Reconfigure.")