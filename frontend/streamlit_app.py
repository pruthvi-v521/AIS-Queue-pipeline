import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from streamlit_option_menu import option_menu
from api_client import *
import pydeck as pdk
import folium
from streamlit_folium import st_folium


st.set_page_config(page_title="AIS Dashboard", layout="wide")

st.title(" Automatic Identification System Dashboard")

# ------------------------------
# API Health Check
# ------------------------------

st.subheader("System Status")

try:
    health = requests.get("http://127.0.0.1:8000/health").json()
    st.success(health["status"])
except:
    st.error("Backend API not running")


selected = option_menu(
        menu_title = None ,
        options = ["Vessels", "Live Vessel Map", "Vessel Trajectory", "Collision Alerts"] , 
        default_index = 0,
        orientation = "horizontal"
    )


if selected == "Vessels":
    st.header(" Static Vessels ")

    vessels = get_vessels()
    df = pd.DataFrame(vessels)

    st.dataframe(df)

if selected == "Live Vessel Map":
    st.header("Live Vessel Positions")

    vessels = get_latest_positions()

    df = pd.DataFrame(vessels)

    if not df.empty:
        # Center map in Europe or around your vessels
        center_lat = df["latitude"].mean()
        center_lon = df["longitude"].mean()
        vessel_map = folium.Map(location=[center_lat, center_lon], zoom_start=6)

        # Add markers for each vessel
        for _, vessel in df.iterrows():
            location = [vessel['latitude'], vessel['longitude']]
            tooltip = f"MMSI: {vessel['mmsi']}\nSpeed: {vessel['sog']}\nCourse: {vessel['cog']}"
            folium.Marker(location, tooltip=tooltip, icon=folium.Icon(icon='ship', prefix='fa')).add_to(vessel_map)

        # Render the folium map in Streamlit
        st_folium(vessel_map, width=1100, height=500)

    else:
        st.warning("No vessel data available")

    # if not df.empty:
    #     st.map(df[["latitude","longitude"]] , zoom = 7.5)
    # else:
    #     st.warning("No vessel data available")

# EUROPE_CENTER = (41.5025 - 72.699997)
# map = folium.Map(location = EUROPE_CENTER , zoom_start =9)

# for station in data:
#     location = station['latitude'] , station[longitude]
#     folium.Marker(location).add_to(map)
    
# st.folium(map , width = 700)

if selected== "Vessel Trajectory":

    st.header("Vessel Trajectory")


    mmsi = st.text_input("Enter MMSI")

    if mmsi:

        positions = get_positions_by_mmsi(mmsi)

        if positions:

            df = pd.DataFrame(positions)
           
            df = df[df["mmsi"] ==int(mmsi)]

            st.map(df[["latitude","longitude"]])

            st.subheader("Speed and Course")

            st.line_chart(df[["sog","cog"]])
            df = df.dropna(subset=["latitude","longitude"])

        else:
            st.warning("No trajectory found for this vessel")

if selected == "Collision Alerts":

    st.header("Collision Alerts")

    alerts = get_collision_alerts()

    df = pd.DataFrame(alerts)

    if not df.empty:

        st.dataframe(df)

        st.subheader("Alert Map")

        st.map(df[["latitude_a","longitude_a"]])

    else:
        st.success("No collision alerts detected")