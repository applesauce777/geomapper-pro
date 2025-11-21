#!/usr/bin/env python3
"""
GeoMapper Pro - Cross-Platform Installer
Automatically detects OS and installs GeoMapper with appropriate shortcuts.

Usage:
    python install_geomap.py [--no-shortcuts] [--install-dir PATH]
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

__version__ = "2.1.0"

# ANSI colors
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'
    
    @classmethod
    def disable(cls):
        cls.RED = cls.GREEN = cls.YELLOW = cls.CYAN = cls.NC = ''

# Disable colors on Windows if not supported
if sys.platform == 'win32':
    try:
        os.system('color')
    except:
        Colors.disable()


def print_banner():
    print(f"""
{Colors.CYAN}==============================================={Colors.NC}
{Colors.CYAN}   GeoMapper Pro v{__version__} - Installer{Colors.NC}
{Colors.CYAN}==============================================={Colors.NC}
""")


def print_step(num, total, msg):
    print(f"{Colors.YELLOW}[{num}/{total}] {msg}{Colors.NC}")


def print_success(msg):
    print(f"  {Colors.GREEN}✓ {msg}{Colors.NC}")


def print_error(msg):
    print(f"  {Colors.RED}✗ {msg}{Colors.NC}")


def get_platform():
    if sys.platform == 'win32':
        return 'windows'
    elif sys.platform == 'darwin':
        return 'macos'
    else:
        return 'linux'


def get_default_install_dir(platform):
    home = Path.home()
    if platform == 'windows':
        return home / 'AppData' / 'Local' / 'GeoMapperPro'
    else:
        return home / '.local' / 'share' / 'geomapper'


def check_python():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print_error(f"Python 3.7+ required. Found: {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_dependencies(install_dir):
    req_file = install_dir / 'requirements.txt'
    try:
        if req_file.exists():
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(req_file), '-q'],
                          check=True, capture_output=True)
        else:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 
                          'pandas', 'folium', 'numpy', 'openpyxl', 'pyarrow', '-q'],
                          check=True, capture_output=True)
        print_success("Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False


def copy_files(source_dir, install_dir):
    files_to_copy = ['geomap.py', 'geomap_pro.py', 'requirements.txt', 'README.md']
    copied = 0
    
    for filename in files_to_copy:
        src = source_dir / filename
        if src.exists():
            shutil.copy2(src, install_dir / filename)
            copied += 1
    
    # Copy icons folder if exists
    icons_src = source_dir / 'icons'
    icons_dst = install_dir / 'icons'
    if icons_src.exists():
        if icons_dst.exists():
            shutil.rmtree(icons_dst)
        shutil.copytree(icons_src, icons_dst)
        copied += 1
    
    print_success(f"Copied {copied} files to {install_dir}")
    return True


def create_windows_shortcuts(install_dir):
    """Create Windows shortcuts and batch file."""
    # Create batch launcher
    batch_path = install_dir / 'geomap.bat'
    batch_content = f'@echo off\npython "{install_dir / "geomap.py"}" %*\n'
    batch_path.write_text(batch_content)
    
    # Create PowerShell shortcut script
    ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Desktop = [Environment]::GetFolderPath("Desktop")
$Shortcut = $WshShell.CreateShortcut("$Desktop\\GeoMapper Pro.lnk")
$Shortcut.TargetPath = "cmd.exe"
$Shortcut.Arguments = '/k cd /d "{install_dir}" && echo GeoMapper Pro Ready && echo. && echo Type: python geomap.py --help'
$Shortcut.WorkingDirectory = "{install_dir}"
$IconPath = "{install_dir}\\icons\\GeoMapperPro.ico"
if (Test-Path $IconPath) {{ $Shortcut.IconLocation = $IconPath }}
$Shortcut.Save()
'''
    
    try:
        subprocess.run(['powershell', '-Command', ps_script], 
                      check=True, capture_output=True)
        print_success("Created Desktop shortcut")
    except:
        print_error("Could not create shortcut (run as admin or create manually)")
    
    return True


def create_macos_app(install_dir):
    """Create macOS .app bundle."""
    home = Path.home()
    app_dir = home / 'Applications' / 'GeoMapper Pro.app'
    
    # Create structure
    contents = app_dir / 'Contents'
    macos = contents / 'MacOS'
    resources = contents / 'Resources'
    
    for d in [macos, resources]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Info.plist
    plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key><string>GeoMapperPro</string>
    <key>CFBundleIdentifier</key><string>com.geomapper.pro</string>
    <key>CFBundleName</key><string>GeoMapper Pro</string>
    <key>CFBundleVersion</key><string>{__version__}</string>
    <key>CFBundleIconFile</key><string>GeoMapperPro</string>
    <key>CFBundlePackageType</key><string>APPL</string>
</dict>
</plist>'''
    (contents / 'Info.plist').write_text(plist)
    
    # Launcher
    launcher = f'''#!/bin/bash
osascript -e 'tell app "Terminal" to do script "cd {install_dir} && echo GeoMapper Pro v{__version__} && python3 geomap.py --help"'
'''
    launcher_path = macos / 'GeoMapperPro'
    launcher_path.write_text(launcher)
    launcher_path.chmod(0o755)
    
    # Copy icon
    icon_src = install_dir / 'icons' / 'GeoMapperPro.icns'
    if icon_src.exists():
        shutil.copy2(icon_src, resources / 'GeoMapperPro.icns')
    
    print_success(f"Created {app_dir}")
    
    # CLI wrapper
    bin_dir = home / '.local' / 'bin'
    bin_dir.mkdir(parents=True, exist_ok=True)
    wrapper = bin_dir / 'geomap'
    wrapper.write_text(f'#!/bin/bash\npython3 "{install_dir}/geomap.py" "$@"\n')
    wrapper.chmod(0o755)
    print_success("Created CLI wrapper: ~/.local/bin/geomap")
    
    return True


def create_linux_desktop(install_dir):
    """Create Linux .desktop file and CLI wrapper."""
    home = Path.home()
    
    # .desktop file
    desktop_dir = home / '.local' / 'share' / 'applications'
    desktop_dir.mkdir(parents=True, exist_ok=True)
    
    icon_path = install_dir / 'icons' / 'GeoMapperPro.png'
    
    desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name=GeoMapper Pro
Comment=Transform geographic data into interactive maps
Exec=x-terminal-emulator -e bash -c "cd {install_dir} && echo 'GeoMapper Pro v{__version__}' && bash"
Icon={icon_path}
Terminal=false
Categories=Science;Geography;Development;
'''
    
    desktop_file = desktop_dir / 'geomapper-pro.desktop'
    desktop_file.write_text(desktop_content)
    print_success("Created .desktop launcher")
    
    # CLI wrapper
    bin_dir = home / '.local' / 'bin'
    bin_dir.mkdir(parents=True, exist_ok=True)
    wrapper = bin_dir / 'geomap'
    wrapper.write_text(f'#!/bin/bash\npython3 "{install_dir}/geomap.py" "$@"\n')
    wrapper.chmod(0o755)
    print_success("Created CLI wrapper: ~/.local/bin/geomap")
    
    # Desktop shortcut
    desktop_shortcut = home / 'Desktop' / 'GeoMapper Pro.desktop'
    if (home / 'Desktop').exists():
        shutil.copy2(desktop_file, desktop_shortcut)
        desktop_shortcut.chmod(0o755)
        print_success("Created Desktop shortcut")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='GeoMapper Pro Installer')
    parser.add_argument('--install-dir', type=Path, help='Custom installation directory')
    parser.add_argument('--no-shortcuts', action='store_true', help='Skip shortcut creation')
    args = parser.parse_args()
    
    print_banner()
    
    platform = get_platform()
    print(f"Detected platform: {Colors.CYAN}{platform}{Colors.NC}")
    print()
    
    # Determine directories
    source_dir = Path(__file__).parent.resolve()
    install_dir = args.install_dir or get_default_install_dir(platform)
    
    total_steps = 5 if args.no_shortcuts else 6
    
    # Step 1: Check Python
    print_step(1, total_steps, "Checking Python...")
    if not check_python():
        sys.exit(1)
    
    # Step 2: Create install directory
    print_step(2, total_steps, "Creating installation directory...")
    install_dir.mkdir(parents=True, exist_ok=True)
    print_success(f"Directory: {install_dir}")
    
    # Step 3: Copy files
    print_step(3, total_steps, "Copying files...")
    copy_files(source_dir, install_dir)
    
    # Step 4: Install dependencies
    print_step(4, total_steps, "Installing dependencies...")
    install_dependencies(install_dir)
    
    # Step 5: Create platform-specific launchers
    if not args.no_shortcuts:
        print_step(5, total_steps, "Creating shortcuts...")
        if platform == 'windows':
            create_windows_shortcuts(install_dir)
        elif platform == 'macos':
            create_macos_app(install_dir)
        else:
            create_linux_desktop(install_dir)
    
    # Done
    print(f"""
{Colors.CYAN}==============================================={Colors.NC}
{Colors.GREEN}   Installation Complete!{Colors.NC}
{Colors.CYAN}==============================================={Colors.NC}

{Colors.YELLOW}Installation directory:{Colors.NC}
  {install_dir}

{Colors.YELLOW}Usage:{Colors.NC}
  geomap yourdata.csv
  geomap track.gpx --connect-lines
  geomap data.csv --export-kml output.kml

{Colors.YELLOW}For help:{Colors.NC}
  geomap --help
""")


if __name__ == '__main__':
    main()
