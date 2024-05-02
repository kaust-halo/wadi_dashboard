"""
Wadi ad-Dawasir INMA fields (2023 only for now)
"""
import streamlit as st
import leafmap.foliumap as leafmap
#from streamlit_gsheets import GSheetsConnection
#import geopandas as gpd
#from shapely import wkt

#sheet1_url = st.secrets["gsheets"]["geo"]
#conn = st.connection("gsheets", type=GSheetsConnection)
#gdata = conn.read(spreadsheet=sheet1_url).dropna()  # Different sheet than the weather one.
#gdata['geometry'] = gdata.geometry.apply(wkt.loads)
#gdf = gpd.GeoDataFrame(gdata)


markdown = """
Wadi ad-Dawasir field map (2023)
"""

st.sidebar.title("About")
st.sidebar.info(markdown)


st.title("2023 INMA fields map")

m = leafmap.Map(
    locate_control=True, latlon_control=True, draw_export=False, minimap_control=True
)
#m.add_gdf(gdf, layer_name="Fields")
m.to_streamlit(height=700)

