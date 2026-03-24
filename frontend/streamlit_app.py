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

st.markdown("""
    <style>

    .stApp {
        background-color: #0A1628;
    }
    
    h1 {
        color: #00B4D8;
        font-weight: bold;
        padding-bottom: 10px;
        border-bottom: none;
        text-align: center
    }
    
    h2, h3 {
        color: #FFFFFF;
        text-align : center
    }
            
    .system-status {
    text-align: left ;
    color: #FFFFFF;  
    margin-bottom: 6px;
}
   
    [data-testid="stDataFrame"] {
        border: 1px solid #0D3B6E;
        border-radius: 8px;
    }
    .api-status {
    width: 100%;
    display: block;
    margin-top: -10px;
}
    </style>
""", unsafe_allow_html=True)

st.title(" Automatic Identification System Dashboard")

st.markdown(
    '<h3 class="system-status">System Status</h3>',
    unsafe_allow_html=True
)

try:
    health = requests.get("http://127.0.0.1:8000/health").json()
    st.markdown(
    f'<div class="api-status" style="background:#0D3B6E;border:1px solid #00B4D8;'
    f'border-radius:8px;padding:12px 20px;color:#00B4D8;font-weight:bold;">● {health["status"]}</div>',
    unsafe_allow_html=True
)
except:
    st.markdown(
    f'<div class="api-status" style="background:#0D3B6E;border:1px solid #00B4D8;'
    f'border-radius:8px;padding:12px 20px;color:#00B4D8;font-weight:bold;">● API not running</div>',
    unsafe_allow_html=True
)


selected = option_menu(
        menu_title = None ,
        options = ["Vessels", "Live Vessel Map", "Vessel Trajectory"] , 
        default_index = 0,
        orientation = "horizontal",

        styles={
        "container": {"width": "100%", "padding": "0" },
        # "background-color": "#0A1628"
        "nav-item": {"flex": "1"},
        "nav-link": {
            "text-align": "center",
            "width": "100%",
            "color": "#94A3B8",
            "background-color": "#0A1628",
            "border": "1px solid #0D3B6E",
            "border-radius": "5px",
            "padding": "10px"
        },
        "nav-link-selected": {
            "background-color": "#0D3B6E",
            "color": "#00B4D8",
            "font-weight": "bold"
        },
        
    }
    )


if selected == "Vessels":
    st.header(" Static Vessels ")

    vessels = get_vessels()
    df = pd.DataFrame(vessels)

    df["mmsi"] = df["mmsi"].astype(str)

    
    df["updated_at"] = pd.to_datetime(df["updated_at"], utc=True)
    df["updated_at"] = df["updated_at"].dt.strftime("%d %b %Y, %H:%M UTC")

    
    df["shipname"] = df["shipname"].fillna("Unknown Vessel")

    
    df = df[["mmsi", "shipname", "updated_at"]].rename(columns={
        "mmsi": "MMSI",
        "shipname": "Vessel Name",
        "updated_at": "Last Seen (UTC)"
    })

    st.dataframe(df, use_container_width=True)

if selected == "Live Vessel Map":
    st.header("Live Vessel Positions")

    positions = get_latest_positions()

    df= pd.DataFrame(positions)
    

    df = df.dropna(subset=["latitude", "longitude"])

    if not df.empty:
        # Center map in Europe or around your vessels
        center_lat = df["latitude"].mean()
        center_lon = df["longitude"].mean()
        vessel_map = folium.Map(location=[center_lat, center_lon], zoom_start=6)

        # Add markers for each vessel
        for _, vessel in df.iterrows():
            location = [vessel['latitude'], vessel['longitude']]

            tooltip = (
                f"MMSI: {vessel['mmsi']}\n " 
               f"Speed: {vessel['sog'] if pd.notna(vessel['sog']) else 'N/A'} kn\n"
                f"Course: {vessel['cog'] if pd.notna(vessel['cog']) else 'N/A'}°\n"
    
            )

            folium.Marker(
                location,
                tooltip=tooltip,
                icon=folium.Icon(icon="ship", prefix="fa")
            ).add_to(vessel_map)
            
        # Render the folium map in Streamlit
        st_folium(vessel_map, width=1600, height=600)

    else:
        st.warning("No vessel data available")


