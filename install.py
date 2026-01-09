"""
LyX Hebrew Installation Script (StupidityInc Version)
Installs TeXLive, required packages, LyX, and scrapes custom configs.
"""

import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from shutil import rmtree, which
from urllib.request import urlopen
from pathlib import Path

# --- CONFIGURATION ---
CONFIG_REPO_RAW = "https://raw.githubusercontent.com/StupidityInc/lyx-config/main"

### UTILITIES ###

def is_windows() -> bool:
    return sys.platform == "win32"

def sudo():
    return "sudo " if not is_windows() else ""

def panic(message: str):
    print(f"[LyX Hebrew] {message}")
    sys.exit(-1)

def prompt(message: str):
    try:
        if not input(f"[LyX Hebrew] {message} [y/n]: ").lower().startswith("y"):
            panic("Aborting installation.")
    except EOFError:
        pass 

def run(command: str):
    if os.system(command) != 0:
        print(f"[LyX Hebrew] Warning: Command '{command}' failed.")

def fetch_raw(remote_path):
    """Downloads a raw file from the config repo."""
    url = f"{CONFIG_REPO_RAW}/{remote_path}"
    try:
        print(f"[LyX Hebrew] Downloading {remote_path}...")
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        print(f"[LyX Hebrew] ❌ Error downloading {remote_path}: {e}")
        return None
    except Exception as e:
        print(f"[LyX Hebrew] ❌ Unexpected error: {e}")
        return None

### TEXLIVE & LYX INSTALLATION LOGIC ###

def download_texlive_installer() -> str:
    installer_url = (
        "https://mirror.ctan.org/systems/texlive/tlnet/install-tl.zip"
        if is_windows()
        else "https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz"
    )
    installer_archive_filename = (
        "install-tl.zip" if is_windows() else "install-tl-unx.tar.gz"
    )
    installer = urlopen(installer_url).read()
    with open(installer_archive_filename, "wb") as installer_file:
        installer_file.write(installer)

    if os.path.exists("install-tl"):
        rmtree("install-tl")

    run(f"mkdir install-tl && tar -xf {installer_archive_filename} -C install-tl --strip-components=1")
    os.remove(installer_archive_filename)
    return (
        ".\\install-tl\\install-tl-windows.bat -no-gui"
        if is_windows()
        else "./install-tl/install-tl"
    )

def cleanup_texlive_installer():
    if os.path.exists("install-tl"):
        rmtree("install-tl")

def get_texlive_installation_directory():
    return "C:\\texlive" if is_windows() else "/usr/local/texlive"

def get_latest_texlive_installation_directory():
    installation_directory = get_texlive_installation_directory()
    if not os.path.exists(installation_directory):
        return None
    try:
        last_installation = sorted(
            [int(s) for s in os.listdir(installation_directory) if s.isnumeric()]
        )[-1]
        return os.path.join(installation_directory, str(last_installation))
    except IndexError:
        return None

def get_texlive_binary_directory():
    latest = get_latest_texlive_installation_directory()
    if not latest: return None
    bin_directory = os.path.join(latest, "bin")
    if not os.path.exists(bin_directory): return None
    contents = os.listdir(bin_directory)
    dirs = [d for d in contents if os.path.isdir(os.path.join(bin_directory, d))]
    if len(dirs) == 1:
        return os.path.join(bin_directory, dirs[0])
    return None

def install_lyx():
    if sys.platform == "win32":
        if which("winget") is not None:
            run("winget install lyx.lyx")
        elif which("choco") is not None:
            run("choco install lyx")
        else:
            print("Downloading LyX installer...")
            installer = urlopen("https://lyx.mirror.garr.it/bin/2.3.7/LyX-237-Installer-1-x64.exe").read()
            with open("lyx-installer.exe", "wb") as installer_file:
                installer_file.write(installer)
            run("lyx-installer.exe /S")
            os.remove("lyx-installer.exe")
    elif sys.platform == "darwin":
        if which("brew") is not None:
            run("brew install lyx")
        else:
            panic("Please install Homebrew: https://brew.sh/")
    else:
        # Check for Flatpak first
        if which("flatpak") is not None:
            print("[LyX Hebrew] Installing via Flatpak...")
            run("flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo")
            run("flatpak install --user -y flathub org.lyx.LyX")
            run("flatpak override --user --filesystem=host org.lyx.LyX")
            for font_path in [Path.home()/".fonts", Path.home()/".local/share/fonts", "/usr/share/fonts"]:
                 if os.path.exists(font_path):
                     run(f"flatpak override --user --filesystem={font_path} org.lyx.LyX")
        elif which("apt-get") is not None:
            run("sudo apt-get install -y lyx")
        elif which("dnf") is not None:
            run("sudo dnf install lyx")
        elif which("yay") is not None:
            run("yay -S lyx")
        else:
            prompt("Please install LyX manually.")

def get_lyx_user_directory():
    """Locates the LyX user folder, prioritizing Flatpak if present."""
    flatpak_path = Path.home() / ".var/app/org.lyx.LyX/config/lyx"
    if flatpak_path.exists():
        return str(flatpak_path)

    if sys.platform == "win32":
        roaming = os.environ["APPDATA"]
        roaming_contents = os.listdir(roaming)
        latest_lyx = sorted([f for f in roaming_contents if f.startswith("LyX")])
        if len(latest_lyx) != 0:
            return os.path.join(roaming, latest_lyx[-1])
    elif sys.platform == "darwin":
        application_support = os.path.expanduser("~/Library/Application Support")
        if os.path.exists(application_support):
            application_support_contents = os.listdir(application_support)
            latest_lyx = sorted([f for f in application_support_contents if f.startswith("LyX")])
            if len(latest_lyx) != 0:
                return os.path.join(application_support, latest_lyx[-1])
    else:
        return os.path.expanduser("~/.lyx")

