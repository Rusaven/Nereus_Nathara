import streamlit as st
import numpy as np
import cv2
import random
import time
import os
from datetime import datetime
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
import requests

# Config for auto refresh
st.set_page_config(page_title="Robot Monitoring System", layout="wide")
st_autorefresh(interval=1000, key="datarefresh")

# Style
st.markdown("""
<style>
div[data-testid="stMetricValue"] {
    font-size: clamp(16px, 6vw, 22px) !important;
    color: #2E86C1 !important;
}
</style>
""", unsafe_allow_html=True)


###########################
# Back4App Connection
###########################
BASE_URL    = "https://parseapi.back4app.com/classes/NereusNathara"
headers     = {
        "X-Parse-Application-Id"    :'G8ywQkYC82dwuwSPpUWUo4Q7cVWbCOZhlyLTflgN',
        "X-Parse-REST-API-Key"      :'b6Xm6nc3J7qjaNLzjoUvIovvOqjTkSbmtray1t6R',
    }

def backend_data():
    response = requests.get(BASE_URL, headers=headers, params={"order": "-createdAt", "limit": 1})
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        st.error(f"Failed: {response.status_code}")
        return []

###########################
# Dummy Data Generator
###########################
def data_monitoring():
    now = datetime.now()
    return {
        "Day"        : now.strftime("%A"),
        "Date"       : now.strftime("%d-%m-%Y"),
        "Time"       : now.strftime("%H:%M:%S"),
        "Position_X" : random.uniform(0, 2500),
        "Position_Y" : random.uniform(0, 2500),
        "Latitude"   : random.uniform(-90, 90),
        "Longitude"  : random.uniform(-180, 180),
        "SOG_knot"   : random.uniform(0, 100),
        "SOG_kmh"    : random.uniform(0, 200),
        "COG"        : random.uniform(0, 360),

        "Yaw"        : random.uniform(0, 360),
        "Etc"        : random.uniform(0, 1000),
        "Battery1"        : random.uniform(0, 100),
        "Battery2"        : random.uniform(0, 100),
        "Battery3"        : random.uniform(0, 100),
        "Battery4"        : random.uniform(0, 100),
        "Battery5"        : random.uniform(0, 100),
    }

def data_vision():
    return {
        "Greenball_conf"     : random.uniform(0, 0.99),
        "Redball_conf"       : random.uniform(0, 0.99),
        "Mangrove_conf"      : random.uniform(0, 0.99),
        "Fish_conf"          : random.uniform(0, 0.99),

        "Greenball_dist"     : random.uniform(0.2, 5.0),
        "Redball_dist"       : random.uniform(0.2, 5.0),
        "Mangrove_dist"      : random.uniform(0.2, 5.0),
    }

def data_autonomous():
    return {
        "Left_thruster"  : random.uniform(0, 2500),
        "Right_thruster" : random.uniform(0, 2500),
        "Bow_thruster"   : random.uniform(0, 2500),
        "Left_servo"     : random.uniform(-90, 90),
        "Right_servo"    : random.uniform(-90, 90),
        "Angular"        : random.uniform(0, 100),
        "Linear"         : random.uniform(0, 100),
        "Command"        : random.choice(["Kiri", "Maju", "Kanan"]),
        "Zone"           : random.choice(["I", "II", "III"]),
    }

###########################
# Floating Ball + Arena
###########################
def floating_ball_positions(arena):
    if arena == "Arena A":
        green_positions = [(330, 960  ), (330, 1310 ), (450, 1715 ),
                           (1040, 2250), (1200, 2250), (1360, 2250), (1520, 2250),
                           (2325, 1465), (2180, 1160), (2260, 855 )]
        
        red_positions   = [(180, 960  ), (180, 1310 ), (300, 1715 ),
                           (1040, 2100), (1200, 2100), (1360, 2100), (1520, 2100),
                           (2175, 1465), (2030, 1160), (2110, 855 )]
    else:
        red_positions   = [(390, 855  ), (470, 1160 ), (325, 1465 ),
                           (980, 2100 ), (1140, 2100), (1300, 2100), (1460, 2100),
                           (2200, 1715), (2320, 1310), (2320, 960 )]
        
        green_positions = [(240, 855  ), (320, 1160 ), (175, 1465 ),
                           (980, 2250 ), (1140, 2250), (1300, 2250), (1460, 2250),
                           (2050, 1715), (2170, 1310), (2170, 960 )]
        
    return red_positions, green_positions

def build_static_map(arena):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, 2500)
    ax.set_ylim(0, 2500)
    ax.grid(True)

    if arena == "Arena A":
        ax.add_patch(plt.Rectangle((2100, 65) , 170, 100, color='red'  ))
        ax.add_patch(plt.Rectangle((520 , 300), 100, 50 , color='blue' ))
        ax.add_patch(plt.Rectangle((300 , 620), 100, 50 , color='green'))
    else:
        ax.add_patch(plt.Rectangle((250 , 65) , 170, 100, color='green'))
        ax.add_patch(plt.Rectangle((1880, 300), 100, 50 , color='blue' ))
        ax.add_patch(plt.Rectangle((2100, 620), 100, 50 , color='green'))

    red_positions, green_positions = floating_ball_positions(arena)
    for pos in red_positions:
        ax.add_patch(plt.Circle(pos, 25, color='red'))
    for pos in green_positions:
        ax.add_patch(plt.Circle(pos, 25, color='green'))

    trajectory_line, = ax.plot([], [], color='black', linestyle='--', marker='o', markersize=3)
    return fig, ax, trajectory_line