if selected== "Vessel Trajectory":

    st.header("Vessel Trajectory")


    mmsi = st.text_input("Enter MMSI")

    if mmsi:

        positions = get_positions_by_mmsi(mmsi)

        if positions:

            df = pd.DataFrame(positions)
           
            df = df[df["mmsi"] ==int(mmsi)]
            df = df.dropna(subset=["latitude", "longitude"])

            trajectory_map = folium.Map(
                location=[df["latitude"].mean(), df["longitude"].mean()],
                zoom_start=8
            )

            coordinates = list(zip(df["latitude"], df["longitude"]))
            folium.PolyLine(
                coordinates,
                color="blue",
                weight=3,
                opacity=0.8,
                tooltip=f"Trajectory for MMSI {mmsi}"
            ).add_to(trajectory_map)

            folium.Marker(
                coordinates[0],
                tooltip="Start",
                icon=folium.Icon(color="green", icon="play", prefix="fa")
            ).add_to(trajectory_map)

            folium.Marker(
                coordinates[-1],
                tooltip="End",
                icon=folium.Icon(color="red", icon="stop", prefix="fa")
            ).add_to(trajectory_map)

            st_folium(trajectory_map, width=1600, height=500)
            df = df.sort_values("ts")
            df["ts"] = pd.to_datetime(df["ts"], utc=True)   # ← add this

            start = df["ts"].min().strftime("%d %b %Y")
            end = df["ts"].max().strftime("%d %b %Y")

            duration = df["ts"].max() - df["ts"].min()
            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            st.subheader(f"Summary of the Voyage ")
            st.subheader(f"MMSI :{mmsi}  -  {start} to {end}")
            
            st.markdown("""
    <style>
    [data-testid="metric-container"] {
        background-color: #0D3B6E;
        border: 1px solid #00B4D8;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    [data-testid="stMetricLabel"] {
        color: #00B4D8;
        font-size: 14px;
        font-weight: bold;
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF;
        font-size: 28px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)
            
            # Replace the single background-color with individual column colors
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown('<div style="background:#0D3B6E;border:1px solid #00B4D8;border-radius:10px;padding:20px;text-align:center"><p style="color:#00B4D8;font-weight:bold;margin:0"> Total Positions</p><h2 style="color:white;margin:0">{}</h2></div>'.format(len(df)), unsafe_allow_html=True)

            with col2:
                st.markdown('<div style="background:#0D3B6E;border:1px solid #00B4D8;border-radius:10px;padding:20px;text-align:center"><p style="color:#00B4D8;font-weight:bold;margin:0">Avg Speed</p><h2 style="color:white;margin:0">{:.1f} kn</h2></div>'.format(df["sog"].mean()), unsafe_allow_html=True)

            with col3:
                st.markdown('<div style="background:#0D3B6E;border:1px solid #00B4D8;border-radius:10px;padding:20px;text-align:center"><p style="color:#00B4D8;font-weight:bold;margin:0">Max Speed</p><h2 style="color:white;margin:0">{:.1f} kn</h2></div>'.format(df["sog"].max()), unsafe_allow_html=True)

            with col4:
                st.markdown('<div style="background:#0D3B6E;border:1px solid #00B4D8;border-radius:10px;padding:20px;text-align:center"><p style="color:#00B4D8;font-weight:bold;margin:0"> Duration</p><h2 style="color:white;margin:0">{}h {}m</h2></div>'.format(hours, minutes), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

        else:
            st.warning("No trajectory found for this vessel")


            
