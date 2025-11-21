#!/usr/bin/env python3
"""GeoMapper Pro - enhanced with route smoothing, optional threading, and a Tkinter GUI wrapper.
This file wraps the original geomap.GeoMapper (assumed available as /mnt/data/geomap.py)
and adds lightweight, optional features:
 - Ramer-Douglas-Peucker route smoothing (--smooth N)
 - Threaded preparation of marker payloads (--threads N)
 - A small CLI and a --gui entrypoint (launches geomap_gui.py)
"""

import sys
from pathlib import Path
sys.path.insert(0, '/mnt/data')  # ensure local geomap.py is importable
import argparse
import concurrent.futures
from typing import List, Tuple

try:
    from geomap import GeoMapper  # original class from user's uploaded file
except Exception as e:
    raise ImportError(f"Could not import original geomap.py: {e}")


def rdp(points: List[Tuple[float, float]], epsilon: float) -> List[Tuple[float, float]]:
    """Ramer-Douglas-Peucker line simplification.
    points: list of (lat, lon)
    epsilon: tolerance in same units as coords (roughly degrees)
    Returns simplified list of points.
    """
    if not points:
        return []
    if len(points) < 3:
        return points

    def perpendicular_distance(pt, line_start, line_end):
        (x0, y0) = pt
        (x1, y1) = line_start
        (x2, y2) = line_end
        if x1 == x2 and y1 == y2:
            return ((x0 - x1)**2 + (y0 - y1)**2) ** 0.5
        num = abs((y2 - y1)*x0 - (x2 - x1)*y0 + x2*y1 - y2*x1)
        den = ((y2 - y1)**2 + (x2 - x1)**2) ** 0.5
        return num / den

    def rdp_rec(pts):
        if len(pts) < 3:
            return pts
        max_dist = 0.0
        index = 0
        for i in range(1, len(pts)-1):
            d = perpendicular_distance(pts[i], pts[0], pts[-1])
            if d > max_dist:
                index = i
                max_dist = d
        if max_dist > epsilon:
            left = rdp_rec(pts[:index+1])
            right = rdp_rec(pts[index:])
            return left[:-1] + right
        else:
            return [pts[0], pts[-1]]

    return rdp_rec(points)


class GeoMapperPro:
    """Light wrapper that adds smoothing + threaded marker preparation."""

    def __init__(self, data_file: str, threads: int = 1):
        self.mapper = GeoMapper(data_file)
        self.threads = max(1, int(threads))

    def load_and_prepare(self, table_name=None):
        self.mapper.load_data(table_name)
        self.mapper.detect_coordinate_columns()
        self.mapper.validate_data()

    def smooth_route(self, epsilon: float = 0.01):
        """Simplify the coordinate list used for connecting lines using RDP."""
        lat_col, lon_col = self.mapper.lat_col, self.mapper.lon_col
        points = [(row[lat_col], row[lon_col]) for _, row in self.mapper.df.iterrows()]
        simplified = rdp(points, epsilon)
        import pandas as pd
        df_smooth = pd.DataFrame(simplified, columns=[lat_col, lon_col])
        self.mapper.df = df_smooth
        print(f"✓ Route smoothed: {len(points)} → {len(simplified)} points (epsilon={epsilon})")

    def _prepare_marker_payload(self, row, popup_cols):
        lat = row[self.mapper.lat_col]
        lon = row[self.mapper.lon_col]
        popup_html = "<br/>".join([
            f"<b>{col}:</b> {row[col]}"
            for col in (popup_cols or self.mapper.df.columns.tolist())
            if col in self.mapper.df.columns
        ])
        color = 'red'
        return (lat, lon, popup_html, color)

    def create_map(self, style='default', heatmap=False, cluster=False, color_by=None,
                   connect_lines=False, popup_cols=None, smooth=None, threads=1):

        if smooth is not None and connect_lines:
            try:
                eps = float(smooth)
            except Exception:
                eps = 0.01
            self.smooth_route(eps)

        df = self.mapper.df
        popup_cols_list = popup_cols or df.columns.tolist()

        marker_payloads = []
        if not heatmap:
            rows = list(df.itertuples(index=False, name=None))
            cols = df.columns.tolist()

            def row_to_payload(tup):
                row = dict(zip(cols, tup))
                return self._prepare_marker_payload(row, popup_cols_list)

            if threads and threads > 1:
                max_workers = min(threads, 8)
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
                    marker_payloads = list(ex.map(row_to_payload, rows))
                print(f"✓ Prepared {len(marker_payloads)} marker payloads using {max_workers} threads")
            else:
                marker_payloads = [row_to_payload(r) for r in rows]

        base_map = self.mapper.create_map(
            style=style, heatmap=heatmap, cluster=cluster,
            color_by=color_by, connect_lines=False, popup_cols=popup_cols
        )

        if connect_lines and not heatmap:
            coords = [[row[self.mapper.lat_col], row[self.mapper.lon_col]]
                      for _, row in self.mapper.df.iterrows()]
            import folium
            folium.PolyLine(coords, color='blue', weight=2, opacity=0.7, name='Route').add_to(base_map)

        if not heatmap:
            import folium
            if cluster:
                container = folium.plugins.MarkerCluster(name='Markers')
            else:
                container = folium.FeatureGroup(name='Markers')

            for lat, lon, popup_html, color in marker_payloads:
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    popup=folium.Popup(popup_html, max_width=300),
                    color=color,
                    fill=True,
                    fill_opacity=0.7
                ).add_to(container)

            container.add_to(base_map)
            print(f"✓ Added {len(marker_payloads)} markers (rendered)")

        try:
            import folium
            folium.LayerControl().add_to(base_map)
        except Exception:
            pass

        return base_map


