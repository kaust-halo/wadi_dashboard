"""
Wadi ad-Dawasir INMA fields (2023 only for now)
"""
import streamlit as st
import leafmap.foliumap as leafmap
from streamlit_gsheets import GSheetsConnection
import geopandas as gpd
from shapely import wkt
from folium.plugins import MiniMap


# Page configuration
st.set_page_config(
    page_title="Wadi ad-Dawasir INMA fields map",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded")

# Secrets
sheet1_url = st.secrets["gsheets"]["geo"]
xyz_layers = st.secrets["xyz"]

# Read the geospatial data (fields)
conn = st.connection("gsheets", type=GSheetsConnection)
gdata = conn.read(spreadsheet=sheet1_url).dropna()  
gdata['geometry'] = gdata.geometry.apply(wkt.loads)
gdf = gpd.GeoDataFrame(gdata)

# Quick area calculation in hectares:
gdf["Area"] = gdf.set_crs("EPSG:4326").to_crs("EPSG:32638").area*1e-4

# Total area per crop type:
total_area = gdf.groupby(["Crop"]).Area.sum()
crop_emoji={
    "Wheat": "🌾",
    "Potato": "🥔",
    "Watermelon": "🍉"
}
# Display in sidebar -- 
st.sidebar.title("Total area")
st.sidebar.metric("Total area", f"{total_area.sum():.0f} ha")
for x in total_area.items():
    st.sidebar.metric(f"{crop_emoji[x[0]]}{x[0]}", f"{x[1]:.0f} ha")


# Initial color
wheat_color =  "#FFC107"
potato_color = "#E66100"
watermelon_color = "#086608"

color_dict = {
    "Wheat": wheat_color,
    "Potato": potato_color,
    "Watermelon": watermelon_color
}


markdown = """
Wadi ad-Dawasir field map (2023)
"""

st.sidebar.title("About")
st.sidebar.info(markdown)


st.title("2023 INMA fields map")

m = leafmap.Map(
    locate_control=False, 
    search_control=False, 
    draw_export=False, 
    draw_control=False,
    minimap_control=False,
    measure_control=False,
    latlon_control=True,
)
MiniMap(zoom_level_offset=-9, position="bottomleft").add_to(m)

landsat_2023 = xyz_layers["landsat_2023"]
ndvi_2023 = xyz_layers["ndvi_2023"]
m.add_tile_layer(
    url=landsat_2023,
    name="2023 Landsat basemap",
    attribution="Landsat, KAUST-HALO",
    max_native_zoom=13,
    shown = False
)
m.add_tile_layer(
    url=ndvi_2023,
    name="2023 Max NDVI",
    attribution="Landsat, KAUST-HALO",
    max_native_zoom=13,
    shown = False
)

def style(feature):
    return {
        "fillColor": color_dict.get(feature["properties"]["Crop"],"#000000"),
        "color": "black",
        "fillOpacity": 1
    }

m.add_gdf(gdf, layer_name="Fields",
          style_function = style,
)

m.add_legend(title="Crop", legend_dict=color_dict, position="bottomright")

m.to_streamlit(height=700)

