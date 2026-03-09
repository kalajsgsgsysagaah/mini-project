import gradio as gr
from fastapi import FastAPI
import pandas as pd
import numpy as np
import pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os, traceback

try:
    import folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# ─────────────────────────────────────────────────────
#  DARK GODAVARI THEME  – no white anywhere
# ─────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600;700&display=swap');

:root {
    --bg-deep:   #060b18;
    --bg-mid:    #0d1530;
    --bg-card:   rgba(255,255,255,0.05);
    --border:    rgba(102,126,234,0.25);
    --accent1:   #667eea;
    --accent2:   #4ecdc4;
    --accent3:   #ffd700;
    --text:      #c8d8ff;
    --text-dim:  #7a8ab0;
    --shadow:    0 8px 32px rgba(0,0,0,0.5);
}

/* ── Page ── */
body, .gradio-container {
    background:
        radial-gradient(ellipse at 20% 10%, rgba(102,126,234,0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(78,205,196,0.12) 0%, transparent 50%),
        linear-gradient(160deg, #060b18 0%, #0d1530 50%, #06101f 100%) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text) !important;
    min-height: 100vh;
}

/* ── Animated header ── */
.gw-header {
    text-align: center;
    padding: 36px 20px 8px;
    position: relative;
}
.gw-header h1 {
    font-family: 'Orbitron', monospace !important;
    font-size: clamp(1.5rem, 3.5vw, 2.6rem) !important;
    background: linear-gradient(90deg, #667eea, #4ecdc4, #ffd700, #667eea);
    background-size: 300% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 4s linear infinite;
    letter-spacing: 2px;
    margin-bottom: 6px !important;
}
@keyframes shimmer { 0%{background-position:0% center} 100%{background-position:300% center} }
.gw-header p { font-size: .95rem; color: var(--text-dim); letter-spacing: .8px; }

/* ── Divider ── */
.gw-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, #667eea 20%, #4ecdc4 50%, #667eea 80%, transparent);
    margin: 12px auto 28px;
    width: 60%;
    opacity: .7;
    box-shadow: 0 0 12px rgba(102,126,234,0.6);
}

/* ── Glass cards ── */
.card {
    background: var(--bg-card) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important;
    box-shadow: var(--shadow), inset 0 1px 0 rgba(102,126,234,0.15) !important;
    padding: 22px !important;
    transition: border-color .3s, box-shadow .3s;
}
.card:hover {
    border-color: rgba(102,126,234,0.5) !important;
    box-shadow: var(--shadow), 0 0 20px rgba(102,126,234,0.15) !important;
}

/* ── Tabs ── */
.tab-nav {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 50px !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
    backdrop-filter: blur(10px);
    margin-bottom: 20px;
}
.tab-nav button {
    border-radius: 45px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-dim) !important;
    transition: all .3s !important;
    letter-spacing: .5px;
}
.tab-nav button.selected {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: #e0e8ff !important;
    box-shadow: 0 4px 16px rgba(102,126,234,0.5) !important;
}

/* ── Input fields ── */
.gr-form, label, .gr-box { background: transparent !important; border: none !important; }
input, .gr-input, textarea, select {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(102,126,234,0.3) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    transition: border .3s, box-shadow .3s !important;
}
input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102,126,234,0.2) !important;
    outline: none !important;
}
label span { font-weight: 600 !important; color: var(--text) !important; font-size: .9rem !important; }
input[type=range] { accent-color: #667eea !important; }

/* ── Dropdowns ── */
.gr-dropdown, ul.options, .multiselect {
    background: #0d1530 !important;
    border-color: rgba(102,126,234,0.35) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}

/* ── Buttons ── */
button.primary, .gr-button-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    border-radius: 50px !important;
    color: #e0e8ff !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 13px 36px !important;
    box-shadow: 0 6px 20px rgba(102,126,234,0.45) !important;
    transition: all .3s ease !important;
    cursor: pointer;
}
button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 28px rgba(102,126,234,0.6) !important;
}
button.secondary {
    background: rgba(102,126,234,0.1) !important;
    border: 1px solid rgba(102,126,234,0.4) !important;
    border-radius: 50px !important;
    color: var(--accent1) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    transition: all .3s !important;
}
button.secondary:hover {
    background: rgba(102,126,234,0.2) !important;
    border-color: #667eea !important;
}

/* ── Section title ── */
.section-title {
    font-family: 'Orbitron', monospace !important;
    color: #667eea !important;
    font-size: .95rem !important;
    letter-spacing: 1.5px;
    border-left: 3px solid #4ecdc4;
    padding-left: 10px;
    margin-bottom: 14px;
    text-transform: uppercase;
}

/* ── Prediction result box ── */
.gr-textbox {
    background: rgba(102,126,234,0.08) !important;
    border: 1px solid rgba(102,126,234,0.4) !important;
    border-radius: 14px !important;
    color: #ffd700 !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    font-family: 'Orbitron', monospace !important;
    text-align: center !important;
}

/* ── Footer ── */
.gw-footer {
    text-align: center;
    padding: 24px 0 16px;
    color: var(--text-dim);
    font-size: .82rem;
}
.gw-footer span {
    display: inline-block;
    padding: 5px 18px;
    background: rgba(102,126,234,0.1);
    border: 1px solid rgba(102,126,234,0.25);
    border-radius: 20px;
}