def main():
    parser = argparse.ArgumentParser(description='GeoMapper Pro - smoothing + threading + GUI launcher')
    parser.add_argument('data_file', nargs='?', help='Data file (CSV, GPX, etc.) - optional when launching GUI')
    parser.add_argument('--table', help='SQLite table name')
    parser.add_argument('--style', default='default', help='Map style')
    parser.add_argument('--heatmap', action='store_true')
    parser.add_argument('--cluster', action='store_true')
    parser.add_argument('--color-by', help='Column to color markers by')
    parser.add_argument('--connect-lines', action='store_true')
    parser.add_argument('--popup', nargs='+', metavar='COLUMN', help='Columns for popup')
    parser.add_argument('--output', '-o', help='Output HTML file')
    parser.add_argument('--export-gpx', metavar='FILE')
    parser.add_argument('--export-kml', metavar='FILE')
    parser.add_argument('--validate-only', action='store_true')
    parser.add_argument('--smooth', metavar='EPS', help='Apply RDP smoothing')
    parser.add_argument('--threads', type=int, default=1)
    parser.add_argument('--gui', action='store_true')
    args = parser.parse_args()

    if args.gui:
        gui_path = Path(__file__).parent / 'geomap_gui.py'
        if not gui_path.exists():
            print(f"GUI script not found: {gui_path}")
            return
        import subprocess
        subprocess.Popen([sys.executable, str(gui_path)])
        return

    if not args.data_file:
        print("No input file supplied. Use --gui to launch the graphical interface.")
        return

    pro = GeoMapperPro(args.data_file, threads=args.threads)
    pro.load_and_prepare(args.table)

    if args.validate_only:
        print("Validation complete")
        return

    map_obj = pro.create_map(
        style=args.style,
        heatmap=args.heatmap,
        cluster=args.cluster,
        color_by=args.color_by,
        connect_lines=args.connect_lines,
        popup_cols=args.popup,
        smooth=args.smooth,
        threads=args.threads
    )

    if args.export_gpx:
        pro.mapper.export_gpx(args.export_gpx)
    if args.export_kml:
        pro.mapper.export_kml(args.export_kml)

    pro.mapper.save_map(map_obj, args.output)
    print('Done.')


if __name__ == '__main__':
    main()

