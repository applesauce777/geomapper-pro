import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import tempfile
from pathlib import Path
import sys

# Add parent directory for geomap import
sys.path.insert(0, str(Path(__file__).parent))
from geomap import GeoMapper

# Page config
st.set_page_config(
    page_title="GeoMapper - Interactive Map Generator (Free Demo)",
    page_icon="🗺️",
    layout="wide",
)

# FREE VERSION LIMITS
MAX_DATA_POINTS = 500
ALLOWED_STYLES = ["default", "light"]
GUMROAD_URL = "https://gumroad.com/your-product-link"  # UPDATE THIS

# ----------------------------
# CSS - Applied directly without textwrap
# ----------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #2b0f6b 0%, #0b4b8a 50%, #07102a 100%);
    }
    
    .block-container {
        padding-top: 2rem !important;
        max-width: 1200px;
    }
    
    .glass {
        background: rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        border: 1px solid rgba(155,92,255,0.3);
        box-shadow: 0 6px 30px rgba(3,6,23,0.6);
        backdrop-filter: blur(10px);
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        color: #fff;
    }
    
    .hero-subtitle {
        margin: 8px 0 0 0;
        color: rgba(230,238,248,0.85);
        font-size: 1.1rem;
    }
    
    .pill {
        display: inline-block;
        background: rgba(155,92,255,0.2);
        color: #c9b0ff;
        padding: 0.4rem 1rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.85rem;
        border: 1px solid rgba(155,92,255,0.3);
    }
    
    .upgrade-btn {
        display: inline-block;
        padding: 0.7rem 1.5rem;
        border-radius: 10px;
        background: linear-gradient(90deg, #9b5cff, #4ec6ff);
        color: white !important;
        font-weight: 700;
        text-decoration: none;
        box-shadow: 0 8px 30px rgba(75,0,130,0.3);
        transition: transform 0.15s ease;
    }
    
    .upgrade-btn:hover {
        transform: translateY(-3px);
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.75rem;
        margin-top: 1rem;
    }
    
    .feature-item {
        background: rgba(255,255,255,0.04);
        padding: 0.6rem 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.08);
        color: #fff;
        font-weight: 500;
    }
    
    .example-box {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a0a3e 0%, #0d1f3c 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# HERO SECTION
# ----------------------------
hero_html = f"""
<div class="glass" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
    <div>
        <h1 class="hero-title">🗺️ GeoMapper</h1>
        <p class="hero-subtitle">Transform geographic data into beautiful interactive maps</p>
    </div>
    <div style="display:flex;flex-direction:column;gap:0.5rem;align-items:flex-end;">
        <span class="pill">FREE DEMO</span>
        <a class="upgrade-btn" href="{GUMROAD_URL}" target="_blank">Upgrade →</a>
    </div>
</div>
"""
st.markdown(hero_html, unsafe_allow_html=True)

# ----------------------------
# SIDEBAR
# ----------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    
    style = st.selectbox("Map Style", options=ALLOWED_STYLES)
    st.caption("🔒 Satellite, terrain, toner, dark in full version")
    st.divider()
    
    st.subheader("Visualization Mode")
    viz_mode = st.radio("Select mode", ["Markers"])
    st.caption("🔒 Heatmaps + clustering in full version")
    st.divider()
    
    with st.expander("🎨 Advanced Options"):
        color_by = st.text_input("Color by column", placeholder="category")
        connect_lines = st.checkbox("Connect points with lines")
    
    st.divider()
    
    with st.expander("📍 Column Names (Optional)"):
        lat_col = st.text_input("Latitude column", placeholder="Auto-detect")
        lon_col = st.text_input("Longitude column", placeholder="Auto-detect")

# ----------------------------
# MAIN CONTENT
# ----------------------------
st.markdown('<div class="glass">', unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📁 Upload Data")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx", "xls", "json", "geojson", "parquet"]
    )
    
    if uploaded_file:
        st.success(f"✓ Loaded: {uploaded_file.name}")
        st.caption(f"Size: {len(uploaded_file.getvalue()) / 1024:.1f} KB")

with col2:
    st.subheader("🗺️ Generated Map")
    
    if uploaded_file:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            mapper = GeoMapper(tmp_path)
            
            with st.spinner("Loading data..."):
                mapper.load_data()
                
                with col1:
                    with st.expander("👀 Preview Data"):
                        st.dataframe(mapper.df.head(10), use_container_width=True)
                        st.caption(f"Showing first 10 of {len(mapper.df)} rows")
            
            mapper.detect_coordinate_columns(lat_col or None, lon_col or None)
            mapper.validate_data()
            
            # Free version limit check
            if len(mapper.df) > MAX_DATA_POINTS:
                with col1:
                    st.error(f"❌ Free version limited to {MAX_DATA_POINTS} points. Your file has {len(mapper.df)}.")
                    st.info(f"[Get full version →]({GUMROAD_URL})")
                st.stop()
            
            with col1:
                st.info(f"✓ {len(mapper.df)} valid points — Using: {mapper.lat_col}, {mapper.lon_col}")
                st.caption(f"Remaining: {MAX_DATA_POINTS - len(mapper.df)} points")
            
            with st.spinner("Generating map..."):
                map_obj = mapper.create_map(
                    style=style,
                    heatmap=False,
                    cluster=False,
                    color_by=color_by if color_by else None,
                    connect_lines=connect_lines,
                )
            
            st_folium(map_obj, height=600)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_html:
                map_obj.save(tmp_html.name)
                with open(tmp_html.name, "rb") as f:
                    html_data = f.read()
            
            st.download_button(
                "⬇️ Download Map (HTML)",
                data=html_data,
                file_name=f"{Path(uploaded_file.name).stem}_map.html",
                mime="text/html",
                use_container_width=True,
            )
            
            Path(tmp_path).unlink(missing_ok=True)
        
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.exception(e)
    
    else:
        st.markdown("""
        <div class="example-box">
            <strong>📋 Supported Formats</strong><br>
            <span style="color:rgba(230,238,248,0.8)">CSV, Excel, JSON, GeoJSON, Parquet with latitude & longitude columns</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📋 Example Data Format"):
            example_df = pd.DataFrame({
                "name": ["Location A", "Location B", "Location C"],
                "latitude": [40.7128, 34.0522, 41.8781],
                "longitude": [-74.0060, -118.2437, -87.6298],
                "category": ["Store", "Warehouse", "Store"],
            })
            st.dataframe(example_df, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# UPGRADE CTA
# ----------------------------
st.markdown(
    '<div class="glass">'
    '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">'
    '<div>'
    '<h3 style="margin:0 0 8px 0;color:#fff;">🚀 Upgrade to Full Version</h3>'
    '<p style="margin:0;color:rgba(230,238,248,0.85);">'
    'Unlimited data points, all map styles, heatmaps, clustering & more'
    '</p>'
    '</div>'
    f'<a class="upgrade-btn" href="{GUMROAD_URL}" target="_blank">Get Full Version →</a>'
    '</div>'
    '<div class="feature-grid">'
    '<div class="feature-item">✓ Unlimited data points</div>'
    '<div class="feature-item">✓ All 6 map styles</div>'
    '<div class="feature-item">✓ Heatmaps & clustering</div>'
    '<div class="feature-item">✓ Advanced customization</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

# ----------------------------
# FOOTER
# ----------------------------
st.divider()
st.caption("🗺️ GeoMapper v2.0.0 (Free Demo)")
