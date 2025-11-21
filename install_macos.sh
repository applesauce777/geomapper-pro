#!/bin/bash
# GeoMapper Pro - macOS Installer & .app Bundle Generator
# Run: chmod +x install_macos.sh && ./install_macos.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

INSTALL_DIR="$HOME/.local/share/geomapper"
APP_NAME="GeoMapper Pro"
APP_BUNDLE="$HOME/Applications/${APP_NAME}.app"
WEB_APP_BUNDLE="$HOME/Applications/${APP_NAME} Web.app"

echo ""
echo -e "${CYAN}===============================================${NC}"
echo -e "${CYAN}   GeoMapper Pro - macOS Installer${NC}"
echo -e "${CYAN}===============================================${NC}"
echo ""

# Check Python
echo -e "${YELLOW}[1/7] Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "  ${GREEN}Found: $PYTHON_VERSION${NC}"
else
    echo -e "  ${RED}ERROR: Python 3 not found. Install via: brew install python${NC}"
    exit 1
fi

# Create install directory
echo -e "${YELLOW}[2/7] Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"
echo -e "  ${GREEN}Location: $INSTALL_DIR${NC}"

# Copy files
echo -e "${YELLOW}[3/7] Copying GeoMapper files...${NC}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

for file in geomap.py geomap_pro.py flask_app.py requirements.txt; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        cp "$SCRIPT_DIR/$file" "$INSTALL_DIR/"
        echo -e "  ${GREEN}Copied: $file${NC}"
    fi
done

# Copy icon if exists
if [ -f "$SCRIPT_DIR/icons/GeoMapperPro.icns" ]; then
    cp "$SCRIPT_DIR/icons/GeoMapperPro.icns" "$INSTALL_DIR/"
    echo -e "  ${GREEN}Copied: GeoMapperPro.icns${NC}"
fi

# Install dependencies
echo -e "${YELLOW}[4/7] Installing Python dependencies...${NC}"
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    python3 -m pip install -r "$INSTALL_DIR/requirements.txt" --quiet
else
    python3 -m pip install pandas folium numpy openpyxl pyarrow flask --quiet
fi
echo -e "  ${GREEN}Dependencies installed${NC}"

# Create CLI wrappers
echo -e "${YELLOW}[5/7] Creating command-line wrappers...${NC}"
mkdir -p "$HOME/.local/bin"

cat > "$HOME/.local/bin/geomap" << 'EOF'
#!/bin/bash
python3 "$HOME/.local/share/geomapper/geomap.py" "$@"
EOF
chmod +x "$HOME/.local/bin/geomap"

cat > "$HOME/.local/bin/geomap-web" << 'EOF'
#!/bin/bash
echo "Starting GeoMapper Pro Web UI..."
echo "Opening browser to http://localhost:5000"
python3 "$HOME/.local/share/geomapper/flask_app.py"
EOF
chmod +x "$HOME/.local/bin/geomap-web"

echo -e "  ${GREEN}Created: ~/.local/bin/geomap${NC}"
echo -e "  ${GREEN}Created: ~/.local/bin/geomap-web${NC}"

# Create CLI .app bundle
echo -e "${YELLOW}[6/7] Creating macOS .app bundles...${NC}"
mkdir -p "$HOME/Applications"

# --- CLI App Bundle ---
rm -rf "$APP_BUNDLE"
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

cat > "$APP_BUNDLE/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key><string>GeoMapperPro</string>
    <key>CFBundleIdentifier</key><string>com.geomapper.pro</string>
    <key>CFBundleName</key><string>GeoMapper Pro</string>
    <key>CFBundleDisplayName</key><string>GeoMapper Pro</string>
    <key>CFBundleVersion</key><string>2.1.0</string>
    <key>CFBundleShortVersionString</key><string>2.1.0</string>
    <key>CFBundleIconFile</key><string>GeoMapperPro</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>LSMinimumSystemVersion</key><string>10.13</string>
    <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
EOF

cat > "$APP_BUNDLE/Contents/MacOS/GeoMapperPro" << EOF
#!/bin/bash
osascript -e 'tell app "Terminal"
    do script "cd $INSTALL_DIR && echo \"GeoMapper Pro v2.1.0\" && echo \"\" && echo \"Usage: python3 geomap.py <file> [options]\" && echo \"\" && echo \"Type: python3 geomap.py --help for all options\" && echo \"\""
    activate
end tell'
EOF
chmod +x "$APP_BUNDLE/Contents/MacOS/GeoMapperPro"

if [ -f "$INSTALL_DIR/GeoMapperPro.icns" ]; then
    cp "$INSTALL_DIR/GeoMapperPro.icns" "$APP_BUNDLE/Contents/Resources/"
fi

echo -e "  ${GREEN}Created: ~/Applications/GeoMapper Pro.app${NC}"

# --- Web UI App Bundle ---
rm -rf "$WEB_APP_BUNDLE"
mkdir -p "$WEB_APP_BUNDLE/Contents/MacOS"
mkdir -p "$WEB_APP_BUNDLE/Contents/Resources"

cat > "$WEB_APP_BUNDLE/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key><string>GeoMapperWeb</string>
    <key>CFBundleIdentifier</key><string>com.geomapper.pro.web</string>
    <key>CFBundleName</key><string>GeoMapper Pro Web</string>
    <key>CFBundleDisplayName</key><string>GeoMapper Pro Web</string>
    <key>CFBundleVersion</key><string>2.1.0</string>
    <key>CFBundleShortVersionString</key><string>2.1.0</string>
    <key>CFBundleIconFile</key><string>GeoMapperPro</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>LSMinimumSystemVersion</key><string>10.13</string>
    <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
EOF

cat > "$WEB_APP_BUNDLE/Contents/MacOS/GeoMapperWeb" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
osascript -e 'tell app "Terminal"
    do script "cd $INSTALL_DIR && echo \"Starting GeoMapper Pro Web UI...\" && echo \"Browser will open to http://localhost:5000\" && echo \"\" && python3 flask_app.py"
    activate
end tell'
EOF
chmod +x "$WEB_APP_BUNDLE/Contents/MacOS/GeoMapperWeb"

if [ -f "$INSTALL_DIR/GeoMapperPro.icns" ]; then
    cp "$INSTALL_DIR/GeoMapperPro.icns" "$WEB_APP_BUNDLE/Contents/Resources/"
fi

echo -e "  ${GREEN}Created: ~/Applications/GeoMapper Pro Web.app${NC}"

# Summary
echo ""
echo -e "${CYAN}===============================================${NC}"
echo -e "${GREEN}   Installation Complete!${NC}"
echo -e "${CYAN}===============================================${NC}"
echo ""
echo -e "${YELLOW}To use from anywhere, add to your PATH:${NC}"
echo '  echo '\''export PATH="$HOME/.local/bin:$PATH"'\'' >> ~/.zshrc'
echo '  source ~/.zshrc'
echo ""
echo -e "${YELLOW}Command-line usage:${NC}"
echo "  geomap yourdata.csv"
echo "  geomap track.gpx --connect-lines --style terrain"
echo ""
echo -e "${YELLOW}Web interface:${NC}"
echo "  geomap-web"
echo "  (Opens browser to http://localhost:5000)"
echo ""
echo -e "${YELLOW}Or launch the apps:${NC}"
echo "  open ~/Applications/GeoMapper\\ Pro.app"
echo "  open ~/Applications/GeoMapper\\ Pro\\ Web.app"
echo ""
