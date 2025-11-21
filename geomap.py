#!/usr/bin/env python3
"""
GeoMapper - Simple Geographic Data Visualization Tool
Transforms tabular data with coordinates into interactive maps
"""

import argparse
import os
import re
import sys
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Tuple, Optional, List
from datetime import datetime

import numpy as np
import pandas as pd
import folium
from folium import plugins

# Version info
__version__ = "2.1.0"
__author__ = "GeoMapper"


class GeoMapper:
    """Main class for geographic data visualization"""
    
    # Map style options with free tile sources
    MAP_STYLES = {
        'default': {'tiles': 'OpenStreetMap', 'attr': None},
        'satellite': {'tiles': 'Esri.WorldImagery', 'attr': None},
        'terrain': {
            'tiles': 'https://tile.opentopomap.org/{z}/{x}/{y}.png',
            'attr': '&copy; <a href="https://opentopomap.org">OpenTopoMap</a> contributors'
        },
        'toner': {
            'tiles': 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
            'attr': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
        },
        'dark': {'tiles': 'CartoDB dark_matter', 'attr': None},
        'light': {'tiles': 'CartoDB positron', 'attr': None}
    }
    
    # Color schemes for categorical data
    COLOR_SCHEMES = [
        '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00',
        '#ffff33', '#a65628', '#f781bf', '#999999'
    ]
    
    def __init__(self, file_path: str):
        """Initialize with data file path"""
        self.file_path = file_path
        self.df = None
        self.lat_col = None
        self.lon_col = None
        
    def load_data(self, table_name: Optional[str] = None) -> pd.DataFrame:
        """Load data from various file formats"""
        file_ext = Path(self.file_path).suffix.lower()
        
        try:
            if file_ext in ['.db', '.sqlite', '.sqlite3']:
                self.df = self._load_sqlite(table_name)
            elif file_ext == '.csv':
                self.df = pd.read_csv(self.file_path)
            elif file_ext in ['.xlsx', '.xls']:
                self.df = pd.read_excel(self.file_path)
            elif file_ext == '.json':
                self.df = pd.read_json(self.file_path)
            elif file_ext == '.geojson':
                self.df = self._load_geojson()
            elif file_ext == '.parquet':
                self.df = pd.read_parquet(self.file_path)
            elif file_ext == '.gpx':
                self.df = self._load_gpx()
            elif file_ext == '.kml':
                self.df = self._load_kml()
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            if self.df is None or len(self.df) == 0:
                raise ValueError("No data loaded from file")
                
            print(f"✓ Loaded {len(self.df)} records from {self.file_path}")
            return self.df
            
        except Exception as e:
            print(f"✗ Error loading data: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _load_sqlite(self, table_name: Optional[str] = None) -> pd.DataFrame:
        """Load data from SQLite database"""
        conn = sqlite3.connect(self.file_path)
        
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table';", 
            conn
        )
        if len(tables) == 0:
            conn.close()
            raise ValueError("No tables found in database")
        
        valid_tables = tables['name'].tolist()
        
        if table_name is None:
            table_name = valid_tables[0]
            print(f"  Using table: {table_name}")
        else:
            if table_name not in valid_tables:
                conn.close()
                raise ValueError(
                    f"Table '{table_name}' not found. Available tables: {', '.join(valid_tables)}"
                )
        
        df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
        conn.close()
        return df
    
    def _load_geojson(self) -> pd.DataFrame:
        """Load GeoJSON and extract coordinates"""
        import json
        
        with open(self.file_path, 'r') as f:
            geojson = json.load(f)
        
        features = geojson.get('features', [])
        records = []
        
        for feature in features:
            props = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            geometry_type = geometry.get('type', '')
            coords = geometry.get('coordinates', [])
            
            lat, lon = None, None
            
            if geometry_type == 'Point':
                if len(coords) >= 2:
                    lon, lat = coords[0], coords[1]
            elif geometry_type == 'LineString':
                if coords and len(coords[0]) >= 2:
                    lon, lat = coords[0][0], coords[0][1]
            elif geometry_type == 'Polygon':
                if coords and coords[0] and len(coords[0][0]) >= 2:
                    lon, lat = coords[0][0][0], coords[0][0][1]
            elif geometry_type in ['MultiPoint', 'MultiLineString', 'MultiPolygon']:
                if coords and len(coords) > 0:
                    first_geom = coords[0]
                    if geometry_type == 'MultiPoint':
                        if len(first_geom) >= 2:
                            lon, lat = first_geom[0], first_geom[1]
                    elif geometry_type == 'MultiLineString':
                        if first_geom and len(first_geom[0]) >= 2:
                            lon, lat = first_geom[0][0], first_geom[0][1]
                    elif geometry_type == 'MultiPolygon':
                        if first_geom and first_geom[0] and len(first_geom[0][0]) >= 2:
                            lon, lat = first_geom[0][0][0], first_geom[0][0][1]
            
            if lat is not None and lon is not None:
                props['latitude'] = lat
                props['longitude'] = lon
                records.append(props)
        
        return pd.DataFrame(records)
    
    def _load_gpx(self) -> pd.DataFrame:
        """Load GPX file and extract coordinates"""
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        
        # Handle GPX namespace
        ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
        if root.tag.startswith('{'):
            ns['gpx'] = root.tag.split('}')[0][1:]
        
        records = []
        
        # Extract waypoints
        for wpt in root.findall('.//gpx:wpt', ns) or root.findall('.//wpt'):
            lat = wpt.get('lat')
            lon = wpt.get('lon')
            if lat and lon:
                record = {
                    'latitude': float(lat),
                    'longitude': float(lon),
                    'type': 'waypoint'
                }
                # Get optional fields
                name = wpt.find('gpx:name', ns) if ns else wpt.find('name')
                if name is None:
                    name = wpt.find('name')
                if name is not None and name.text:
                    record['name'] = name.text
                
                ele = wpt.find('gpx:ele', ns) if ns else wpt.find('ele')
                if ele is None:
                    ele = wpt.find('ele')
                if ele is not None and ele.text:
                    record['elevation'] = float(ele.text)
                
                time = wpt.find('gpx:time', ns) if ns else wpt.find('time')
                if time is None:
                    time = wpt.find('time')
                if time is not None and time.text:
                    record['time'] = time.text
                
                records.append(record)
        
        # Extract track points
        for trkpt in root.findall('.//gpx:trkpt', ns) or root.findall('.//trkpt'):
            lat = trkpt.get('lat')
            lon = trkpt.get('lon')
            if lat and lon:
                record = {
                    'latitude': float(lat),
                    'longitude': float(lon),
                    'type': 'trackpoint'
                }
                
                ele = trkpt.find('gpx:ele', ns) if ns else trkpt.find('ele')
                if ele is None:
                    ele = trkpt.find('ele')
                if ele is not None and ele.text:
                    record['elevation'] = float(ele.text)
                
                time = trkpt.find('gpx:time', ns) if ns else trkpt.find('time')
                if time is None:
                    time = trkpt.find('time')
                if time is not None and time.text:
                    record['time'] = time.text
                
                records.append(record)
        
        # Extract route points
        for rtept in root.findall('.//gpx:rtept', ns) or root.findall('.//rtept'):
            lat = rtept.get('lat')
            lon = rtept.get('lon')
            if lat and lon:
                record = {
                    'latitude': float(lat),
                    'longitude': float(lon),
                    'type': 'routepoint'
                }
                
                name = rtept.find('gpx:name', ns) if ns else rtept.find('name')
                if name is None:
                    name = rtept.find('name')
                if name is not None and name.text:
                    record['name'] = name.text
                
                records.append(record)
        
        if not records:
            raise ValueError("No waypoints, tracks, or routes found in GPX file")
        
        print(f"  Found {len(records)} points in GPX file")
        return pd.DataFrame(records)
    
    def _load_kml(self) -> pd.DataFrame:
        """Load KML file and extract coordinates"""
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        
        # Handle KML namespace
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        if root.tag.startswith('{'):
            ns['kml'] = root.tag.split('}')[0][1:]
        
        records = []
        
        # Find all Placemarks
        placemarks = root.findall('.//kml:Placemark', ns) or root.findall('.//Placemark')
        
        for pm in placemarks:
            name_el = pm.find('kml:name', ns) if ns else pm.find('name')
            if name_el is None:
                name_el = pm.find('name')
            name = name_el.text if name_el is not None else None
            
            desc_el = pm.find('kml:description', ns) if ns else pm.find('description')
            if desc_el is None:
                desc_el = pm.find('description')
            desc = desc_el.text if desc_el is not None else None
            
            # Extract Point coordinates
            point = pm.find('.//kml:Point/kml:coordinates', ns)
            if point is None:
                point = pm.find('.//Point/coordinates')
            
            if point is not None and point.text:
                coords = point.text.strip().split(',')
                if len(coords) >= 2:
                    record = {
                        'longitude': float(coords[0]),
                        'latitude': float(coords[1]),
                        'type': 'point'
                    }
                    if name:
                        record['name'] = name
                    if desc:
                        record['description'] = desc
                    if len(coords) >= 3:
                        record['elevation'] = float(coords[2])
                    records.append(record)
            
            # Extract LineString coordinates (use first point)
            linestring = pm.find('.//kml:LineString/kml:coordinates', ns)
            if linestring is None:
                linestring = pm.find('.//LineString/coordinates')
            
            if linestring is not None and linestring.text:
                points = linestring.text.strip().split()
                for i, pt in enumerate(points):
                    coords = pt.split(',')
                    if len(coords) >= 2:
                        record = {
                            'longitude': float(coords[0]),
                            'latitude': float(coords[1]),
                            'type': 'linestring',
                            'sequence': i
                        }
                        if name:
                            record['name'] = name
                        if len(coords) >= 3:
                            record['elevation'] = float(coords[2])
                        records.append(record)
        
        if not records:
            raise ValueError("No placemarks found in KML file")
        
        print(f"  Found {len(records)} points in KML file")
        return pd.DataFrame(records)
    
    def detect_coordinate_columns(
        self, 
        lat_hint: Optional[str] = None, 
        lon_hint: Optional[str] = None
    ) -> Tuple[str, str]:
        """Auto-detect latitude and longitude columns"""
        
        if lat_hint and lon_hint:
            if lat_hint in self.df.columns and lon_hint in self.df.columns:
                self.lat_col = lat_hint
                self.lon_col = lon_hint
                return self.lat_col, self.lon_col
        
        lat_patterns = [
            r'^lat(itude)?$',
            r'.*lat(itude)?.*',
            r'.*y[-_]?coord.*',
            r'.*\by\b.*'
        ]
        
        lon_patterns = [
            r'^lon(g(itude)?)?$',
            r'.*lon(g(itude)?)?.*',
            r'.*x[-_]?coord.*',
            r'.*\bx\b.*'
        ]
        
        for pattern in lat_patterns:
            matches = [col for col in self.df.columns 
                      if re.match(pattern, col, re.IGNORECASE)]
            if matches:
                self.lat_col = matches[0]
                break
        
        for pattern in lon_patterns:
            matches = [col for col in self.df.columns 
                      if re.match(pattern, col, re.IGNORECASE)]
            if matches:
                self.lon_col = matches[0]
                break
        
        if not self.lat_col or not self.lon_col:
            print("\n✗ Could not auto-detect coordinate columns", file=sys.stderr)
            print(f"Available columns: {', '.join(self.df.columns)}", file=sys.stderr)
            sys.exit(1)
        
        print(f"✓ Using coordinates: {self.lat_col}, {self.lon_col}")
        return self.lat_col, self.lon_col
    
    def validate_data(self) -> pd.DataFrame:
        """Validate and clean coordinate data"""
        original_count = len(self.df)
        
        self.df = self.df.dropna(subset=[self.lat_col, self.lon_col])
        
        self.df = self.df[
            (self.df[self.lat_col].between(-90, 90)) &
            (self.df[self.lon_col].between(-180, 180))
        ]
        
        dropped = original_count - len(self.df)
        if dropped > 0:
            print(f"  Dropped {dropped} invalid records")
        
        if len(self.df) == 0:
            print("✗ No valid coordinates found", file=sys.stderr)
            sys.exit(1)
        
        print(f"✓ Validated {len(self.df)} data points")
        return self.df
    
    def create_map(
        self,
        style: str = 'default',
        heatmap: bool = False,
        cluster: bool = False,
        color_by: Optional[str] = None,
        connect_lines: bool = False,
        popup_cols: Optional[List[str]] = None
    ) -> folium.Map:
        """Create the map with specified visualization options"""
        
        center_lat = self.df[self.lat_col].mean()
        center_lon = self.df[self.lon_col].mean()
        
        lat_range = self.df[self.lat_col].max() - self.df[self.lat_col].min()
        lon_range = self.df[self.lon_col].max() - self.df[self.lon_col].min()
        max_range = max(lat_range, lon_range)
        
        if max_range > 50:
            zoom = 3
        elif max_range > 10:
            zoom = 5
        elif max_range > 1:
            zoom = 8
        else:
            zoom = 11
        
        style_config = self.MAP_STYLES.get(style, self.MAP_STYLES['default'])
        
        if isinstance(style_config, dict):
            tiles = style_config['tiles']
            attr = style_config['attr']
            base_map = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=zoom,
                tiles=tiles,
                attr=attr if attr else None
            )
        else:
            base_map = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=zoom,
                tiles=style_config
            )
        
        if heatmap:
            heat_data = [
                [row[self.lat_col], row[self.lon_col]] 
                for _, row in self.df.iterrows()
            ]
            plugins.HeatMap(heat_data, name='Heatmap').add_to(base_map)
            print("✓ Added heatmap layer")
        
        else:
            if cluster:
                marker_cluster = plugins.MarkerCluster(name='Markers')
                container = marker_cluster
                print("✓ Added marker clustering")
            else:
                container = folium.FeatureGroup(name='Markers')
            
            color_map = {}
            if color_by and color_by in self.df.columns:
                unique_values = self.df[color_by].unique()
                color_map = {
                    val: self.COLOR_SCHEMES[i % len(self.COLOR_SCHEMES)]
                    for i, val in enumerate(unique_values)
                }
                print(f"✓ Color-coding by '{color_by}' ({len(unique_values)} categories)")
            
            if popup_cols is None:
                popup_cols = self.df.columns.tolist()
            
            for idx, row in self.df.iterrows():
                lat = row[self.lat_col]
                lon = row[self.lon_col]
                
                popup_html = "<br/>".join([
                    f"<b>{col}:</b> {row[col]}" 
                    for col in popup_cols 
                    if col in self.df.columns
                ])
                
                if color_map and color_by in self.df.columns:
                    color = color_map.get(row[color_by], 'blue')
                else:
                    color = 'red'
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    popup=folium.Popup(popup_html, max_width=300),
                    color=color,
                    fill=True,
                    fill_opacity=0.7
                ).add_to(container)
            
            container.add_to(base_map)
            print(f"✓ Added {len(self.df)} markers")
        
        if connect_lines and not heatmap:
            coordinates = [
                [row[self.lat_col], row[self.lon_col]]
                for _, row in self.df.iterrows()
            ]
            folium.PolyLine(
                coordinates,
                color='blue',
                weight=2,
                opacity=0.7,
                name='Route'
            ).add_to(base_map)
            print("✓ Connected points with lines")
        
        folium.LayerControl().add_to(base_map)
        
        return base_map
    
    def save_map(self, map_obj: folium.Map, output_path: Optional[str] = None):
        """Save map to HTML file"""
        if output_path is None:
            input_name = Path(self.file_path).stem
            script_dir = Path(__file__).parent
            output_path = script_dir / f"{input_name}_map.html"
        
        map_obj.save(str(output_path))
        print(f"✓ Map saved to: {output_path}")
        print(f"  Open in browser: file://{Path(output_path).absolute()}")
    
    def export_gpx(self, output_path: str, name: str = "GeoMapper Export"):
        """Export data to GPX format"""
        gpx = ET.Element('gpx', {
            'version': '1.1',
            'creator': 'GeoMapper',
            'xmlns': 'http://www.topografix.com/GPX/1/1'
        })
        
        metadata = ET.SubElement(gpx, 'metadata')
        ET.SubElement(metadata, 'name').text = name
        ET.SubElement(metadata, 'time').text = datetime.utcnow().isoformat() + 'Z'
        
        # Add waypoints
        for _, row in self.df.iterrows():
            wpt = ET.SubElement(gpx, 'wpt', {
                'lat': str(row[self.lat_col]),
                'lon': str(row[self.lon_col])
            })
            
            # Add name if available
            if 'name' in row and pd.notna(row['name']):
                ET.SubElement(wpt, 'name').text = str(row['name'])
            
            # Add elevation if available
            if 'elevation' in row and pd.notna(row['elevation']):
                ET.SubElement(wpt, 'ele').text = str(row['elevation'])
            
            # Add time if available
            if 'time' in row and pd.notna(row['time']):
                ET.SubElement(wpt, 'time').text = str(row['time'])
        
        tree = ET.ElementTree(gpx)
        ET.indent(tree, space="  ")
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        print(f"✓ Exported {len(self.df)} points to GPX: {output_path}")
    
    def export_kml(self, output_path: str, name: str = "GeoMapper Export"):
        """Export data to KML format"""
        kml = ET.Element('kml', {'xmlns': 'http://www.opengis.net/kml/2.2'})
        document = ET.SubElement(kml, 'Document')
        ET.SubElement(document, 'name').text = name
        
        # Add placemarks
        for _, row in self.df.iterrows():
            placemark = ET.SubElement(document, 'Placemark')
            
            # Add name if available
            if 'name' in row and pd.notna(row['name']):
                ET.SubElement(placemark, 'name').text = str(row['name'])
            
            # Add description if available
            if 'description' in row and pd.notna(row['description']):
                ET.SubElement(placemark, 'description').text = str(row['description'])
            
            # Add point geometry
            point = ET.SubElement(placemark, 'Point')
            
            # Build coordinates string (lon,lat,elevation)
            coord_str = f"{row[self.lon_col]},{row[self.lat_col]}"
            if 'elevation' in row and pd.notna(row['elevation']):
                coord_str += f",{row['elevation']}"
            
            ET.SubElement(point, 'coordinates').text = coord_str
        
        tree = ET.ElementTree(kml)
        ET.indent(tree, space="  ")
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        print(f"✓ Exported {len(self.df)} points to KML: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='GeoMapper - Transform geographic data into interactive maps',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data.csv
  %(prog)s data.xlsx --heatmap
  %(prog)s track.gpx --connect-lines
  %(prog)s places.kml --cluster
  %(prog)s data.csv --export-gpx output.gpx
  %(prog)s track.gpx --export-kml output.kml
        """
    )
    
    # Input options
    parser.add_argument('data_file', help='Path to data file (CSV, Excel, SQLite, JSON, GeoJSON, Parquet, GPX, KML)')
    parser.add_argument('--table', help='Table name for SQLite database (auto-detected if not specified)')
    parser.add_argument('--lat', help='Column name for latitude (auto-detected if not specified)')
    parser.add_argument('--lon', help='Column name for longitude (auto-detected if not specified)')
    
    # Visualization options
    parser.add_argument('--style', choices=list(GeoMapper.MAP_STYLES.keys()), 
                       default='default', help='Map style/theme')
    parser.add_argument('--heatmap', action='store_true', 
                       help='Generate heatmap instead of markers')
    parser.add_argument('--cluster', action='store_true',
                       help='Enable marker clustering for better performance')
    parser.add_argument('--color-by', metavar='COLUMN',
                       help='Color markers by categorical column values')
    parser.add_argument('--connect-lines', action='store_true',
                       help='Connect points with lines (useful for routes/paths)')
    parser.add_argument('--popup', nargs='+', metavar='COLUMN',
                       help='Columns to show in marker popups (default: all)')
    
    # Output options
    parser.add_argument('--output', '-o', help='Output HTML file path')
    parser.add_argument('--export-gpx', metavar='FILE', help='Export data to GPX file')
    parser.add_argument('--export-kml', metavar='FILE', help='Export data to KML file')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate data without generating map')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    args = parser.parse_args()
    
    # Initialize mapper
    print(f"\n🗺️  GeoMapper v{__version__}\n")
    mapper = GeoMapper(args.data_file)
    
    # Load data
    mapper.load_data(args.table)
    
    # Detect coordinates
    mapper.detect_coordinate_columns(args.lat, args.lon)
    
    # Validate data
    mapper.validate_data()
    
    # Handle exports
    if args.export_gpx:
        mapper.export_gpx(args.export_gpx)
    
    if args.export_kml:
        mapper.export_kml(args.export_kml)
    
    # Exit if validation only or only exporting
    if args.validate_only:
        print("\n✓ Validation complete - data is ready for mapping")
        return
    
    if args.export_gpx or args.export_kml:
        if not args.output and args.validate_only is False:
            # If only exporting, don't generate HTML unless explicitly requested
            print("\n✓ Export complete!")
            return
    
    # Create and save map
    print("\nGenerating map...")
    map_obj = mapper.create_map(
        style=args.style,
        heatmap=args.heatmap,
        cluster=args.cluster,
        color_by=args.color_by,
        connect_lines=args.connect_lines,
        popup_cols=args.popup
    )
    
    mapper.save_map(map_obj, args.output)
    print("\n✓ Done!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
