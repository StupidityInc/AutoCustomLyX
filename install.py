"""
LyX Hebrew Installation Script
Installs TeXLive, required packages and LyX.
"""

import os
import subprocess
import sys
import time
from shutil import rmtree, which
from urllib.request import urlopen
import requests

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


def is_windows() -> bool:
    return sys.platform == "win32"


def sudo():
    return "sudo " if not is_windows() else ""


def panic(message: str):
    print(f"[LyX Hebrew] {message}")
    exit(-1)


def prompt(message: str):
    if not input(f"[LyX Hebrew] {message} [y/n]: ").lower().startswith("y"):
        panic("Aborting installation.")


def run(command: str):
    if os.system(command) != 0:
        prompt("It seems the last command failed. Do you still wish to continue?")


### TEXLIVE ###


def download_texlive_installer() -> str:
    """Downloads the TeXLive Installer (https://www.tug.org/texlive/acquire-netinstall.html) and returns the path to it. Should support Windows, macOS and Linux."""
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

    run(
        f"mkdir install-tl && tar -xf {installer_archive_filename} -C install-tl --strip-components=1"
    )
    os.remove(installer_archive_filename)
    return (
        ".\\install-tl\\install-tl-windows.bat -no-gui"
        if is_windows()
        else "./install-tl/install-tl"
    )


def cleanup_texlive_installer():
    rmtree("install-tl")


def get_texlive_installation_directory():
    return "C:\\texlive" if is_windows() else "/usr/local/texlive"


def get_latest_texlive_installation_directory():
    installation_directory = get_texlive_installation_directory()
    last_installation = sorted(
        [int(s) for s in os.listdir(installation_directory) if s.isnumeric()]
    )[-1]

    return os.path.join(installation_directory, str(last_installation))


def get_texlive_binary_directory():
    bin_directory = os.path.join(get_latest_texlive_installation_directory(), "bin")
    # The bin directory should only contain a single folder with binaries for the host OS
    contents = os.listdir(bin_directory)
    assert len(contents) == 1
    return os.path.join(bin_directory, contents[0])


### LYX ###


def install_lyx():
    if sys.platform == "win32":
        if which("winget") is not None:
            run("winget install lyx.lyx")
        elif which("choco") is not None:
            run("choco install lyx")
        else:
            installer = urlopen(
                "https://lyx.mirror.garr.it/bin/2.3.7/LyX-237-Installer-1-x64.exe"
            ).read()
            with open("lyx-installer.exe", "wb") as installer_file:
                installer_file.write(installer)
            current_directory = os.path.abspath(".")
            os.chdir(get_texlive_binary_directory())
            run(f"{os.path.join(current_directory, 'lyx-installer.exe')} /S")
            os.chdir(current_directory)
            os.remove("lyx-installer.exe")
    elif sys.platform == "darwin":
        if which("brew") is not None:
            run("brew install lyx")
        else:
            panic("Please install Homebrew on your system: https://brew.sh/")
    else:
        if which("apt-get") is not None:
            run("sudo apt-get install lyx")
        elif which("dnf") is not None:
            run("sudo dnf install lyx")
        elif which("yay") is not None:
            run("yay -S lyx")
        elif which("paru") is not None:
            run("paru -S lyx")
        else:
            prompt(
                "Please install LyX using your package manager and then run the installation script again. Have you installed LyX?"
            )


def get_lyx_user_directory():
    """https://wiki.lyx.org/LyX/UserDir"""

    if sys.platform == "win32":
        roaming = os.environ["APPDATA"]
        roaming_contents = os.listdir(roaming)
        latest_lyx = sorted([f for f in roaming_contents if f.startswith("LyX")])
        if len(latest_lyx) != 0:
            return os.path.join(roaming, latest_lyx[-1])
    elif sys.platform == "darwin":
        application_support = os.path.expanduser("~/Library/Application Support")
        application_support_contents = os.listdir(application_support)
        latest_lyx = sorted(
            [f for f in application_support_contents if f.startswith("LyX")]
        )
        if len(latest_lyx) != 0:
            return os.path.join(application_support, latest_lyx[-1])
    else:
        return os.path.expanduser("~/.lyx")


