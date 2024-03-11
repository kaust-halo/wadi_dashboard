"""
Wadi ad-Dawasir weather information

https://docs.streamlit.io/knowledge-base/tutorials/databases/private-gsheet

Dev/local run:
streamlit run --server.fileWatcherType=poll --server.port 8503 wadi_weather.py
"""
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
import datetime 

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Wadi ad-Dawasir weather data",
    page_icon="⛅",
    layout="wide",
    initial_sidebar_state="expanded")

# Read data
conn = st.connection("gsheets", type=GSheetsConnection)
wdata = conn.read(parse_dates=["date"],
               dayfirst=True)

# Sidebar input (year and colormap)
st.sidebar.title('⛅ Wadi ad-Dawasir weather data')

# Initial date range:
if 'cdate_range' not in st.session_state:
    st.session_state['cdate_range'] = [datetime.date(2019,6,1), 
                                       datetime.date(2019,6,30)]

cdate_range = st.session_state['cdate_range']

# Plots -- here with go instead of px
# because we want a simpler view
plot_temperature = go.Figure().update_layout(
    title=dict(text="🌡️ Temperature (°C)")
)
plot_temperature.add_trace(
    go.Bar(x=wdata.date, y=wdata.max_T, name="Hi",
           marker = {'color' : '#e65618'},
           hovertemplate="%{x}<br>%{y}")
)
plot_temperature.add_trace(
    go.Bar(x=wdata.date, y=wdata.min_T, name="Low",
           marker = {'color' : '#08b0c6'},
           hovertemplate="%{x}<br>%{y}")
)


plot_humidity = go.Figure().update_layout(
    title=dict(text="💦 Humidity (%)")
)
plot_humidity.add_trace(
    go.Bar(x=wdata.date, y=wdata.max_H, name="Hi",
           marker = {'color' : '#e65618'},
           hovertemplate="%{x}<br>%{y}")
)
plot_humidity.add_trace(
    go.Bar(x=wdata.date, y=wdata.min_H, name="Low",
           marker = {'color' : '#08b0c6'},
           hovertemplate="%{x}<br>%{y}")
)

plot_wind = go.Figure().update_layout(
    title=dict(text=("💨 Wind speed (km/h)"))
)
plot_wind.add_trace(
    go.Bar(x=wdata.date, y=wdata.max_U, name="Hi",
           marker = {'color' : '#e65618'},
           hovertemplate="%{x}<br>%{y}")
)
plot_wind.add_trace(
    go.Bar(x=wdata.date, y=wdata.mean_U, name="Avg",
           marker = {'color' : '#04570c'},
           hovertemplate="%{x}<br>%{y}")
)

plot_solar = go.Figure().update_layout(
    title=dict(text=("☀️ Daily accumulated solar radiation (W/m²)"))
)
plot_solar.add_trace(
    go.Bar(x=wdata.date, y=wdata.solar, name="Solar radiation",
           marker = {'color' : '#e65618'},
           hovertemplate="%{x}<br>%{y}")
)

plot_et = go.Figure().update_layout(
    title=dict(text=("💧 Evapotranspiration (mm/day)"))
)
plot_et.add_trace(
    go.Bar(x=wdata.date, y=wdata.ET, name="ET",
           marker = {'color' : '#189ee6'},
           hovertemplate="%{x}<br>%{y}")
)


selected_range_date = st.sidebar.date_input(
    "Plot view date range",
    (datetime.date(2018, 8, 1), datetime.date(2018,8,31)),
    datetime.date(2018, 8, 1),
    datetime.date(2019, 12, 27),
    key="date_range",
)

# update selection date range only when the date_input returns 
# TWO values, otherwise keep the copy from the session state. 
selected_range_date = st.session_state.date_range
if len(selected_range_date)==2:
    cdate_range = selected_range_date
    st.session_state.cdate_range = cdate_range


# Selected data
date_query = f"date>='{cdate_range[0]}' and date<='{cdate_range[1]}'"
selected_data = (wdata
                 .query(date_query)
                 .assign(
                     mean_T=lambda x: (x.max_T+x.min_T)/2,
                     mean_H=lambda x: (x.max_H+x.min_H)/2, 
                     )
)

# Summary data on selected data
s = selected_data.agg({
            "mean_T": "mean",
            "mean_H": "mean",
            "max_T": "max",
            "min_T": "min",
            "max_H": "max",
            "min_H": "min",
            "max_U": "max",
            "mean_U": "mean",
            "solar": "mean", 
            "ET": "mean"
    })
T = pd.DataFrame()


# +-1 day, otherwise 1 of the two bars is missing.  
pdate_range = [cdate_range[0]
               +datetime.timedelta(days=-1)
               , 
               cdate_range[1]
               +datetime.timedelta(days=1)
               ]
plot_temperature.update_layout(xaxis=dict(range=pdate_range, uirevision=True), uirevision=True)
plot_humidity.update_layout(xaxis=dict(range=pdate_range, uirevision=True), uirevision=True)
plot_wind.update_layout(xaxis=dict(range=pdate_range, uirevision=True), uirevision=True)
plot_solar.update_layout(xaxis=dict(range=pdate_range, uirevision=True), uirevision=True)
plot_et.update_layout(xaxis=dict(range=pdate_range, uirevision=True), uirevision=True)


# Main panel 
st.markdown("## Wadi ad-Dawasir weather data")
st.plotly_chart(plot_temperature, use_container_width=True)
st.plotly_chart(plot_humidity, use_container_width=True)
st.plotly_chart(plot_wind, use_container_width=True)
st.plotly_chart(plot_et, use_container_width=True)
st.plotly_chart(plot_solar, use_container_width=True)

with st.sidebar:
    st.markdown("## Summary")

    st.markdown("### 🌡️ Temperature")
    t1, t2, t3 = st.columns(3)
    t1.metric("High", f"{s.max_T:.1f} °C")
    t2.metric("Low", f"{s.min_T:.1f} °C")
    t3.metric("Average", f"{s.mean_T:.1f} °C")

    st.markdown("### 💦 Humidity")
    h1, h2, h3 = st.columns(3)
    h1.metric("High", f"{s.max_H:.0f} %")
    h2.metric("Low", f"{s.min_H:.0f} %")
    h3.metric("Average", f"{s.mean_H:.0f} %")

    st.markdown("### 💨 Wind speed")
    u1, u2  = st.columns(2)
    u1.metric("High", f"{s.max_U:.1f} km/h")
    u2.metric("Average", f"{s.mean_U:.1f} km/h")


    st.markdown("### 💧 ET")
    st.metric("Average", f"{s.ET:.1f} mm/day")


    st.expander('About', expanded=True).write('''
            - Weather data by [INMA agricultural company](https://inmanet.com.sa/en/home)
            - Select a view date range to update the plots view and summary.
            ''')