def get_lyx_library_directory():
    """Locates the system LyX directory (needed for finding the exe on Windows)."""
    if sys.platform == "win32":
        for base_directory in [
            os.path.join(os.environ["APPDATA"], "..", "Local"),
            os.path.join(os.environ["APPDATA"], "..", "Local", "Programs"),
            "C:\\Program Files (x86)",
            "C:\\Program Files",
        ]:
            if os.path.exists(base_directory):
                contents = os.listdir(base_directory)
                latest_lyx = sorted([f for f in contents if f.startswith("LyX")])
                if len(latest_lyx) != 0:
                    return os.path.join(base_directory, latest_lyx[-1])
    elif sys.platform == "darwin":
        return "/Applications/LyX.app/Contents/Resources"
    else:
        return "/usr/local/share/lyx/"

def open_and_close_lyx():
    """Runs LyX briefly to generate the initial folder structure."""
    print("[LyX Hebrew] Initializing user directory...")
    if which("flatpak") and os.path.exists(Path.home() / ".var/app/org.lyx.LyX"):
         try:
             subprocess.run(["flatpak", "run", "--command=lyx", "org.lyx.LyX", "-e", "info"], timeout=10)
         except subprocess.TimeoutExpired:
             pass
         except Exception as e:
             print(f"Flatpak init warning: {e}")
    elif sys.platform == "darwin":
        os.system("open -a LyX")
        time.sleep(5)
        os.system("osascript -e 'quit app \"LyX\"'")
    else:
        lyx_bin = "lyx"
        if is_windows():
             lib_dir = get_lyx_library_directory()
             if lib_dir: lyx_bin = os.path.join(lib_dir, "bin", "LyX.exe")
        
        try:
            subprocess.run([lyx_bin, "-e", "info"], timeout=10) 
        except:
            pass

### MAIN EXECUTION ###

if __name__ == "__main__":
    
    # 1. TEXLIVE CHECK
    tex_dir = get_texlive_installation_directory()
    tex_bin = get_texlive_binary_directory()
    
    if not is_windows() and which("flatpak"):
        print("[LyX Hebrew] Detected Flatpak environment. Skipping system TeXLive check.")
    elif (not tex_dir or not os.path.exists(tex_dir) or not tex_bin):
        print("[LyX Hebrew] TeXLive not found. Installing...")
        installer = download_texlive_installer()
        run(f"{sudo()}{installer} --scheme basic --no-interaction")
        cleanup_texlive_installer()
        
        print("[LyX Hebrew] Installing Hebrew packages...")
        tex_bin = get_texlive_binary_directory()
        if tex_bin:
            tlmgr = os.path.join(tex_bin, "tlmgr")
            run(f"{sudo()}{tlmgr} install babel-hebrew hebrew-fonts culmus")

    # 2. LYX INSTALL CHECK
    lyx_user_directory = get_lyx_user_directory()
    if not lyx_user_directory:
        print("[LyX Hebrew] LyX user directory not found. Installing/Initializing LyX...")
        install_lyx()
        open_and_close_lyx()
        lyx_user_directory = get_lyx_user_directory()
    
    if not lyx_user_directory or not os.path.exists(lyx_user_directory):
        print("[LyX Hebrew] Could not locate LyX user folder. Please open LyX once manually.")
        sys.exit(1)

    print(f"[LyX Hebrew] Configuring LyX in: {lyx_user_directory}")

    # 3. CREATE DIRECTORIES
    for folder in ["bind", "Macros", "templates"]:
        target_dir = os.path.join(lyx_user_directory, folder)
        os.makedirs(target_dir, exist_ok=True)

    # 4. SCRAPE CONFIG FILES
    
    # A. Preferences
    pref_content = fetch_raw("preferences")
    if pref_content:
        if tex_bin and "\\path_prefix" not in pref_content:
             pref_content += f'\n\\path_prefix "{tex_bin}"'
        
        with open(os.path.join(lyx_user_directory, "preferences"), "w", encoding="utf-8") as f:
            f.write(pref_content)
        print("[LyX Hebrew] Updated preferences.")

    # B. Shortcuts (user.bind)
    bind_content = fetch_raw("bind/user.bind")
    if bind_content:
        with open(os.path.join(lyx_user_directory, "bind", "user.bind"), "w", encoding="utf-8") as f:
            f.write(bind_content)
        print("[LyX Hebrew] Updated shortcuts (user.bind).")

    # C. Macros
    macro_content = fetch_raw("Macros/Macros_Standard.lyx")
    if macro_content:
        with open(os.path.join(lyx_user_directory, "Macros", "Macros_Standard.lyx"), "w", encoding="utf-8") as f:
            f.write(macro_content)
        print("[LyX Hebrew] Installed Macros.")

    # D. Templates
    template_content = fetch_raw("Templates/Assignments.lyx")
    if template_content:
        with open(os.path.join(lyx_user_directory, "templates", "Assignments.lyx"), "w", encoding="utf-8") as f:
            f.write(template_content)
        print("[LyX Hebrew] Installed Assignment Template.")

    print("\n[LyX Hebrew] Installation Complete!")