def get_lyx_library_directory():
    """https://wiki.lyx.org/LyX/SystemDir"""

    if sys.platform == "win32":
        for base_directory in [
            os.path.join(os.environ["APPDATA"], "..", "Local"),
            os.path.join(os.environ["APPDATA"], "..", "Local", "Programs"),
            "C:\\Program Files (x86)",
            "C:\\Program Files",
        ]:
            contents = os.listdir(base_directory)
            latest_lyx = sorted([f for f in contents if f.startswith("LyX")])
            if len(latest_lyx) != 0:
                return os.path.join(base_directory, latest_lyx[-1])
    elif sys.platform == "darwin":
        return "/Applications/LyX.app/Contents/Resources"
    else:
        return "/usr/local/share/lyx/"


def open_and_close_lyx():
    if sys.platform == "darwin":
        if os.system("open -a LyX") != 0:
            print(
                "Please manually open the LyX app and immediately close it, and then press enter."
            )
            input(
                "You may need to right click it and then click 'Open Anyway' to do so. "
            )
        time.sleep(10)
        os.system("""osascript -e 'quit app "LyX"'""")
    else:
        lyx = (
            os.path.join(get_lyx_library_directory(), "bin", "LyX.exe")
            if is_windows()
            else "/usr/bin/lyx"
        )
        p = subprocess.Popen([lyx])
        time.sleep(10)
        p.kill()

