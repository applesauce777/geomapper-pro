#!/bin/bash
# GeoMapper Pro - Linux Installer & .desktop File Generator
# Run: chmod +x install_linux.sh && ./install_linux.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

INSTALL_DIR="$HOME/.local/share/geomapper"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"

echo ""
echo -e "${CYAN}===============================================${NC}"
echo -e "${CYAN}   GeoMapper Pro - Linux Installer${NC}"
echo -e "${CYAN}===============================================${NC}"
echo ""

# Check Python
echo -e "${YELLOW}[1/8] Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "  ${GREEN}Found: $PYTHON_VERSION${NC}"
else
    echo -e "  ${RED}ERROR: Python 3 not found.${NC}"
    echo -e "  ${RED}Install via: sudo apt install python3 python3-pip${NC}"
    exit 1
fi

# Create directories
echo -e "${YELLOW}[2/8] Creating directories...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_DIR"
echo -e "  ${GREEN}Created installation directories${NC}"

# Copy files
echo -e "${YELLOW}[3/8] Copying GeoMapper files...${NC}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

for file in geomap.py flask_app.py requirements.txt; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        cp "$SCRIPT_DIR/$file" "$INSTALL_DIR/"
        echo -e "  ${GREEN}Copied: $file${NC}"
    fi
done

# Copy icon
if [ -f "$SCRIPT_DIR/icons/GeoMapperPro.png" ]; then
    cp "$SCRIPT_DIR/icons/GeoMapperPro.png" "$ICON_DIR/"
    cp "$SCRIPT_DIR/icons/GeoMapperPro.png" "$INSTALL_DIR/"
    echo -e "  ${GREEN}Copied: GeoMapperPro.png${NC}"
fi

# Install dependencies
echo -e "${YELLOW}[4/8] Installing Python dependencies...${NC}"
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    python3 -m pip install -r "$INSTALL_DIR/requirements.txt" --quiet --user
else
    python3 -m pip install pandas folium numpy openpyxl pyarrow flask --quiet --user
fi
echo -e "  ${GREEN}Dependencies installed${NC}"

# Create CLI wrapper
echo -e "${YELLOW}[5/8] Creating command-line wrapper...${NC}"
cat > "$BIN_DIR/geomap" << EOF
#!/bin/bash
python3 "$INSTALL_DIR/geomap.py" "\$@"
EOF
chmod +x "$BIN_DIR/geomap"
echo -e "  ${GREEN}Created: ~/.local/bin/geomap${NC}"

# Create Web UI launcher script
echo -e "${YELLOW}[6/8] Creating Web UI launcher...${NC}"
cat > "$BIN_DIR/geomap-web" << EOF
#!/bin/bash
echo "Starting GeoMapper Pro Web UI..."
echo "Opening browser to http://localhost:5000"
python3 "$INSTALL_DIR/flask_app.py"
EOF
chmod +x "$BIN_DIR/geomap-web"
echo -e "  ${GREEN}Created: ~/.local/bin/geomap-web${NC}"

# Create CLI .desktop file
echo -e "${YELLOW}[7/8] Creating .desktop launchers...${NC}"
cat > "$DESKTOP_DIR/geomapper-pro.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=GeoMapper Pro
GenericName=Geographic Data Visualizer
Comment=Transform geographic data into interactive maps (CLI)
Exec=x-terminal-emulator -e bash -c "cd $INSTALL_DIR && echo 'GeoMapper Pro v2.1.0' && echo '' && echo 'Usage: python3 geomap.py <file> [options]' && echo 'Type: python3 geomap.py --help for options' && echo '' && bash"
Icon=$ICON_DIR/GeoMapperPro.png
Terminal=false
Categories=Science;Geography;DataVisualization;Development;
Keywords=map;gps;gpx;kml;csv;geographic;visualization;
StartupNotify=true
EOF

# Create Web UI .desktop file
cat > "$DESKTOP_DIR/geomapper-web.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=GeoMapper Pro (Web UI)
GenericName=Geographic Data Visualizer
Comment=Launch GeoMapper Pro web interface in browser
Exec=bash -c "python3 $INSTALL_DIR/flask_app.py"
Icon=$ICON_DIR/GeoMapperPro.png
Terminal=true
Categories=Science;Geography;DataVisualization;Development;
Keywords=map;gps;gpx;kml;csv;geographic;visualization;web;
StartupNotify=true
EOF

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo -e "  ${GREEN}Created: geomapper-pro.desktop${NC}"
echo -e "  ${GREEN}Created: geomapper-web.desktop${NC}"

# Create desktop shortcuts
echo -e "${YELLOW}[8/8] Creating desktop shortcuts...${NC}"
if [ -d "$HOME/Desktop" ]; then
    cp "$DESKTOP_DIR/geomapper-pro.desktop" "$HOME/Desktop/GeoMapper Pro.desktop"
    cp "$DESKTOP_DIR/geomapper-web.desktop" "$HOME/Desktop/GeoMapper Pro (Web).desktop"
    chmod +x "$HOME/Desktop/GeoMapper Pro.desktop"
    chmod +x "$HOME/Desktop/GeoMapper Pro (Web).desktop"
    # Mark as trusted (GNOME)
    gio set "$HOME/Desktop/GeoMapper Pro.desktop" metadata::trusted true 2>/dev/null || true
    gio set "$HOME/Desktop/GeoMapper Pro (Web).desktop" metadata::trusted true 2>/dev/null || true
    echo -e "  ${GREEN}Created: Desktop shortcuts${NC}"
else
    echo -e "  ${YELLOW}Skipped: No Desktop folder found${NC}"
fi

# Check if ~/.local/bin is in PATH
echo ""
echo -e "${CYAN}===============================================${NC}"
echo -e "${GREEN}   Installation Complete!${NC}"
echo -e "${CYAN}===============================================${NC}"
echo ""

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo -e "${YELLOW}NOTE: Add ~/.local/bin to your PATH:${NC}"
    echo '  echo '\''export PATH="$HOME/.local/bin:$PATH"'\'' >> ~/.bashrc'
    echo '  source ~/.bashrc'
    echo ""
fi

echo -e "${YELLOW}Command-line usage:${NC}"
echo "  geomap yourdata.csv"
echo "  geomap track.gpx --connect-lines --style terrain"
echo ""
echo -e "${YELLOW}Web interface:${NC}"
echo "  geomap-web"
echo "  (Opens browser to http://localhost:5000)"
echo ""
echo -e "${YELLOW}Or launch from applications menu:${NC}"
echo "  • GeoMapper Pro (CLI)"
echo "  • GeoMapper Pro (Web UI)"
echo ""