footer { display: none !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #060b18; }
::-webkit-scrollbar-thumb { background: rgba(102,126,234,0.4); border-radius: 6px; }
"""

# ─────────────────────────────────────────────
#  Load model
# ─────────────────────────────────────────────
MODEL_PATH         = os.path.join("src", "models", "groundwater_model.pkl")
UNIQUE_VALUES_PATH = os.path.join("src", "models", "unique_values.pkl")
DATA_PATH          = "godavari_groundwater_synthetic_dataset.csv"

model = None; unique_values = {}

try:
    with open(MODEL_PATH, 'rb') as f: model = pickle.load(f); print("✅ Model loaded.")
except Exception as e: print(f"⚠️ {e}")
try:
    with open(UNIQUE_VALUES_PATH, 'rb') as f: unique_values = pickle.load(f); print("✅ UV loaded.")
except:
    unique_values = {'Geology':['Gneiss','Schist','Granite','Basalt'],
                     'Geomorphology':['Flood Plain','Pediplain','Hills'],
                     'Soil':['Red Soil','Black Cotton Soil','Alluvial'],
                     'LULC':['Agriculture','Forest','Water Body']}

# ─────────────────────────────────────────────
#  Station master data
# ─────────────────────────────────────────────
STATIONS = {
    "Bhadrachalam":    {"lat":17.668,"lon":80.893,"avg_discharge":1340,"peak_discharge":3400,"min_discharge":370,"current_level":46.5,"monsoon_flow":3200,"groundwater_zone":"High Potential Zone","aquifer_type":"Basalt with Granitic Gneiss","depth_to_water":8.5,"water_quality":"Good","yield_potential":"High (15-25 lpm)","recharge_rate":"Medium (500-750 mm/year)","density":"Moderate - 1 well/2 ha","soil_type":"Black Soil & Red Soil","geological_formation":"Deccan Basalt & Archean Granite","recommendation":"Suitable for irrigation wells"},
    "Ramagundam NTPC": {"lat":18.755,"lon":79.513,"avg_discharge":1158,"peak_discharge":3000,"min_discharge":280,"current_level":43.2,"monsoon_flow":2800,"groundwater_zone":"Moderate Potential Zone","aquifer_type":"Granite with Quartzite","depth_to_water":12.3,"water_quality":"Good","yield_potential":"Moderate (8-15 lpm)","recharge_rate":"Low (350-500 mm/year)","density":"Low - 1 well/3-4 ha","soil_type":"Red Soil & Laterite","geological_formation":"Archean Granite & Pegmatite","recommendation":"Suitable for domestic wells"},
    "Dowleswaram":     {"lat":16.934,"lon":81.771,"avg_discharge":1492,"peak_discharge":3700,"min_discharge":410,"current_level":47.5,"monsoon_flow":3500,"groundwater_zone":"Very High Potential Zone","aquifer_type":"Alluvium & Basalt","depth_to_water":6.2,"water_quality":"Excellent","yield_potential":"Very High (25-40 lpm)","recharge_rate":"High (750-1000 mm/year)","density":"High - 1 well/1.5 ha","soil_type":"Alluvial Soil","geological_formation":"Recent Alluvium","recommendation":"Highly suitable for large scale irrigation"},
    "Pattiseema":      {"lat":17.136,"lon":81.609,"avg_discharge":1280,"peak_discharge":3300,"min_discharge":360,"current_level":46.2,"monsoon_flow":3150,"groundwater_zone":"High Potential Zone","aquifer_type":"Basalt & Alluvium","depth_to_water":7.8,"water_quality":"Good","yield_potential":"High (18-28 lpm)","recharge_rate":"High (650-850 mm/year)","density":"Moderate-High - 1 well/2 ha","soil_type":"Black Soil & Alluvial","geological_formation":"Deccan Basalt & Alluvium","recommendation":"Suitable for irrigation & domestic use"},
    "Rajahmundry":     {"lat":17.000,"lon":81.804,"avg_discharge":1420,"peak_discharge":3620,"min_discharge":395,"current_level":47.2,"monsoon_flow":3400,"groundwater_zone":"Very High Potential Zone","aquifer_type":"Alluvium & Basalt","depth_to_water":5.8,"water_quality":"Excellent","yield_potential":"Very High (28-42 lpm)","recharge_rate":"High (780-1050 mm/year)","density":"High - 1 well/1.2 ha","soil_type":"Deep Alluvial Soil","geological_formation":"Recent Alluvium & Basalt","recommendation":"Highly suitable for large-scale irrigation and industrial use"},
}

ORDER_MAP = {'Very Low':0,'Low':1,'Moderate':2,'High':3,'Very High':4}
ZONE_COLOR = {'Very High Potential Zone':'#4ecdc4','High Potential Zone':'#667eea',
               'Moderate Potential Zone':'#ffd700','Low Potential Zone':'#ff6b6b',
               'Very Low Potential Zone':'#ff4040'}
CLASS_COLOR = {'Very Low':'#ff4040','Low':'#ff9f40','Moderate':'#ffd700','High':'#667eea','Very High':'#4ecdc4'}

def dark_fig(w=8, h=4.5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.set_facecolor('#060b18')
    ax.set_facecolor('#0d1530')
    ax.tick_params(colors='#c8d8ff', labelsize=9)
    ax.xaxis.label.set_color('#c8d8ff')
    ax.yaxis.label.set_color('#c8d8ff')
    ax.title.set_color('#e0e8ff')
    for sp in ax.spines.values(): sp.set_color('#667eea'); sp.set_linewidth(0.5)
    ax.grid(True, linestyle='--', alpha=0.2, color='#667eea')
    return fig, ax

# ─────────────────────────────────────────────
#  TAB 1: Prediction
# ─────────────────────────────────────────────
def predict_groundwater(geology, geomorphology, soil, slope, drainage,
                        lineament, lulc, ndvi, savi, rainfall, station):
    print(f"[PREDICT] called: geo={geology}, rain={rainfall}, station={station}")
    if model is None:
        return "⚠️ Model not loaded", None
    try:
        inp = pd.DataFrame([{
            'Geology':           str(geology),
            'Geomorphology':     str(geomorphology),
            'Soil':              str(soil),
            'Slope_percent':     float(slope),
            'Drainage_Density':  float(drainage),
            'Lineament_Density': float(lineament),
            'LULC':              str(lulc),
            'NDVI':              float(ndvi),
            'SAVI':              float(savi),
            'Rainfall_mm':       float(rainfall),
        }])
        pred  = model.predict(inp)[0]
        probs = model.predict_proba(inp)[0]
        cls   = model.classes_
        print(f"[PREDICT] result={pred}")

        idx = sorted(range(len(cls)), key=lambda k: ORDER_MAP.get(cls[k], -1))
        sc  = [cls[i]   for i in idx]
        sp  = [probs[i] for i in idx]
        col = [CLASS_COLOR.get(cls[i], '#667eea') for i in idx]

        fig, ax = dark_fig(7, 4)
        bars = ax.bar(sc, sp, color=col, width=0.5, alpha=0.85,
                      edgecolor='none', linewidth=0)
        ax.bar(sc, sp, color=col, width=0.58, alpha=0.18, linewidth=0)
        if pred in sc:
            hi = sc.index(pred)
            bars[hi].set_edgecolor('#ffd700')
            bars[hi].set_linewidth(2.5)

        for i, p in enumerate(sp):
            ax.text(i, p + 0.03, f'{p:.2f}', ha='center', va='bottom',
                    fontsize=9, color='#c8d8ff', fontweight='bold')

        ax.set_ylim(0, 1.2)
        ax.set_ylabel('Probability', color='#c8d8ff', fontsize=10)
        station_label = f" — {station}" if station else ""
        ax.set_title(f'Predicted Zone: {pred}{station_label}', fontsize=13, color='#ffd700',
                     fontweight='bold', pad=14, fontfamily='sans-serif')
        ax.set_xticks(range(len(sc)))
        ax.set_xticklabels(sc, fontsize=10, color='#c8d8ff')
        plt.tight_layout()
        return f"🌍 {pred}", fig

    except Exception as e:
        traceback.print_exc()
        return f"❌ Error: {e}", None

# ─────────────────────────────────────────────
#  TAB 2: Geospatial Map — highlight selected station
# ─────────────────────────────────────────────
def generate_map(selected_station="", predicted_zone=None):
    if model is None:
        return None, "<p>Model not loaded.</p>"
    try:
        df = pd.read_csv(DATA_PATH)
        df['lat'] = df['Station'].map(lambda x: STATIONS.get(x, {}).get('lat', 17.0))
        df['lon'] = df['Station'].map(lambda x: STATIONS.get(x, {}).get('lon', 80.0))

        features = ['Geology', 'Geomorphology', 'Soil', 'Slope_percent', 'Drainage_Density',
                    'Lineament_Density', 'LULC', 'NDVI', 'SAVI', 'Rainfall_mm']

        if all(f in df.columns for f in features):
            df['Prediction'] = model.predict(df[features])
        else:
            df['Prediction'] = df['Groundwater_Potential_Class']

        def get_mode(s): m = s.mode(); return m.iloc[0] if len(m) > 0 else "Unknown"
        sc_df   = df.groupby('Station')['Prediction'].agg(get_mode).reset_index()
        sc_dict = dict(zip(sc_df['Station'], sc_df['Prediction']))
        cnt     = df.groupby('Station').size().to_dict()

        np.random.seed(42)
        df['lat_j']   = df['lat'] + np.random.normal(0, .04, len(df))
        df['lon_j']   = df['lon'] + np.random.normal(0, .04, len(df))
        df['pot_num'] = df['Prediction'].map(ORDER_MAP)

        from matplotlib.colors import ListedColormap
        dark_map = ListedColormap(['#ff4040','#ff9f40','#ffd700','#667eea','#4ecdc4'])

        fig = plt.figure(figsize=(12, 6), facecolor='#060b18')
        ax  = fig.add_axes([0.04, 0.08, 0.61, 0.84], facecolor='#0d1a35')

        try:
            from scipy.interpolate import griddata
            from scipy.ndimage     import gaussian_filter
            gx, gy = np.mgrid[df['lon_j'].min():df['lon_j'].max():130j,
                               df['lat_j'].min():df['lat_j'].max():130j]
            gz   = griddata((df['lon_j'], df['lat_j']), df['pot_num'], (gx, gy), method='nearest')
            gz_b = gaussian_filter(gz.astype(float), sigma=4)
            ax.contourf(gx, gy, gz_b, levels=np.arange(-.5, 5, 1),
                        cmap=dark_map, alpha=.35, zorder=1, vmin=0, vmax=4)
        except Exception: pass

        ax.scatter(df['lon_j'], df['lat_j'], c=df['pot_num'], cmap=dark_map,
                   s=40, edgecolors='#060b18', linewidths=.5, zorder=2, alpha=.65, vmin=0, vmax=4)

        label_offsets = {
            'Bhadrachalam':    (-0.32,  0.14),
            'Ramagundam NTPC': (-0.30,  0.14),
            'Dowleswaram':     ( 0.28, -0.15),
            'Pattiseema':      (-0.32, -0.15),
            'Rajahmundry':     ( 0.28,  0.13),
        }
        for stn, info in STATIONS.items():
            lat, lon = info['lat'], info['lon']
            dom = sc_dict.get(stn, 'N/A')
            
            # OVERRIDE historical Prediction with Live Prediction from Tab 1
            if stn == selected_station and predicted_zone is not None:
                dom = predicted_zone
                
            bc  = CLASS_COLOR.get(dom, '#667eea')
            lo, la = label_offsets.get(stn, (0.2, 0.12))
            is_selected = (stn == selected_station)
            marker_size = 22 if is_selected else 15
            marker_edge = '#ffffff' if is_selected else '#060b18'
            ax.plot(lon, lat, marker='*', markersize=marker_size, color='#ffd700',
                    markeredgecolor=marker_edge, markeredgewidth=1.5 if is_selected else 0.8, zorder=5)
            label_text = f" ★ {stn}\n [{dom}]" if is_selected else f" {stn}\n [{dom}]"
            ax.annotate(label_text, xy=(lon, lat),
                        xytext=(lon + lo, lat + la),
                        fontsize=7.5, fontweight='bold',
                        ha='left' if lo >= 0 else 'right', va='center',
                        bbox=dict(facecolor='#0d1530', alpha=.90,
                                  edgecolor='#ffd700' if is_selected else bc,
                                  boxstyle='round,pad=0.4', linewidth=2.5 if is_selected else 1.5),
                        color='#ffd700' if is_selected else bc,
                        arrowprops=dict(arrowstyle='->', color='#ffd700' if is_selected else bc, lw=1.2,
                                        connectionstyle='arc3,rad=0.2'), zorder=6)

        title_stn = f" — Highlighted: {selected_station}" if selected_station else ""
        ax.set_title(f"Groundwater Zoning — Godavari Basin{title_stn}",
                     fontsize=12, fontweight='bold', color='#e0e8ff', pad=10)
        ax.set_xlabel("Longitude", fontsize=9, color='#7a8ab0')
        ax.set_ylabel("Latitude",  fontsize=9, color='#7a8ab0')
        ax.tick_params(labelsize=8, colors='#7a8ab0')
        ax.grid(True, linestyle='--', alpha=.2, color='#667eea')
        for sp in ax.spines.values(): sp.set_color('#667eea'); sp.set_linewidth(.5)

        legend_els = [mpatches.Patch(facecolor=CLASS_COLOR[l], edgecolor='#060b18', label=l)
                      for l in ['Very Low','Low','Moderate','High','Very High']]
        star_p = plt.Line2D([0],[0], marker='*', color='w', markerfacecolor='#ffd700',
                            markersize=10, label='Station')
        ax.legend(handles=legend_els + [star_p], loc='lower left',
                  title='Legend', fontsize=7.5, title_fontsize=8.5,
                  framealpha=.85, facecolor='#0d1530', edgecolor='#667eea',
                  labelcolor='#c8d8ff')

        # Right: station table
        tax = fig.add_axes([0.67, 0.08, 0.31, 0.84], facecolor='#0d1530')
        tax.axis('off')
        col_lbls = ['Station', 'Zone', 'Records']
        tdata = [[stn, sc_dict.get(stn, 'N/A'), str(cnt.get(stn, 0))] for stn in STATIONS]
        tbl = tax.table(cellText=tdata, colLabels=col_lbls, cellLoc='center', loc='center')
        tbl.auto_set_font_size(False); tbl.set_fontsize(7.5); tbl.scale(1, 1.9)
        for ci in range(len(col_lbls)):
            tbl[0, ci].set_facecolor('#667eea')
            tbl[0, ci].set_text_props(color='#e0e8ff', fontweight='bold')
        for ri, row in enumerate(tdata, 1):
            dom = row[1]
            is_sel_row = (row[0] == selected_station)
            for ci in range(len(col_lbls)):
                tbl[ri, ci].set_facecolor('#1a2a60' if is_sel_row else ('#0d1a35' if ri % 2 == 0 else '#0d1530'))
                tbl[ri, ci].set_text_props(
                    color=CLASS_COLOR.get(dom,'#c8d8ff') if ci==1 else ('#ffd700' if is_sel_row else '#c8d8ff'),
                    fontweight='bold' if (ci==1 or is_sel_row) else 'normal')
                tbl[ri, ci].set_edgecolor('#ffd700' if is_sel_row else '#667eea')
        tax.set_title("📍 Stations", fontsize=9, fontweight='bold', pad=6, color='#4ecdc4')
        return fig, ""
    except Exception as e:
        traceback.print_exc()
        return None, f"<p>Error: {e}</p>"

# ─────────────────────────────────────────────
#  TAB 3: Godavari Dashboard
# ─────────────────────────────────────────────
def make_folium_map(selected_station=""):
    """Render Folium map with WHITE tile background. Highlights selected station."""
    if not HAS_FOLIUM: return "<p>pip install folium</p>"
    # Use CartoDB Positron (white/light map) instead of dark_matter
    m = folium.Map(location=[17.8, 80.5], zoom_start=7, tiles='CartoDB positron')
    for stn, d in STATIONS.items():
        col  = ZONE_COLOR.get(d['groundwater_zone'], '#667eea')
        size = 12 + d['avg_discharge'] / 110
        is_selected = (stn == selected_station)
        border_color = '#ff6b00' if is_selected else col
        border_width = 5 if is_selected else 3
        html = f"""
        <div style="font-family:Inter,sans-serif;width:380px;
                    background:linear-gradient(135deg,#0d1530,#1a2050);
                    padding:16px;border-radius:14px;color:#c8d8ff;
                    border:1px solid rgba(102,126,234,0.4);
                    box-shadow:0 8px 32px rgba(0,0,0,0.7);">
          <h3 style="margin:0 0 12px;font-size:17px;color:#ffd700;">🎯 {stn} {'⭐ SELECTED' if is_selected else ''}</h3>
          <div style="background:rgba(255,255,255,0.05);padding:10px;border-radius:10px;margin-bottom:10px;">
            <h4 style="margin:0 0 8px;color:#4ecdc4;font-size:13px;">💧 Water Discharge</h4>
            <table style="width:100%;font-size:12px;">
              <tr><td>Avg Discharge:</td><td align="right"><b style="color:#ffd700">{d['avg_discharge']} MCM</b></td></tr>
              <tr><td>Peak:</td><td align="right"><b>{d['peak_discharge']} MCM</b></td></tr>
              <tr><td>Minimum:</td><td align="right"><b>{d['min_discharge']} MCM</b></td></tr>
              <tr><td>Monsoon Flow:</td><td align="right"><b>{d['monsoon_flow']} MCM</b></td></tr>
              <tr><td>Water Level:</td><td align="right"><b>{d['current_level']} m</b></td></tr>
            </table>
          </div>
          <div style="background:rgba(255,255,255,0.05);padding:10px;border-radius:10px;">
            <h4 style="margin:0 0 8px;font-size:13px;color:#667eea;">🌍 Groundwater Zone</h4>
            <table style="width:100%;font-size:12px;">
              <tr><td>Zone:</td><td align="right"><b style="color:{col}">{d['groundwater_zone']}</b></td></tr>
              <tr><td>Aquifer:</td><td align="right"><b>{d['aquifer_type']}</b></td></tr>
              <tr><td>Depth:</td><td align="right"><b>{d['depth_to_water']} m</b></td></tr>
              <tr><td>Quality:</td><td align="right"><b>{d['water_quality']}</b></td></tr>
              <tr><td>Yield:</td><td align="right"><b>{d['yield_potential']}</b></td></tr>
              <tr><td>Recharge:</td><td align="right"><b>{d['recharge_rate']}</b></td></tr>
              <tr><td>Well Density:</td><td align="right"><b>{d['density']}</b></td></tr>
              <tr><td>Soil:</td><td align="right"><b>{d['soil_type']}</b></td></tr>
              <tr><td>Geology:</td><td align="right"><b>{d['geological_formation']}</b></td></tr>
            </table>
            <div style="background:rgba(102,126,234,0.2);padding:8px;margin-top:8px;
                        border-radius:8px;border:1px solid rgba(102,126,234,0.4);
                        color:#ffd700;font-weight:bold;font-size:12px;">
              ✅ {d['recommendation']}
            </div>
          </div>
        </div>"""
        folium.CircleMarker(
            location=[d['lat'], d['lon']],
            radius=size + (4 if is_selected else 0),
            popup=folium.Popup(html, max_width=430),
            tooltip=f"<b style='font-size:13px'>{stn}</b><br>{d['groundwater_zone']}<br>Avg: {d['avg_discharge']} MCM",
            color=border_color, fill=True, fillColor=col, fillOpacity=0.85, weight=border_width
        ).add_to(m)
    return m._repr_html_()


def make_discharge_chart(selected_station=""):
    if not HAS_PLOTLY: return None
    stns = list(STATIONS.keys())
    fig  = go.Figure()
    for label, key, col in [('Average','avg_discharge','#667eea'),
                              ('Peak','peak_discharge','#4ecdc4'),
                              ('Minimum','min_discharge','#ff6b6b')]:
        marker_colors = []
        marker_lines  = []
        for s in stns:
            if s == selected_station:
                marker_colors.append('#ffd700')
                marker_lines.append(dict(color='#ffffff', width=2))
            else:
                marker_colors.append(col)
                marker_lines.append(dict(color='#060b18', width=1))
        fig.add_trace(go.Bar(name=label, x=stns,
                             y=[STATIONS[s][key] for s in stns],
                             marker_color=marker_colors,
                             marker_line_color=[ml['color'] for ml in marker_lines],
                             marker_line_width=[ml['width'] for ml in marker_lines]))
    title_text = f'<b>Discharge Comparison (MCM)</b>' + (f' — {selected_station} highlighted' if selected_station else '')
    fig.update_layout(
        title=dict(text=title_text, font=dict(family='Inter',size=16,color='#e0e8ff'),x=.5),
        barmode='group', bargap=.18,
        plot_bgcolor='#0d1530', paper_bgcolor='#060b18',
        font=dict(color='#c8d8ff', family='Inter'),
        xaxis=dict(gridcolor='rgba(102,126,234,0.15)', linecolor='#667eea'),
        yaxis=dict(title='MCM', gridcolor='rgba(102,126,234,0.15)', linecolor='#667eea'),
        legend=dict(bgcolor='rgba(13,21,48,0.8)', bordercolor='rgba(102,126,234,.4)', borderwidth=1),
        margin=dict(t=55,b=50,l=55,r=20), hovermode='x unified',
    )
    return fig


def make_gw_chart(selected_station=""):
    if not HAS_PLOTLY: return None
    stns  = list(STATIONS.keys())
    depth = [STATIONS[s]['depth_to_water'] for s in stns]
    rech  = [float(STATIONS[s]['recharge_rate'].split('(')[1].split('-')[0].strip()) for s in stns]
    level = [STATIONS[s]['current_level'] for s in stns]
    fig   = go.Figure()
    for lbl, vals, col, dash in [
        ('Depth to Water (m)', depth, '#ff6b6b', 'solid'),
        ('Min Recharge(mm/yr)', rech, '#4ecdc4', 'solid'),
        ('Water Level (m)',    level, '#ffd700', 'dot'),
    ]:
        marker_colors = ['#ffffff' if s == selected_station else col for s in stns]
        marker_sizes  = [14 if s == selected_station else 9 for s in stns]
        fig.add_trace(go.Scatter(x=stns, y=vals, mode='lines+markers', name=lbl,
                                 line=dict(color=col, width=2.5, dash=dash),
                                 marker=dict(size=marker_sizes, color=marker_colors,
                                             line=dict(color='#060b18', width=1.5))))
    title_text = '<b>Groundwater Parameters</b>' + (f' — {selected_station} highlighted' if selected_station else '')
    fig.update_layout(
        title=dict(text=title_text, font=dict(family='Inter',size=16,color='#e0e8ff'),x=.5),
        plot_bgcolor='#0d1530', paper_bgcolor='#060b18',
        font=dict(color='#c8d8ff', family='Inter'),
        xaxis=dict(gridcolor='rgba(102,126,234,0.15)', linecolor='#667eea'),
        yaxis=dict(title='Value', gridcolor='rgba(102,126,234,0.15)', linecolor='#667eea'),
        legend=dict(bgcolor='rgba(13,21,48,0.8)', bordercolor='rgba(102,126,234,.4)', borderwidth=1),
        margin=dict(t=55,b=50,l=55,r=20), hovermode='x unified',
    )
    return fig


def station_detail(name):
    if not name or name not in STATIONS:
        return "<p style='color:#7a8ab0;padding:20px'>Pick a station above.</p>"
    d  = STATIONS[name]
    bc = ZONE_COLOR.get(d['groundwater_zone'], '#667eea')
    return f"""
    <div style="background:linear-gradient(135deg,#0d1530,#1a2050);
                padding:22px;border-radius:18px;color:#c8d8ff;
                border:1px solid rgba(102,126,234,0.35);
                box-shadow:0 8px 32px rgba(0,0,0,0.5);font-family:Inter,sans-serif;">
      <h2 style="margin:0 0 18px;color:#ffd700;font-size:24px">📍 {name}</h2>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px;">
        <div style="background:rgba(255,255,255,0.05);padding:14px;border-radius:12px;
                    border:1px solid rgba(102,126,234,0.2);">
          <h3 style="margin:0 0 10px;color:#4ecdc4;font-size:14px;">⚡ Water Metrics</h3>
          <p style="margin:5px 0"><b>Avg Discharge:</b> {d['avg_discharge']} MCM</p>
          <p style="margin:5px 0"><b>Peak Discharge:</b> {d['peak_discharge']} MCM</p>
          <p style="margin:5px 0"><b>Min Discharge:</b>  {d['min_discharge']} MCM</p>
          <p style="margin:5px 0"><b>Monsoon Flow:</b>   {d['monsoon_flow']} MCM</p>
          <p style="margin:5px 0"><b>Water Level:</b>    {d['current_level']} m</p>
        </div>
        <div style="background:rgba(255,255,255,0.05);padding:14px;border-radius:12px;
                    border:1px solid rgba(102,126,234,0.2);">
          <h3 style="margin:0 0 10px;color:#667eea;font-size:14px;">🌍 Groundwater Zone</h3>
          <p style="margin:5px 0;color:{bc};font-weight:700;font-size:15px">{d['groundwater_zone']}</p>
          <p style="margin:5px 0"><b>Aquifer:</b>  {d['aquifer_type']}</p>
          <p style="margin:5px 0"><b>Depth:</b>    {d['depth_to_water']} m</p>
          <p style="margin:5px 0"><b>Quality:</b>  {d['water_quality']}</p>
          <p style="margin:5px 0"><b>Yield:</b>    {d['yield_potential']}</p>
        </div>
      </div>
      <div style="background:rgba(255,255,255,0.05);padding:14px;border-radius:12px;
                  border:1px solid rgba(102,126,234,0.2);margin-bottom:14px;">
        <h3 style="margin:0 0 10px;color:#ffd700;font-size:14px;">🔬 Characteristics</h3>
        <p style="margin:5px 0"><b>Recharge:</b>    {d['recharge_rate']}</p>
        <p style="margin:5px 0"><b>Well Density:</b> {d['density']}</p>
        <p style="margin:5px 0"><b>Soil:</b>         {d['soil_type']}</p>
        <p style="margin:5px 0"><b>Geology:</b>      {d['geological_formation']}</p>
      </div>
      <div style="background:rgba(102,126,234,0.15);padding:14px;border-radius:12px;
                  border:1px solid {bc};color:#ffd700;font-weight:700;font-size:14px;">
        ✅ {d['recommendation']}
      </div>
    </div>"""


def make_summary_df(selected_station=""):
    rows = []
    for s, d in STATIONS.items():
        rows.append({
            "Station": ("⭐ " + s) if s == selected_station else s,
            "Avg Discharge(MCM)": d['avg_discharge'],
            "Zone": d['groundwater_zone'],
            "Depth(m)": d['depth_to_water'],
            "Quality": d['water_quality'],
            "Yield": d['yield_potential'],
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
#  TAB 4: Model Accuracy
# ─────────────────────────────────────────────
def get_accuracy_html():
    """Compute model accuracy, classification report from CSV and return styled HTML."""
    if model is None:
        return "<p style='color:#ff6b6b;padding:20px'>Model not loaded.</p>"
    try:
        from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
        df = pd.read_csv(DATA_PATH)
        features = ['Geology','Geomorphology','Soil','Slope_percent','Drainage_Density',
                    'Lineament_Density','LULC','NDVI','SAVI','Rainfall_mm']
        target   = 'Groundwater_Potential_Class'
        if not all(f in df.columns for f in features) or target not in df.columns:
            return "<p style='color:#ff6b6b;padding:20px'>Dataset columns mismatch.</p>"

        X = df[features]
        y = df[target]
        y_pred = model.predict(X)

        acc = accuracy_score(y, y_pred)
        report = classification_report(y, y_pred, output_dict=True, zero_division=0)

        # Remove non-class keys
        classes = [k for k in report if k not in ('accuracy','macro avg','weighted avg')]
        classes_sorted = sorted(classes, key=lambda x: ORDER_MAP.get(x, -1))

        # ── HTML ──
        acc_color = '#4ecdc4' if acc >= 0.90 else ('#ffd700' if acc >= 0.75 else '#ff9f40')
        html = f"""
        <div style="font-family:Inter,sans-serif;padding:20px;">
          <div style="text-align:center;margin-bottom:24px;">
            <div style="font-size:3.5rem;font-weight:800;color:{acc_color};
                        font-family:'Orbitron',monospace;letter-spacing:2px;">
              {acc*100:.2f}%
            </div>
            <div style="color:#c8d8ff;font-size:1.1rem;margin-top:6px;">Overall Model Accuracy</div>
            <div style="color:#7a8ab0;font-size:0.85rem;margin-top:4px;">
              Evaluated on all {len(df):,} records from the Godavari dataset
            </div>
          </div>

          <div style="background:rgba(102,126,234,0.08);border:1px solid rgba(102,126,234,0.3);
                      border-radius:14px;padding:16px;margin-bottom:20px;">
            <div style="color:#667eea;font-family:'Orbitron',monospace;font-size:0.85rem;
                        letter-spacing:1.5px;text-transform:uppercase;border-left:3px solid #4ecdc4;
                        padding-left:10px;margin-bottom:14px;">📊 Per-Class Metrics</div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;
                        font-size:0.8rem;color:#7a8ab0;font-weight:700;
                        padding:0 6px 8px;border-bottom:1px solid rgba(102,126,234,0.2);">
              <span>Class</span><span style="text-align:center;">Precision</span>
              <span style="text-align:center;">Recall</span>
            </div>
        """
        for cls in classes_sorted:
            r       = report[cls]
            prec    = r['precision']
            rec     = r['recall']
            bc      = CLASS_COLOR.get(cls, '#667eea')
            prec_w  = min(int(prec*100), 100)
            rec_w   = min(int(rec*100),  100)
            html += f"""
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;
                        align-items:center;padding:8px 6px;
                        border-bottom:1px solid rgba(102,126,234,0.1);">
              <span style="color:{bc};font-weight:700;font-size:0.85rem;">{cls}</span>
              <div>
                <div style="background:rgba(255,255,255,0.08);border-radius:999px;
                            height:8px;overflow:hidden;margin-bottom:2px;">
                  <div style="width:{prec_w}%;height:100%;background:{bc};
                              border-radius:999px;"></div>
                </div>
                <div style="text-align:center;color:#c8d8ff;font-size:0.78rem;">{prec:.3f}</div>
              </div>
              <div>
                <div style="background:rgba(255,255,255,0.08);border-radius:999px;
                            height:8px;overflow:hidden;margin-bottom:2px;">
                  <div style="width:{rec_w}%;height:100%;background:{bc};
                              border-radius:999px;"></div>
                </div>
                <div style="text-align:center;color:#c8d8ff;font-size:0.78rem;">{rec:.3f}</div>
              </div>
            </div>"""

        # Weighted avg row
        wa = report['weighted avg']
        html += f"""
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;
                        align-items:center;padding:10px 6px;
                        background:rgba(102,126,234,0.1);border-radius:8px;margin-top:4px;">
              <span style="color:#ffd700;font-weight:700;font-size:0.85rem;">Weighted Avg</span>
              <div style="text-align:center;color:#ffd700;font-weight:700;">{wa['precision']:.3f}</div>
              <div style="text-align:center;color:#ffd700;font-weight:700;">{wa['recall']:.3f}</div>
            </div>
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;">
            <div style="background:rgba(102,126,234,0.08);border:1px solid rgba(102,126,234,0.3);
                        border-radius:12px;padding:14px;text-align:center;">
              <div style="color:#7a8ab0;font-size:0.78rem;text-transform:uppercase;
                          letter-spacing:1px;margin-bottom:6px;">Algorithm</div>
              <div style="color:#c8d8ff;font-weight:700;">Random Forest</div>
            </div>
            <div style="background:rgba(78,205,196,0.08);border:1px solid rgba(78,205,196,0.3);
                        border-radius:12px;padding:14px;text-align:center;">
              <div style="color:#7a8ab0;font-size:0.78rem;text-transform:uppercase;
                          letter-spacing:1px;margin-bottom:6px;">Training Records</div>
              <div style="color:#4ecdc4;font-weight:700;">{len(df):,}</div>
            </div>
            <div style="background:rgba(255,215,0,0.08);border:1px solid rgba(255,215,0,0.3);
                        border-radius:12px;padding:14px;text-align:center;">
              <div style="color:#7a8ab0;font-size:0.78rem;text-transform:uppercase;
                          letter-spacing:1px;margin-bottom:6px;">Classes</div>
              <div style="color:#ffd700;font-weight:700;">{len(classes_sorted)}</div>
            </div>
          </div>
        </div>"""
        return html
    except Exception as e:
        traceback.print_exc()
        return f"<p style='color:#ff6b6b;padding:20px'>Error computing accuracy: {e}</p>"


# ─────────────────────────────────────────────
#  Master update: called when station changes or on Predict
# ─────────────────────────────────────────────
def update_all_tabs(station, predicted_zone=None):
    """Update Geospatial Map, Folium map HTML, Discharge chart, GW chart, Station detail, Summary table."""
    map_fig, map_html    = generate_map(station, predicted_zone)
    folium_html          = make_folium_map(station)
    discharge_fig        = make_discharge_chart(station)
    gw_fig               = make_gw_chart(station)
    stn_detail_html      = station_detail(station)
    summary_df           = make_summary_df(station)
    return map_fig, map_html, folium_html, discharge_fig, gw_fig, stn_detail_html, summary_df

def predict_and_update_all(*args):
    """Runs prediction, then updates all tabs based on the new prediction."""
    station = args[-1]
    # 1. Predict
    txt, plot = predict_groundwater(*args)
    
    # Extract just the string predicted zone (removing the '🌍 ' prefix)
    predicted_zone = txt.replace('🌍 ', '') if type(txt) == str else None
    
    # 2. Update dashboard with live prediction override
    map_fig, map_html, folium_html, discharge_fig, gw_fig, stn_detail_html, summary_df = update_all_tabs(station, predicted_zone)
    
    return txt, plot, map_fig, map_html, folium_html, discharge_fig, gw_fig, stn_detail_html, summary_df


# ─────────────────────────────────────────────
#  Gradio App
# ─────────────────────────────────────────────
with gr.Blocks(title="Groundwater ML — Godavari Basin") as app:

    gr.HTML("""
    <div class="gw-header">
      <h1>💧 GROUNDWATER POTENTIAL ZONING</h1>
      <p>Geospatial Analysis · Random Forest · Godavari Basin · Telangana</p>
      <div class="gw-divider"></div>
    </div>""")

    # Shared station state (drives all tabs)
    shared_station = gr.State(value=list(STATIONS.keys())[0])

    with gr.Tabs(elem_classes="tab-nav"):

        # ── TAB 1: Prediction ─────────────────────────────────────────────
        with gr.TabItem("🔍 Prediction"):
            with gr.Row():
                with gr.Column(scale=1, elem_classes="card"):
                    gr.HTML("<div class='section-title'>📍 Select Station</div>")
                    tab1_station = gr.Dropdown(
                        choices=list(STATIONS.keys()),
                        value=list(STATIONS.keys())[0],
                        label="Station",
                    )
                    gr.HTML("<div class='section-title' style='margin-top:16px'>🌍 Hydro-Geological Parameters</div>")
                    feat_geo  = gr.Dropdown(choices=unique_values.get('Geology',[]),
                                            label="Geology",
                                            value=unique_values.get('Geology',[''])[0])
                    feat_gm   = gr.Dropdown(choices=unique_values.get('Geomorphology',[]),
                                            label="Geomorphology",
                                            value=unique_values.get('Geomorphology',[''])[0])
                    feat_soil = gr.Dropdown(choices=unique_values.get('Soil',[]),
                                            label="Soil Type",
                                            value=unique_values.get('Soil',[''])[0])
                    feat_lulc = gr.Dropdown(choices=unique_values.get('LULC',[]),
                                            label="Land Use / Cover",
                                            value=unique_values.get('LULC',[''])[0])
                    gr.HTML("<div class='section-title' style='margin-top:16px'>📐 Topography & Climate</div>")
                    feat_slope = gr.Slider(0, 50,   value=15,          label="Slope (%)")
                    feat_drain = gr.Slider(0, 5,    value=2.5, step=.1, label="Drainage Density")
                    feat_lin   = gr.Slider(0, 2,    value=.5, step=.01, label="Lineament Density")
                    feat_ndvi  = gr.Slider(-1, 1,   value=.4, step=.01, label="NDVI (Vegetation)")
                    feat_savi  = gr.Slider(-1, 1,   value=.3, step=.01, label="SAVI (Soil Adjusted)")
                    feat_rain  = gr.Number(value=800, label="Rainfall (mm)")
                    pred_btn   = gr.Button("🔍 Analyse Groundwater Potential", variant="primary", size="lg")

                with gr.Column(scale=1, elem_classes="card"):
                    gr.HTML("<div class='section-title'>📊 Prediction Results</div>")
                    result_txt  = gr.Textbox(label="Predicted Zone", interactive=False)
                    result_plot = gr.Plot(label="Zone Probability Distribution")

        # ── TAB 2: Geospatial Map ─────────────────────────────────────────
        with gr.TabItem("🗺️ Geospatial Map"):
            with gr.Column(elem_classes="card"):
                gr.HTML("<div class='section-title'>🛰️ ML Groundwater Potential Zones</div>")
                gr.Markdown("*Colour-coded ML zones across the Godavari basin. "
                             "⭐ markers = monitoring stations. "
                             "Labels show ML-predicted dominant groundwater class.*")
                map_plot = gr.Plot(label="Zoning Map")
                _html    = gr.HTML(visible=False)
                map_btn  = gr.Button("🔄 Refresh Map", variant="secondary")
            map_btn.click(fn=lambda s: generate_map(s), inputs=[tab1_station], outputs=[map_plot, _html])
            app.load(fn=lambda: generate_map(list(STATIONS.keys())[0]), inputs=[], outputs=[map_plot, _html])

        # ── TAB 3: Godavari Dashboard ─────────────────────────────────────
        with gr.TabItem("🌊 Godavari Dashboard"):
            with gr.Tabs(elem_classes="tab-nav"):

                with gr.TabItem("📍 Interactive Map"):
                    with gr.Column(elem_classes="card"):
                        gr.HTML("<div class='section-title'>🗺️ Live Station Map — Click Markers for Details</div>")
                        
                        folium_out = gr.HTML(
                            make_folium_map(list(STATIONS.keys())[0]) if HAS_FOLIUM
                            else "<p style='color:#ff6b6b'>Install: pip install folium</p>"
                        )

                with gr.TabItem("📊 Discharge Analysis"):
                    with gr.Column(elem_classes="card"):
                        gr.HTML("<div class='section-title'>⚡ Water Discharge by Station</div>")
                        
                        discharge_plot = gr.Plot(make_discharge_chart(list(STATIONS.keys())[0]))

                with gr.TabItem("💧 GW Parameters"):
                    with gr.Column(elem_classes="card"):
                        gr.HTML("<div class='section-title'>🔬 Groundwater Parameters</div>")
                        
                        gw_plot = gr.Plot(make_gw_chart(list(STATIONS.keys())[0]))

                with gr.TabItem("🔍 Station Details"):
                    with gr.Column(elem_classes="card"):
                        gr.HTML("<div class='section-title'>📍 Station Deep-Dive</div>")
                        
                        stn_sel = gr.Dropdown(choices=list(STATIONS.keys()),
                                              value=list(STATIONS.keys())[0],
                                              label="Select Station")
                        stn_out = gr.HTML(station_detail(list(STATIONS.keys())[0]))
                        stn_sel.change(fn=station_detail, inputs=stn_sel, outputs=stn_out)

                with gr.TabItem("📈 Summary Table"):
                    with gr.Column(elem_classes="card"):
                        gr.HTML("<div class='section-title'>📋 All Stations at a Glance</div>")
                        
                        summary_tbl = gr.Dataframe(make_summary_df(list(STATIONS.keys())[0]), interactive=False)

        # ── TAB 4: Model Accuracy ─────────────────────────────────────────
        with gr.TabItem("🎯 Model Accuracy"):
            with gr.Column(elem_classes="card"):
                gr.HTML("<div class='section-title'>🏆 Random Forest Model Performance</div>")
                accuracy_out = gr.HTML(get_accuracy_html())
                refresh_acc_btn = gr.Button("🔄 Refresh Accuracy", variant="secondary")
                refresh_acc_btn.click(fn=get_accuracy_html, inputs=[], outputs=[accuracy_out])

    # ── Wire Prediction Button to update ALL tabs ─────────────
    pred_btn.click(
        fn=predict_and_update_all,
        inputs=[feat_geo, feat_gm, feat_soil, feat_slope, feat_drain,
                feat_lin, feat_lulc, feat_ndvi, feat_savi, feat_rain, tab1_station],
        outputs=[result_txt, result_plot, map_plot, _html, folium_out, discharge_plot, gw_plot, stn_out, summary_tbl]
    )

    # ── Wire Tab 1 station dropdown → ALL other tab outputs ─────────────
    tab1_station.change(
        fn=update_all_tabs,
        inputs=[tab1_station],
        outputs=[map_plot, _html, folium_out, discharge_plot, gw_plot, stn_out, summary_tbl]
    )
    # Also sync station detail dropdown with Tab 1
    tab1_station.change(
        fn=lambda s: s,
        inputs=[tab1_station],
        outputs=[stn_sel]
    )

    gr.HTML("""
    <div class="gw-footer">
      <span>🌊 Groundwater ML · Godavari Basin · Powered by Random Forest & Gradio</span>
    </div>""")

# ─────────────────────────────────────────────
#  Vercel: mount Gradio inside FastAPI
#  (same pattern as admission chance predictor)
# ─────────────────────────────────────────────
fast_app = FastAPI(title="Groundwater ML — Godavari Basin")
app_vercel = gr.mount_gradio_app(fast_app, app, path="/")

if __name__ == "__main__":
    print("🚀 Launching Groundwater ML — Godavari Dark Edition …")
    app.queue()
    app.launch(server_name="0.0.0.0", server_port=7866, share=True, css=CSS)
