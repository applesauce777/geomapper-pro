import subprocess
import sys
from pathlib import Path
import pytest


@pytest.fixture
def repo_root():
    """Get the repository root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def script(repo_root):
    """Get the geomap.py script path."""
    script_path = repo_root / 'geomap.py'
    assert script_path.exists(), "geomap.py not found"
    return script_path


@pytest.fixture
def test_data_dir(repo_root):
    """Get the test data directory."""
    data_dir = repo_root / 'tests' / 'data'
    assert data_dir.exists(), "test data directory not found"
    return data_dir


@pytest.fixture
def output_dir(repo_root):
    """Get the output directory for generated maps."""
    return repo_root / 'tests'


# ==================== Validation Tests ====================

def test_validate_csv(script, test_data_dir):
    """Test validation on CSV file."""
    csv_file = test_data_dir / 'test_locations.csv'
    assert csv_file.exists(), "CSV test file not found"
    
    proc = subprocess.run(
        [sys.executable, str(script), str(csv_file), '--validate-only'],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"CSV validation failed with code {proc.returncode}"


def test_validate_json(script, test_data_dir):
    """Test validation on JSON file."""
    json_file = test_data_dir / 'test_locations.json'
    assert json_file.exists(), "JSON test file not found"
    
    proc = subprocess.run(
        [sys.executable, str(script), str(json_file), '--validate-only'],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"JSON validation failed with code {proc.returncode}"


def test_validate_geojson(script, test_data_dir):
    """Test validation on GeoJSON file."""
    geojson_file = test_data_dir / 'test_locations.geojson'
    assert geojson_file.exists(), "GeoJSON test file not found"
    
    proc = subprocess.run(
        [sys.executable, str(script), str(geojson_file), '--validate-only'],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"GeoJSON validation failed with code {proc.returncode}"


def test_validate_parquet(script, test_data_dir):
    """Test validation on Parquet file."""
    parquet_file = test_data_dir / 'test_locations.parquet'
    assert parquet_file.exists(), "Parquet test file not found"
    
    proc = subprocess.run(
        [sys.executable, str(script), str(parquet_file), '--validate-only'],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"Parquet validation failed with code {proc.returncode}"


def test_validate_gpx(script, test_data_dir):
    """Test validation on GPX file."""
    gpx_file = test_data_dir / 'test_locations.gpx'
    assert gpx_file.exists(), "GPX test file not found"
    
    proc = subprocess.run(
        [sys.executable, str(script), str(gpx_file), '--validate-only'],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"GPX validation failed with code {proc.returncode}"


def test_validate_kml(script, test_data_dir):
    """Test validation on KML file."""
    kml_file = test_data_dir / 'test_locations.kml'
    assert kml_file.exists(), "KML test file not found"
    
    proc = subprocess.run(
        [sys.executable, str(script), str(kml_file), '--validate-only'],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"KML validation failed with code {proc.returncode}"


# ==================== Map Generation Tests ====================

def test_generate_basic_map(script, test_data_dir, output_dir):
    """Test basic map generation."""
    csv_file = test_data_dir / 'test_locations.csv'
    output_file = output_dir / 'test_map.html'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(csv_file), '--output', str(output_file)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"Map generation failed with code {proc.returncode}"
    assert output_file.exists(), "Output HTML file was not created"
    assert output_file.stat().st_size > 0, "Output HTML file is empty"


def test_generate_heatmap(script, test_data_dir, output_dir):
    """Test heatmap generation."""
    csv_file = test_data_dir / 'test_locations.csv'
    output_file = output_dir / 'heatmap.html'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(csv_file), '--heatmap', '--output', str(output_file)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"Heatmap generation failed with code {proc.returncode}"
    assert output_file.exists(), "Heatmap HTML file was not created"


def test_generate_clustered_map(script, test_data_dir, output_dir):
    """Test clustered marker map generation."""
    csv_file = test_data_dir / 'test_locations.csv'
    output_file = output_dir / 'clustered.html'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(csv_file), '--cluster', '--output', str(output_file)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"Clustered map generation failed with code {proc.returncode}"
    assert output_file.exists(), "Clustered map HTML file was not created"


def test_generate_colored_map(script, test_data_dir, output_dir):
    """Test color-coded map by category."""
    csv_file = test_data_dir / 'test_locations.csv'
    output_file = output_dir / 'colored.html'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(csv_file), '--color-by', 'type', '--output', str(output_file)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"Colored map generation failed with code {proc.returncode}"
    assert output_file.exists(), "Colored map HTML file was not created"


def test_generate_route_map(script, test_data_dir, output_dir):
    """Test route/line connection map generation."""
    csv_file = test_data_dir / 'test_locations.csv'
    output_file = output_dir / 'route.html'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(csv_file), '--connect-lines', '--output', str(output_file)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"Route map generation failed with code {proc.returncode}"
    assert output_file.exists(), "Route map HTML file was not created"


def test_generate_gpx_map(script, test_data_dir, output_dir):
    """Test map generation from GPX file."""
    gpx_file = test_data_dir / 'test_locations.gpx'
    output_file = output_dir / 'gpx_map.html'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(gpx_file), '--connect-lines', '--output', str(output_file)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"GPX map generation failed with code {proc.returncode}"
    assert output_file.exists(), "GPX map HTML file was not created"


def test_generate_kml_map(script, test_data_dir, output_dir):
    """Test map generation from KML file."""
    kml_file = test_data_dir / 'test_locations.kml'
    output_file = output_dir / 'kml_map.html'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(kml_file), '--cluster', '--output', str(output_file)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"KML map generation failed with code {proc.returncode}"
    assert output_file.exists(), "KML map HTML file was not created"


# ==================== Style Tests ====================

@pytest.mark.parametrize("style", ['default', 'satellite', 'terrain', 'toner', 'dark', 'light'])
def test_map_styles(script, test_data_dir, output_dir, style):
    """Test all available map styles."""
    csv_file = test_data_dir / 'test_locations.csv'
    output_file = output_dir / f'map_{style}.html'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(csv_file), '--style', style, '--output', str(output_file)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"Map generation with {style} style failed"
    assert output_file.exists(), f"Map with {style} style was not created"


# ==================== Custom Column Tests ====================

def test_custom_lat_lon_columns(script, test_data_dir, output_dir):
    """Test explicit latitude/longitude column specification."""
    csv_file = test_data_dir / 'test_locations.csv'
    output_file = output_dir / 'custom_cols.html'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(csv_file), 
         '--lat', 'latitude', '--lon', 'longitude', '--output', str(output_file)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, "Custom column map generation failed"
    assert output_file.exists(), "Custom column map was not created"


def test_custom_popup_columns(script, test_data_dir, output_dir):
    """Test custom popup column selection."""
    csv_file = test_data_dir / 'test_locations.csv'
    output_file = output_dir / 'custom_popup.html'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(csv_file), 
         '--popup', 'name', 'city', 'rating', '--output', str(output_file)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, "Custom popup map generation failed"
    assert output_file.exists(), "Custom popup map was not created"


# ==================== Combined Feature Tests ====================

def test_combined_features(script, test_data_dir, output_dir):
    """Test multiple features combined."""
    csv_file = test_data_dir / 'test_locations.csv'
    output_file = output_dir / 'combined.html'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(csv_file), 
         '--cluster', '--color-by', 'type', '--style', 'dark', '--output', str(output_file)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, "Combined features map generation failed"
    assert output_file.exists(), "Combined features map was not created"


# ==================== Export Tests ====================

def test_export_gpx(script, test_data_dir, output_dir):
    """Test GPX export from CSV."""
    csv_file = test_data_dir / 'test_locations.csv'
    output_file = output_dir / 'exported.gpx'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(csv_file), '--export-gpx', str(output_file)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, "GPX export failed"
    assert output_file.exists(), "GPX export file was not created"
    assert output_file.stat().st_size > 0, "GPX export file is empty"


def test_export_kml(script, test_data_dir, output_dir):
    """Test KML export from CSV."""
    csv_file = test_data_dir / 'test_locations.csv'
    output_file = output_dir / 'exported.kml'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(csv_file), '--export-kml', str(output_file)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, "KML export failed"
    assert output_file.exists(), "KML export file was not created"
    assert output_file.stat().st_size > 0, "KML export file is empty"


def test_export_gpx_from_kml(script, test_data_dir, output_dir):
    """Test GPX export from KML (format conversion)."""
    kml_file = test_data_dir / 'test_locations.kml'
    output_file = output_dir / 'converted_from_kml.gpx'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(kml_file), '--export-gpx', str(output_file)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, "KML to GPX conversion failed"
    assert output_file.exists(), "Converted GPX file was not created"


def test_export_kml_from_gpx(script, test_data_dir, output_dir):
    """Test KML export from GPX (format conversion)."""
    gpx_file = test_data_dir / 'test_locations.gpx'
    output_file = output_dir / 'converted_from_gpx.kml'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(gpx_file), '--export-kml', str(output_file)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, "GPX to KML conversion failed"
    assert output_file.exists(), "Converted KML file was not created"


def test_export_with_map(script, test_data_dir, output_dir):
    """Test generating map AND exporting at the same time."""
    csv_file = test_data_dir / 'test_locations.csv'
    html_output = output_dir / 'dual_output_map.html'
    gpx_output = output_dir / 'dual_output.gpx'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(csv_file), 
         '--output', str(html_output), '--export-gpx', str(gpx_output)],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, "Dual output generation failed"
    assert html_output.exists(), "HTML output was not created"
    assert gpx_output.exists(), "GPX output was not created"


# ==================== Error Handling Tests ====================

def test_missing_file_error(script, output_dir):
    """Test error handling for missing input file."""
    nonexistent_file = output_dir / 'does_not_exist.csv'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(nonexistent_file)],
        capture_output=True, text=True
    )
    assert proc.returncode != 0, "Should fail with missing file"


def test_invalid_style_error(script, test_data_dir, output_dir):
    """Test error handling for invalid style."""
    csv_file = test_data_dir / 'test_locations.csv'
    output_file = output_dir / 'invalid_style.html'
    
    proc = subprocess.run(
        [sys.executable, str(script), str(csv_file), 
         '--style', 'invalid_style_name', '--output', str(output_file)],
        capture_output=True, text=True
    )
    assert proc.returncode != 0, "Should fail with invalid style"


# ==================== Sample Data Test (Original) ====================

def test_validate_sample(script, repo_root):
    """Run geomap.py in validate-only mode on the sample dataset."""
    sample = repo_root / 'sample' / 'locations.csv'
    if not sample.exists():
        pytest.skip("Sample data not found")
    
    proc = subprocess.run(
        [sys.executable, str(script), str(sample), '--validate-only'],
        capture_output=True, text=True
    )
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"Validator exited with {proc.returncode}"
