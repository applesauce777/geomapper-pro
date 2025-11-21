# 🗺️ GeoMapper Pro

**Transform your geographic data into beautiful interactive maps in seconds.**

GeoMapper Pro is a powerful desktop tool that converts tabular data with coordinates into stunning interactive web maps. Runs completely offline — your data never leaves your machine.

![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-lightgrey.svg)

---

## ✨ Features

- **Web Interface**: Beautiful browser-based UI — no command line required
- **Multiple Formats**: CSV, Excel, SQLite, JSON, GeoJSON, Parquet, GPX, KML
- **Export Options**: Download as HTML, GPX, or KML
- **Visualization Modes**: Markers, heatmaps, clustering, connected routes
- **6 Map Styles**: Default, satellite, dark, light, terrain, toner
- **Color Coding**: Categorize markers by any column
- **Auto-Detection**: Automatically finds lat/lon columns
- **100% Offline**: Runs locally, your data stays private
- **Cross-Platform**: Windows, macOS, and Linux installers included

---

## 🚀 Quick Start

### Windows

```powershell
# Right-click and "Run with PowerShell" or:
powershell -ExecutionPolicy Bypass -File install_windows.ps1
```

Then double-click **"GeoMapper Pro Web"** on your Desktop.

### macOS

```bash
chmod +x install_macos.sh
./install_macos.sh
```

Then open **"GeoMapper Pro Web"** from `~/Applications`.

### Linux

```bash
chmod +x install_linux.sh
./install_linux.sh
```

Then run `geomap-web` or find **"GeoMapper Pro (Web UI)"** in your applications menu.

---

## 🖥️ Two Ways to Use

### 1. Web Interface (Recommended)

Launch the web UI and use GeoMapper in your browser:

- **Windows**: Double-click "GeoMapper Pro Web" on Desktop
- **macOS**: Open "GeoMapper Pro Web.app"
- **Linux**: Run `geomap-web` or use the desktop launcher

Your browser opens to `http://localhost:5000` with a beautiful drag-and-drop interface.

### 2. Command Line

For scripting, automation, or if you prefer the terminal:

```bash
# Basic usage
geomap locations.csv

# With options
geomap track.gpx --connect-lines --style terrain

# Export to GPX
geomap data.csv --export-gpx output.gpx
```

---

## 📊 Examples

### Basic Map
```bash
geomap stores.csv
```

### Heatmap
```bash
geomap crime_data.csv --heatmap
```

### Clustered Markers
```bash
geomap cities.xlsx --cluster
```

### Color by Category
```bash
geomap restaurants.json --color-by cuisine_type
```

### Route/Track Visualization
```bash
geomap delivery_route.csv --connect-lines
geomap hike.gpx --connect-lines --style terrain
```

### Dark Mode
```bash
geomap properties.xlsx --style dark --cluster
```

---

## 📋 Supported Formats

| Format | Extensions | Input | Export |
|--------|------------|:-----:|:------:|
| CSV | `.csv` | ✅ | — |
| Excel | `.xlsx`, `.xls` | ✅ | — |
| SQLite | `.db`, `.sqlite` | ✅ | — |
| JSON | `.json` | ✅ | — |
| GeoJSON | `.geojson` | ✅ | — |
| Parquet | `.parquet` | ✅ | — |
| GPX | `.gpx` | ✅ | ✅ |
| KML | `.kml` | ✅ | ✅ |
| HTML Map | `.html` | — | ✅ |

---

## 🎨 Map Styles

| Style | Description |
|-------|-------------|
| `default` | Classic OpenStreetMap |
| `satellite` | Satellite imagery |
| `terrain` | Topographic view |
| `dark` | Dark mode |
| `light` | Minimal light theme |
| `toner` | High contrast B&W |

---

## 🛠️ Command Line Reference

```
geomap <file> [options]

Options:
  --style STYLE       Map style (default, satellite, terrain, dark, light, toner)
  --heatmap           Generate heatmap instead of markers
  --cluster           Enable marker clustering
  --color-by COLUMN   Color markers by column values
  --connect-lines     Connect points with lines (routes)
  --popup COL [COL]   Columns to show in popups
  --output FILE       Output HTML file path
  --export-gpx FILE   Export to GPX format
  --export-kml FILE   Export to KML format
  --lat COLUMN        Manually specify latitude column
  --lon COLUMN        Manually specify longitude column
  --table TABLE       SQLite table name
  --validate-only     Check data without generating map
  --version           Show version
```

---

## 📁 Data Requirements

Your data needs latitude and longitude columns. GeoMapper auto-detects common names:

**Latitude**: `lat`, `latitude`, `y`, `y_coord`, `lat_col`
**Longitude**: `lon`, `long`, `longitude`, `x`, `x_coord`, `lng`

Example CSV:
```csv
name,latitude,longitude,category
Store A,40.7128,-74.0060,retail
Store B,34.0522,-118.2437,warehouse
```

GPX and KML files have coordinates built-in — no configuration needed.

---

## 🎯 Use Cases

- **Business**: Store locations, customer distribution, sales territories
- **Real Estate**: Property mapping, market analysis
- **Logistics**: Delivery routes, warehouse coverage
- **Fitness**: Visualize GPS tracks from Strava, Garmin, etc.
- **Travel**: Plan trips, share routes
- **Research**: Field study locations, geographic analysis

---

## 🔧 Manual Installation

If you prefer not to use the installers:

```bash
# Install dependencies
pip install -r requirements.txt

# Run CLI
python geomap.py yourdata.csv

# Run Web UI
python flask_app.py
```

---

## 💡 Tips

- **Large datasets**: Use `--cluster` for 1000+ points
- **Quick check**: Use `--validate-only` before generating
- **Custom popups**: `--popup name address phone`
- **The HTML output is self-contained** — share it directly or embed in websites

---

## 🐛 Troubleshooting

**"Could not auto-detect coordinate columns"**
→ Use `--lat your_column --lon your_column`

**"No valid coordinates found"**
→ Check that lat is -90 to 90, lon is -180 to 180

**Web UI won't start**
→ Make sure port 5000 is free, or check if Flask is installed: `pip install flask`

**Map is empty**
→ Verify coordinates are decimal degrees (not degrees-minutes-seconds)

---

## 📄 License

See LICENSE.md for terms.

---

**GeoMapper Pro v2.1.0** — Your data, your maps, your machine.
