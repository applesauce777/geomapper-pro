#!/usr/bin/env python3
"""
GeoMapper Pro - Flask Web Interface
A beautiful offline web UI for GeoMapper Pro.

Usage:
    python flask_app.py
    Then open: http://localhost:5000
"""

__version__ = "2.1.0"
import os
import sys
import json
import uuid
import tempfile
import webbrowser
import threading
from pathlib import Path

from flask import (Flask, render_template_string, request, 
                   jsonify, send_file, redirect, url_for)

# Import GeoMapper from same directory
sys.path.insert(0, str(Path(__file__).parent))
from geomap import GeoMapper

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp(prefix='geomapper_')
app.secret_key = 'geomapper-pro-local'

# Store session data
sessions = {}

# ============================================================================
# HTML TEMPLATE
# ============================================================================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GeoMapper Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        :root {
            --grad-1: #1a0a3e;
            --grad-2: #0d2847;
            --grad-3: #071428;
            --accent: #9b5cff;
            --accent-lt: #c9b0ff;
        }
        body {
            background: linear-gradient(135deg, var(--grad-1), var(--grad-2), var(--grad-3));
            min-height: 100vh;
        }
        .glass {
            background: rgba(255,255,255,0.04);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid rgba(155,92,255,0.25);
            backdrop-filter: blur(10px);
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #fff, var(--accent-lt));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .pill {
            background: rgba(155,92,255,0.2);
            color: var(--accent-lt);
            padding: 0.3rem 0.8rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .btn-accent {
            background: linear-gradient(90deg, var(--accent), #4ec6ff);
            border: none;
            color: #fff;
            font-weight: 600;
            padding: 0.6rem 1.4rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(155,92,255,0.3);
        }
        .btn-accent:hover { transform: translateY(-2px); color: #fff; }
        .btn-accent:disabled { opacity: 0.5; transform: none; }
        .upload-zone {
            border: 2px dashed rgba(155,92,255,0.4);
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            cursor: pointer;
            transition: 0.2s;
        }
        .upload-zone:hover, .upload-zone.dragover {
            border-color: var(--accent);
            background: rgba(155,92,255,0.1);
        }
        .upload-zone i { font-size: 2.5rem; color: var(--accent); }
        .form-control, .form-select {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            color: #fff;
        }
        .form-control:focus, .form-select:focus {
            background: rgba(255,255,255,0.08);
            border-color: var(--accent);
            box-shadow: 0 0 0 0.2rem rgba(155,92,255,0.2);
            color: #fff;
        }
        .form-check-input:checked { background-color: var(--accent); border-color: var(--accent); }
        .map-frame {
            border-radius: 12px;
            overflow: hidden;
            background: #12121a;
            min-height: 480px;
        }
        .map-frame iframe { width: 100%; height: 480px; border: none; }
        .settings-section {
            background: rgba(255,255,255,0.02);
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }
        .settings-section h6 { color: var(--accent-lt); font-size: 0.85rem; margin-bottom: 0.6rem; }
        .file-badge {
            background: rgba(76,175,80,0.15);
            border: 1px solid rgba(76,175,80,0.3);
            border-radius: 8px;
            padding: 0.6rem 0.9rem;
            margin-top: 0.75rem;
        }
        .export-btn {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            color: #fff;
            padding: 0.4rem 0.9rem;
            border-radius: 8px;
            font-size: 0.85rem;
        }
        .export-btn:hover { background: rgba(255,255,255,0.12); color: #fff; }
        .toast-container { position: fixed; top: 1rem; right: 1rem; z-index: 9999; }
        .status-bar {
            background: rgba(0,0,0,0.25);
            border-radius: 8px;
            padding: 0.6rem 1rem;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
<div class="container py-4">
    <!-- Header -->
    <div class="glass mb-4 d-flex justify-content-between align-items-center flex-wrap gap-2">
        <div>
            <h1 class="hero-title mb-0"><i class="bi bi-globe-americas me-2"></i>GeoMapper Pro</h1>
            <small class="text-light opacity-75">Transform geographic data into interactive maps</small>
        </div>
        <div class="text-end">
            <span class="pill">v2.1.0</span><br>
            <small class="text-muted">localhost:5000</small>
        </div>
    </div>

    <div class="row g-4">
        <!-- Sidebar -->
        <div class="col-lg-4">
            <!-- Upload -->
            <div class="glass mb-3">
                <h5 class="mb-3"><i class="bi bi-upload me-2"></i>Upload Data</h5>
                <div class="upload-zone" id="uploadZone" onclick="document.getElementById('fileInput').click()">
                    <i class="bi bi-cloud-arrow-up d-block mb-2"></i>
                    <span>Drop file or click to browse</span><br>
                    <small class="text-muted">CSV, Excel, JSON, GeoJSON, GPX, Parquet</small>
                </div>
                <input type="file" id="fileInput" hidden accept=".csv,.xlsx,.xls,.json,.geojson,.gpx,.parquet">
                <div class="file-badge d-none" id="fileBadge">
                    <i class="bi bi-file-earmark-check text-success me-2"></i>
                    <span id="fileName">-</span>
                    <small class="text-muted float-end" id="fileStats">-</small>
                </div>
            </div>

            <!-- Settings -->
            <div class="glass">
                <h5 class="mb-3"><i class="bi bi-sliders me-2"></i>Settings</h5>
                
                <div class="settings-section">
                    <h6><i class="bi bi-palette me-1"></i> Map Style</h6>
                    <select class="form-select form-select-sm" id="mapStyle">
                        <option value="default">Default (OpenStreetMap)</option>
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                        <option value="satellite">Satellite</option>
                        <option value="terrain">Terrain</option>
                        <option value="toner">Toner</option>
                    </select>
                </div>

                <div class="settings-section">
                    <h6><i class="bi bi-layers me-1"></i> Visualization</h6>
                    <div class="form-check mb-1">
                        <input class="form-check-input" type="checkbox" id="heatmap">
                        <label class="form-check-label small" for="heatmap">Heatmap</label>
                    </div>
                    <div class="form-check mb-1">
                        <input class="form-check-input" type="checkbox" id="cluster">
                        <label class="form-check-label small" for="cluster">Cluster markers</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="connectLines">
                        <label class="form-check-label small" for="connectLines">Connect with lines</label>
                    </div>
                </div>

                <div class="settings-section">
                    <h6><i class="bi bi-gear me-1"></i> Advanced</h6>
                    <div class="mb-2">
                        <label class="form-label small mb-1">Color by column</label>
                        <input type="text" class="form-control form-control-sm" id="colorBy" placeholder="e.g. category">
                    </div>
                    <div class="row g-2">
                        <div class="col-6">
                            <label class="form-label small mb-1">Lat column</label>
                            <input type="text" class="form-control form-control-sm" id="latCol" placeholder="auto">
                        </div>
                        <div class="col-6">
                            <label class="form-label small mb-1">Lon column</label>
                            <input type="text" class="form-control form-control-sm" id="lonCol" placeholder="auto">
                        </div>
                    </div>
                </div>

                <button class="btn btn-accent w-100 mt-2" id="generateBtn" disabled>
                    <i class="bi bi-magic me-2"></i>Generate Map
                </button>
            </div>
        </div>

        <!-- Main -->
        <div class="col-lg-8">
            <div class="status-bar mb-3 d-flex justify-content-between align-items-center">
                <span id="status"><i class="bi bi-info-circle me-2"></i>Upload a file to begin</span>
                <span id="spinner" class="d-none"><span class="spinner-border spinner-border-sm me-2"></span>Processing...</span>
            </div>

            <div class="glass">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="mb-0"><i class="bi bi-map me-2"></i>Map Preview</h5>
                    <div id="exportBtns" class="d-none">
                        <button class="export-btn me-1" onclick="download('html')"><i class="bi bi-filetype-html me-1"></i>HTML</button>
                        <button class="export-btn me-1" onclick="download('gpx')"><i class="bi bi-geo-alt me-1"></i>GPX</button>
                        <button class="export-btn" onclick="download('kml')"><i class="bi bi-pin-map me-1"></i>KML</button>
                    </div>
                </div>
                <div class="map-frame" id="mapFrame">
                    <div class="d-flex align-items-center justify-content-center h-100 text-muted" style="min-height:480px">
                        <div class="text-center">
                            <i class="bi bi-map" style="font-size:4rem;opacity:0.2"></i>
                            <p class="mt-2 mb-0">Your map will appear here</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="text-center mt-4 text-muted small">GeoMapper Pro © 2025</div>
</div>

<div class="toast-container" id="toasts"></div>

<script>
let mapId = null;
const $ = id => document.getElementById(id);

// Drag & drop
['dragenter','dragover','dragleave','drop'].forEach(e => 
    $('uploadZone').addEventListener(e, ev => { ev.preventDefault(); ev.stopPropagation(); }));
['dragenter','dragover'].forEach(e => 
    $('uploadZone').addEventListener(e, () => $('uploadZone').classList.add('dragover')));
['dragleave','drop'].forEach(e => 
    $('uploadZone').addEventListener(e, () => $('uploadZone').classList.remove('dragover')));
$('uploadZone').addEventListener('drop', e => { if(e.dataTransfer.files.length) upload(e.dataTransfer.files[0]); });
$('fileInput').addEventListener('change', e => { if(e.target.files.length) upload(e.target.files[0]); });

async function upload(file) {
    setStatus('Uploading...', true);
    const form = new FormData();
    form.append('file', file);
    try {
        const r = await fetch('/upload', {method:'POST', body:form});
        const d = await r.json();
        if(d.error) { toast(d.error,'danger'); setStatus('Upload failed'); return; }
        $('fileName').textContent = file.name;
        $('fileStats').textContent = `${d.rows} rows · ${d.lat_col}, ${d.lon_col}`;
        $('fileBadge').classList.remove('d-none');
        $('generateBtn').disabled = false;
        setStatus(`Ready: ${d.rows} points`);
        toast('File uploaded','success');
    } catch(e) { toast('Upload error','danger'); setStatus('Error'); }
}

$('generateBtn').addEventListener('click', async () => {
    setStatus('Generating...', true);
    $('generateBtn').disabled = true;
    const settings = {
        style: $('mapStyle').value,
        heatmap: $('heatmap').checked,
        cluster: $('cluster').checked,
        connect_lines: $('connectLines').checked,
        color_by: $('colorBy').value || null,
        lat_col: $('latCol').value || null,
        lon_col: $('lonCol').value || null
    };
    try {
        const r = await fetch('/generate', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify(settings)
        });
        const d = await r.json();
        if(d.error) { toast(d.error,'danger'); setStatus('Failed'); $('generateBtn').disabled=false; return; }
        mapId = d.map_id;
        $('mapFrame').innerHTML = `<iframe src="/map/${mapId}"></iframe>`;
        $('exportBtns').classList.remove('d-none');
        setStatus(`Map ready: ${d.points} points`);
        toast('Map generated!','success');
    } catch(e) { toast('Generation error','danger'); setStatus('Error'); }
    $('generateBtn').disabled = false;
});

function download(fmt) { if(mapId) window.location.href = `/download/${mapId}/${fmt}`; }

function setStatus(msg, loading=false) {
    $('status').innerHTML = `<i class="bi bi-${loading?'hourglass-split':'check-circle'} me-2"></i>${msg}`;
    $('spinner').classList.toggle('d-none', !loading);
}

function toast(msg, type='info') {
    const t = document.createElement('div');
    t.className = `toast show align-items-center text-white bg-${type} border-0`;
    t.innerHTML = `<div class="d-flex"><div class="toast-body">${msg}</div><button class="btn-close btn-close-white me-2 m-auto" onclick="this.parentElement.parentElement.remove()"></button></div>`;
    $('toasts').appendChild(t);
    setTimeout(() => t.remove(), 3500);
}
</script>
</body>
</html>
'''

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400
    
    # Save uploaded file
    filepath = Path(app.config['UPLOAD_FOLDER']) / file.filename
    file.save(filepath)
    
    try:
        mapper = GeoMapper(str(filepath))
        mapper.load_data()
        mapper.detect_coordinate_columns()
        mapper.validate_data()
        
        # Store for later
        sid = str(uuid.uuid4())[:8]
        sessions[sid] = {'mapper': mapper, 'filepath': str(filepath)}
        app.config['CURRENT_SESSION'] = sid
        
        return jsonify({
            'success': True,
            'session': sid,
            'rows': len(mapper.df),
            'columns': mapper.df.columns.tolist(),
            'lat_col': mapper.lat_col,
            'lon_col': mapper.lon_col
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/generate', methods=['POST'])
def generate():
    sid = app.config.get('CURRENT_SESSION')
    if not sid or sid not in sessions:
        return jsonify({'error': 'No file uploaded'}), 400
    
    data = sessions[sid]
    mapper = data['mapper']
    settings = request.json or {}
    
    try:
        # Override columns if specified
        lat = settings.get('lat_col')
        lon = settings.get('lon_col')
        if lat and lon:
            mapper.detect_coordinate_columns(lat, lon)
        
        # Generate map
        map_obj = mapper.create_map(
            style=settings.get('style', 'default'),
            heatmap=settings.get('heatmap', False),
            cluster=settings.get('cluster', False),
            color_by=settings.get('color_by'),
            connect_lines=settings.get('connect_lines', False)
        )
        
        # Save to temp
        map_id = str(uuid.uuid4())[:8]
        map_path = Path(app.config['UPLOAD_FOLDER']) / f'map_{map_id}.html'
        map_obj.save(str(map_path))
        
        sessions[sid]['map_id'] = map_id
        sessions[sid]['map_path'] = str(map_path)
        
        return jsonify({
            'success': True,
            'map_id': map_id,
            'points': len(mapper.df)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/map/<map_id>')
def view_map(map_id):
    for s in sessions.values():
        if s.get('map_id') == map_id:
            return send_file(s['map_path'])
    return 'Map not found', 404


@app.route('/download/<map_id>/<fmt>')
def download_map(map_id, fmt):
    session = None
    for s in sessions.values():
        if s.get('map_id') == map_id:
            session = s
            break
    
    if not session:
        return 'Not found', 404
    
    mapper = session['mapper']
    
    if fmt == 'html':
        return send_file(session['map_path'], as_attachment=True,
                        download_name='geomapper_map.html')
    
    export_path = Path(app.config['UPLOAD_FOLDER']) / f'export_{map_id}.{fmt}'
    
    if fmt == 'gpx':
        mapper.export_gpx(str(export_path))
        return send_file(str(export_path), as_attachment=True,
                        download_name='geomapper_export.gpx')
    
    if fmt == 'kml':
        mapper.export_kml(str(export_path))
        return send_file(str(export_path), as_attachment=True,
                        download_name='geomapper_export.kml')
    
    return 'Invalid format', 400


# ============================================================================
# MAIN
# ============================================================================

def open_browser():
    import time
    time.sleep(1.2)
    webbrowser.open('http://localhost:5000')


if __name__ == '__main__':
    print('''
╔══════════════════════════════════════════════════╗
║      🗺️  GeoMapper Pro - Web Interface           ║
╠══════════════════════════════════════════════════╣
║  Server: http://localhost:5000                   ║
║  Press Ctrl+C to stop                            ║
╚══════════════════════════════════════════════════╝
''')
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