def download_github_file(raw_url, folder_path, file_name):
    try:
        # Validate inputs
        if not raw_url or not folder_path or not file_name:
            raise ValueError("raw_url, folder_path, and file_name cannot be empty")
        
        local_path = os.path.join(folder_path, file_name)
        print(f"Downloading from: {raw_url}")
        
        # Create directory
        try:
            os.makedirs(folder_path, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create directory '{folder_path}': {e}")
        
        # Download file with shorter timeout
        try:
            print("Connecting...")
            response = requests.get(raw_url, timeout=5)  # Reduced to 5 seconds
            response.raise_for_status()
            print(f"Downloaded {len(response.content)} bytes")
        except requests.exceptions.Timeout:
            raise requests.exceptions.Timeout(f"Connection timed out (5s) for URL: {raw_url}")
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError(f"Failed to connect to {raw_url}")
        except requests.exceptions.HTTPError:
            raise requests.exceptions.HTTPError(f"HTTP error {response.status_code} for URL: {raw_url}")
        
        # Write file
        try:
            with open(local_path, 'wb') as f:
                f.write(response.content)
        except IOError as e:
            raise IOError(f"Failed to write file '{local_path}': {e}")
        
        print(f'Success: {local_path}')
        return True
    
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')
        return False

# Usage
download_github_file(
    'https://raw.githubusercontent.com/StupidityInc/lyx-config/main/preferences',
    '/home/uri',
    'test'
)


if __name__ == "__main__":
    # Bad installation of texlive: no tlmgr
    if os.path.exists(get_texlive_installation_directory()) and (
        not os.path.exists(
            os.path.join(get_latest_texlive_installation_directory(), "bin")
        )
        or len(
            os.listdir(os.path.join(get_latest_texlive_installation_directory(), "bin"))
        )
        == 0
        or not os.path.exists(
            os.path.join(
                get_texlive_binary_directory(), "tlmgr.bat" if is_windows() else "tlmgr"
            )
        )
    ):
        rmtree(get_texlive_installation_directory())
        print("[LyX Hebrew] Done removing bad installation of texlive.")

    if (
        not os.path.exists(get_texlive_installation_directory())
        or len(os.listdir(get_texlive_installation_directory())) == 0
    ):
        print("[LyX Hebrew] Downloading texlive installer...")
        installer = download_texlive_installer()
        print("[LyX Hebrew] Done downloading texlive installer.")

        print("[LyX Hebrew] Installing texlive...")
        run(f"{sudo()}{installer} --scheme basic --no-interaction")
        print("[LyX Hebrew] Done installing texlive.")

        cleanup_texlive_installer()

    print("[LyX Hebrew] Installing packages using tlmgr...")
    texlive_binary_directory = get_texlive_binary_directory()
    tlmgr = os.path.join(texlive_binary_directory, "tlmgr")
    run(f"{sudo()}{tlmgr} install babel-hebrew hebrew-fonts culmus")
    print("[LyX Hebrew] Done installing packages using tlmgr.")

    try:
        lyx = os.path.join(get_lyx_library_directory(), "bin", "LyX.exe")
        if not os.path.exists(lyx):
            raise Exception()
    except:
        print("[LyX Hebrew] Installing LyX...")
        install_lyx()
        print("[LyX Hebrew] Done installing LyX.")

    if get_lyx_user_directory() is None or not os.path.exists(get_lyx_user_directory()):
        print(
            "[LyX Hebrew] Opening and closing LyX to initialize the user directory. There's no need to interact with it!"
        )
        open_and_close_lyx()
        print("[LyX Hebrew] Closed LyX after it initialized the user directory.")

    if get_lyx_user_directory() is None or not os.path.exists(get_lyx_user_directory()):
        print("[LyX Hebrew] Unable to find LyX User Directory.")
        print('[LyX Hebrew] Please open and close LyX manually to create them, and then press "Enter".')
        print("[LyX Hebrew] If LyX is not installed, please retry the installation.")
        input()

    print("[LyX Hebrew] Setting up settings for hebrew...")
    lyx_user_directory = get_lyx_user_directory()
    preferences_file = os.path.join(lyx_user_directory, "preferences")
    with open(preferences_file, "a") as preferences:
        preferences.write(
            f"""
\\kbmap true
\\kbmap_primary "null"
\\kbmap_secondary "hebrew"
\\visual_cursor true
\\path_prefix "{texlive_binary_directory}"
""".strip()
            + "\n"
        )

    user_bind_file = os.path.join(lyx_user_directory, "bind", "user.bind")
    with open(user_bind_file, "a") as user_bind:
        user_bind.write(
            """
\\bind "A-space" "language hebrew"
""".strip()
            + "\n"
        )

    default_template_file = os.path.join(
        lyx_user_directory, "templates", "defaults.lyx"
    )
    with open(default_template_file, "w") as default_template:
        default_template.write(
            """
#LyX 2.3 created this file. For more info see http://www.lyx.org/
\\lyxformat 544
\\begin_document
\\begin_header
\\save_transient_properties true
\\origin unavailable
\\textclass heb-article
\\begin_preamble
\\usepackage[use-david]{culmus}
\\end_preamble
\\use_default_options true
\\maintain_unincluded_children false
\\language hebrew
\\language_package default
\\inputencoding auto
\\fontencoding global
\\font_roman "default" "default"
\\font_sans "default" "default"
\\font_typewriter "default" "default"
\\font_math "auto" "auto"
\\font_default_family default
\\use_non_tex_fonts false
\\font_sc false
\\font_osf false
\\font_sf_scale 100 100
\\font_tt_scale 100 100
\\use_microtype false
\\use_dash_ligatures true
\\graphics default
\\default_output_format default
\\output_sync 0
\\bibtex_command default
\\index_command default
\\paperfontsize default
\\spacing single
\\use_hyperref false
\\papersize default
\\use_geometry true
\\use_package amsmath 1
\\use_package amssymb 1
\\use_package cancel 1
\\use_package esint 1
\\use_package mathdots 1
\\use_package mathtools 1
\\use_package mhchem 1
\\use_package stackrel 1
\\use_package stmaryrd 1
\\use_package undertilde 1
\\cite_engine basic
\\cite_engine_type default
\\biblio_style plain
\\use_bibtopic false
\\use_indices false
\\paperorientation portrait
\\suppress_date false
\\justification true
\\use_refstyle 1
\\use_minted 0
\\index Index
\\shortcut idx
\\color #008000
\\end_index
\\leftmargin 1.5cm
\\topmargin 2cm
\\rightmargin 1.5cm
\\bottommargin 2cm
\\secnumdepth 3
\\tocdepth 3
\\paragraph_separation indent
\\paragraph_indentation default
\\is_math_indent 0
\\math_numbering_side default
\\quotes_style english
\\dynamic_quotes 0
\\papercolumns 1
\\papersides 1
\\paperpagestyle default
\\tracking_changes false
\\output_changes false
\\html_math_output 0
\\html_css_as_file 0
\\html_be_strict false
\\end_header

\\begin_body

\\begin_layout Standard

\\end_layout

\\end_body
\\end_document
            """.strip()
            + "\n"
        )
    print("[LyX Hebrew] Done setting up settings for hebrew")
    print("[LyX Hebrew] Installation is complete!")
    print(
        "[LyX Hebrew] You may now use LyX and hebrew should work for you. Make sure to keep your system language as English, and if you want to type English in your document use Alt+Space to switch to it."
    )