###########################
# Header
###########################
st.markdown(
    """
    <h1 style='text-align: center; color: #2E86C1;'>NEREUS NATHARA</h1>
    <p style='text-align: center; color: gray;'>BARELANG MARINE ROBOTIC TEAM | POLITEKNIK NEGERI BATAM</p>
    """,
    unsafe_allow_html=True
)

###########################
# Layout
###########################
main_col1, main_col2 = st.columns([2, 2])

# === LEFT SIDE ===
with main_col1:
    # Arena
    st.subheader("Arena")
    arena = st.radio("Select Arena:", ["Arena A", "Arena B"], horizontal=True)

    if ("map_fig" not in st.session_state) or (st.session_state.get("arena_name") != arena):
        fig, ax, trajectory_line = build_static_map(arena)
        st.session_state.map_fig = fig
        st.session_state.map_ax = ax
        st.session_state.trajectory_line = trajectory_line
        st.session_state.trajectory_x = []
        st.session_state.trajectory_y = []
        st.session_state.arena_name = arena

    monitoring = data_monitoring()
    x, y = monitoring["Position_X"], monitoring["Position_Y"]
    st.session_state.trajectory_x.append(x)
    st.session_state.trajectory_y.append(y)
    st.session_state.trajectory_line.set_data(st.session_state.trajectory_x, st.session_state.trajectory_y)

    st.pyplot(st.session_state.map_fig, clear_figure=False)

    # Cameras
    st.subheader("Live Cameras")
    col1, col2 = st.columns(2)
    dummy_img = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
    with col1:
        st.image(dummy_img, channels="RGB", caption="Surface Cam", width="stretch")
    with col2:
        st.image(dummy_img, channels="RGB", caption="Underwater Cam", width="stretch")

    # Pictures
    st.subheader("Pictures")
    col1, col2 = st.columns(2)

    surface_path = os.path.join(os.path.dirname(__file__), "Mangrove.jpg")
    underwater_path = os.path.join(os.path.dirname(__file__), "Fish.jpg")

    surface_img = cv2.imread(surface_path)
    underwater_img = cv2.imread(underwater_path)

    if surface_img is not None:
        surface_img = cv2.cvtColor(surface_img, cv2.COLOR_BGR2RGB)
        with col1:
            st.image(surface_img, channels="RGB", caption="Surface Cam", width="stretch")
    else:
        with col1:
            st.error("Surface image not found")

    if underwater_img is not None:
        underwater_img = cv2.cvtColor(underwater_img, cv2.COLOR_BGR2RGB)
        with col2:
            st.image(underwater_img, channels="RGB", caption="Underwater Cam", width="stretch")
    else:
        with col2:
            st.error("Underwater image not found")

# === RIGHT SIDE ===
with main_col2:
    st.subheader("System Info")
    monitoring = data_monitoring()
    vision     = data_vision()
    autonomous = data_autonomous()

    # Monitoring
    with st.expander("Monitoring"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Day"     , monitoring["Day"])
            st.metric("Date"    , monitoring["Date"])
            st.metric("Time"    , monitoring["Time"])
            st.metric("Position [x, y]", f"{monitoring['Position_X']:.0f}, {monitoring['Position_Y']:.0f}")
        with col2:
            st.metric("Lat/Long", f"{monitoring['Latitude'  ]:.2f}, {monitoring['Longitude']:.2f}")
            st.metric("SOG Knot", f"{monitoring['SOG_knot'  ]:.1f} kn")
            st.metric("SOG Km/h", f"{monitoring['SOG_kmh'   ]:.1f} km/h")
            st.metric("COG"     , f"{monitoring['COG'       ]:.1f} °")

    # Vision
    with st.expander("Vision"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Green Ball Conf", f"{vision['Greenball_conf']:.2f}")
            st.metric("Red Ball Conf"  , f"{vision['Redball_conf'  ]:.2f}")
            st.metric("Mangrove Conf"  , f"{vision['Mangrove_conf' ]:.2f}")
            st.metric("Fish Conf"      , f"{vision['Fish_conf'     ]:.2f}")
        with col2:
            st.metric("Green Ball Dist", f"{vision['Greenball_dist']:.2f} m")
            st.metric("Red Ball Dist"  , f"{vision['Redball_dist'  ]:.2f} m")
            st.metric("Mangrove Dist"  , f"{vision['Mangrove_dist' ]:.2f} m")

    # Autonomous
    with st.expander("Autonomous"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Left Thruster"  , f"{autonomous['Left_thruster' ]:.0f} RPM")
            st.metric("Left Servo"     , f"{autonomous['Left_servo'    ]:.0f} °")
        with col2:
            st.metric("Bow Thruster"   , f"{autonomous['Bow_thruster'  ]:.0f} RPM")
            st.metric("Zone"           , autonomous["Zone"])
            st.metric("Command"        , autonomous["Command"])
        with col3:
            st.metric("Right Thruster" , f"{autonomous['Right_thruster']:.0f} RPM")
            st.metric("Right Servo"    , f"{autonomous['Right_servo'   ]:.0f} °")

    # Localization
    with st.expander("Localization"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("GPS [x, y]", f"{monitoring['Position_X']:.0f}, {monitoring['Position_Y']:.0f}")
        with col2:
            st.metric("Yaw"       , f"{monitoring['Yaw']:.1f} °")
        with col3:
            st.metric("ETC"       , f"{monitoring['Etc']:.1f}")

    # Hardware
    with st.expander("Hardware"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Battery 1", f"{monitoring['Battery1']:.1f} %")    
            st.metric("Battery 2", f"{monitoring['Battery2']:.1f} %")
        with col2:
            st.metric("Battery 3", f"{monitoring['Battery3']:.1f} %")    
            st.metric("Battery 4", f"{monitoring['Battery4']:.1f} %")
        with col3:
            st.metric("Battery 5", f"{monitoring['Battery5']:.1f} %")    
