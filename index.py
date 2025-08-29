import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import math
import time
from datetime import datetime

# Title
st.set_page_config(page_title="Robot Monitoring System", layout="wide")

# Sidebar
st.sidebar.title("Control Panel")
st.sidebar.selectbox("Camera 1", ["Logitech C920", "Realsense RGB", "Depth Camera"])
st.sidebar.selectbox("Camera 2", ["Logitech C920", "Realsense RGB", "Depth Camera"])
st.sidebar.selectbox("Mode",     ["Manual", "Autonomous"])
if "system_active" not in st.session_state:
    st.session_state.system_active = False

# Toggle function
def toggle_system():
    st.session_state.system_active = not st.session_state.system_active

# Start/Stop button
if st.sidebar.button("Start" if not st.session_state.system_active else "Stop", on_click=toggle_system):
    pass

# Indicator status
if st.session_state.system_active:
    st.sidebar.markdown(
        "<span style='color: green; font-weight: 500;'>🟢 Active</span>", 
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        "<span style='color: red; font-weight: 500;'>🔴 Deactivate</span>", 
        unsafe_allow_html=True
    )

# Header
st.markdown(
    """
    <h1 style='text-align: center; color: #2E86C1;'>NEREUS NATHARA</h1>
    <p style='text-align: center; color: gray;'>BARELANG MARINE ROBOTIC TEAM | POLITEKNIK NEGERI BATAM</p>
    """,
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs(["Monitoring", "Vision", "Autonomous"]) # Set how many tab

######################
# TAB 1 | MONITORING #
######################
with tab1:
    with st.container():
        arena = st.radio("Select Arena:", ["Arena A", "Arena B"], horizontal=True) # Select arena

        col1, col2 = st.columns([2, 2]) # Set column size

        # Column for arena map
        with col1:

            # Coordinate function
            def coordinate(arena):
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.set_xlim(0, 2500)
                ax.set_ylim(0, 2500)
                ax.set_xticks(range(0, 2600, 500))
                ax.set_yticks(range(0, 2600, 500))
                ax.grid(True)

                # Decision function | Arena A
                if arena == "Arena A":
                    rectangle = plt.Rectangle((2100, 65), 170, 100, color='red', fill=True) # Dock
                    red_positions, green_positions = floating_ball_positions("Arena A")     # Ball

                    ax.add_patch(rectangle)
                    ax.add_patch(plt.Rectangle((520, 300), 100, 50, color='blue', fill=True))  # Fish
                    ax.add_patch(plt.Rectangle((300, 620), 100, 50, color='green', fill=True)) # Mangrove

                    for pos in red_positions:
                        ax.add_patch(plt.Circle(pos, 25, color='red', fill=True))
                    for pos in green_positions:
                        ax.add_patch(plt.Circle(pos, 25, color='green', fill=True))

                # Decision function | Arena B
                elif arena == "Arena B":
                    rectangle = plt.Rectangle((250, 65), 170, 100, color='green', fill=True) # Dock
                    red_positions, green_positions = floating_ball_positions("Arena B")      # Ball

                    ax.add_patch(rectangle)
                    ax.add_patch(plt.Rectangle((1880, 300), 100, 50, color='blue', fill=True))  # Fish
                    ax.add_patch(plt.Rectangle((2100, 620), 100, 50, color='green', fill=True)) # Mangrove

                    for pos in red_positions:
                        ax.add_patch(plt.Circle(pos, 25, color='red', fill=True))
                    for pos in green_positions:
                        ax.add_patch(plt.Circle(pos, 25, color='green', fill=True))

                return fig

            # Floating ball positions function
            def floating_ball_positions(arena):

                # Decision function | Arena A
                if arena == "Arena A":
                    green_positions = [(330, 960. ), (330, 1310 ), (450, 1715 ),               # Zone 3
                                       (1040, 2250), (1200, 2250), (1360, 2250), (1520, 2250), # Zone 2
                                       (2325, 1465), (2180, 1160), (2260, 855 )]               # Zone 1
                    
                    red_positions   = [(180, 960. ), (180, 1310 ), (300, 1715 ),               # Zone 3
                                       (1040, 2100), (1200, 2100), (1360, 2100), (1520, 2100), # Zone 2
                                       (2175, 1465), (2030, 1160), (2110, 855 )]               # Zone 1
                    
                # Decision function | Arena B
                elif arena == "Arena B":
                    red_positions   = [(390, 855  ), (470, 1160 ), (325, 1465 ),               # Zone 1
                                       (980, 2100 ), (1140, 2100), (1300, 2100), (1460, 2100), # Zone 2
                                       (2200, 1715), (2320, 1310), (2320, 960 )]               # Zone 3
                    
                    green_positions = [(240, 855. ), (320, 1160 ), (175, 1465 ),               # Zone 1
                                       (980, 2250 ), (1140, 2250), (1300, 2250), (1460, 2250), # Zone 2
                                       (2050, 1715), (2170, 1310), (2170, 960 )]               # Zone 3
                    
                return red_positions, green_positions

            # Call function
            fig = coordinate(arena)
            st.pyplot(fig, width='stretch')

        # Column for information
        with col2:
            st.subheader("Monitoring Info")

            subcol1, subcol2 = st.columns(2) # Set sub-column size

            # Info
            with subcol1:
                day_placeholder      = st.empty() # Day
                date_placeholder     = st.empty() # Date
                time_placeholder     = st.empty() # Time
                position_placeholder = st.empty() # Position
            
            # Info
            with subcol2:
                sog_knot_placeholder   = st.empty() # SOG (Knot)
                sog_kmh_placeholder    = st.empty() # SOG (Km/h)
                coordinate_placeholder = st.empty() # Coordinate
                cog_placeholder        = st.empty() # COG

            # Data dummy
            now = datetime.now()
            current_day  = now.strftime("%A")       # Example: Thursday
            current_date = now.strftime("%d-%m-%Y") # Example: 28-08-2025
            current_time = now.strftime("%H:%M:%S") # Example: 12:31:28
        
            x = np.random.randint(0, 100) # Data for x position
            y = np.random.randint(0, 100) # Data for y position
            
            latitude  = np.random.randint(0, 100) # Data for latitude
            lat       = latitude
            longitude = np.random.randint(0, 100) # Data for longitude
            long      = longitude

            sog_knot = np.random.randint(0, 100) # Data for SOG (Knot)
            sog_kmh  = np.random.randint(0, 100) # Data for SOG (Km/h)
            cog      = np.random.randint(0, 100) # Data for COG

            # Format data
            day_placeholder.metric      ("Day", current_day)             # Day      
            date_placeholder.metric     ("Date", current_date)           # Date
            time_placeholder.metric     ("Time", current_time)           # Time
            position_placeholder.metric ("Position [X, Y]", f"{x}, {y}") # Position

            coordinate_placeholder.metric ("Coordinate [Lat, Long]", f"{lat}, {long}") # Coordinate
            sog_knot_placeholder.metric   ("SOG [Knot]", f"{sog_knot:.2f} kn")         # SOG (Knot)
            sog_kmh_placeholder.metric    ("SOG [Km/h]", f"{sog_kmh:.2f} km/h")        # SOG (Km/h)
            cog_placeholder.metric        ("COG", f"{cog:.1f} °")                      # COG

    with st.container():
        col1, col2 = st.columns([1,1]) # Set column size
        
        # Mangrove pic
        with col1:
            st.subheader("Mangrove picture")
            mangrove_pic_placeholder = st.empty()

        # Fish pic
        with col2:
            st.subheader("Fish picture")
            fish_pic_placeholder = st.empty()
        
        # Picture simulation
        img = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mangrove_pic_placeholder.image (img, channels="RGB", width='stretch')
        fish_pic_placeholder.image     (img, channels="RGB", width='stretch')

##################
# TAB 2 | VISION #
##################
with tab2:
    # Vision display
    with st.container():
        col1, col2 = st.columns([1, 1])

        # Display
        with col1:
            st.subheader("Surface Camera")
            cam_surface_placeholder = st.empty()
        # Display
        with col2:
            st.subheader("Underwater Camera")
            cam_underwater_placeholder = st.empty()

    # Vision information
    with st.container():
        col1, col2 = st.columns([1, 1]) # Set column size

        with col1:
            st.subheader("Surface Vision Info")

            subcol1, subcol2 = st.columns(2) # Set sub-column size

            # Info
            with subcol1:
                greenball_placeholder       = st.empty() # Green Ball Conf
                redball_placeholder         = st.empty() # Red Ball Conf
                mangrove_placeholder        = st.empty() # Mangrove Conf
                avgconf_surface_placeholder = st.empty() # Average Conf

            # Info
            with subcol2:
                greendist_placeholder    = st.empty() # Green Ball Dist
                reddist_placeholder      = st.empty() # Red Ball Dist
                mangrovedist_placeholder = st.empty() # Mangrove Dist
                fps_surface_placeholder  = st.empty() # FPS

        with col2:
            st.subheader("Underwater Vision Info")

            subcol1, subcol2 = st.columns(2) # Set sub-column size

            # Info
            with subcol1:
                fish_placeholder               = st.empty() # Fish Conf
                avgconf_underwater_placeholder = st.empty() # Average conf

            # Info
            with subcol2:
                fishdist_placeholder       = st.empty() # Fish Distance
                fps_underwater_placeholder = st.empty() # FPS

    start_time = time.time()

    # Camera simulation
    img = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cam_surface_placeholder.image    (img, channels="RGB", width='stretch')
    cam_underwater_placeholder.image (img, channels="RGB", width='stretch')

    # Data dummy
    dist_class1 = np.random.uniform(0.1, 5.0) # Dist class 1
    dist_class2 = np.random.uniform(0.1, 5.0) # Dist class 2
    dist_class3 = np.random.uniform(0.1, 5.0) # Dist class 3
    dist_class4 = np.random.uniform(0.1, 5.0) # Dist class 4

    conf_class1 = np.random.uniform(0.1, 1.0) # Conf class 1
    conf_class2 = np.random.uniform(0.1, 1.0) # Conf class 2
    conf_class3 = np.random.uniform(0.1, 1.0) # Conf class 3
    conf_class4 = np.random.uniform(0.1, 1.0) # Conf class 4

    fps = round(1.0 / (time.time() - start_time), 1) # FPS Calculation
    start_time = time.time()

    avg_conf = np.random.uniform(0.1, 1.0) # Average conf

    # Format data
    fps_surface_placeholder.metric     ("FPS", f"{fps}")               # FPS surface camera
    avgconf_surface_placeholder.metric ("Avg Conf", f"{avg_conf:.2f}") # Avg conf surface camera

    fps_underwater_placeholder.metric     ("FPS", f"{fps}")               # FPS underwater camera
    avgconf_underwater_placeholder.metric ("Avg Conf", f"{avg_conf:.2f}") # Avg conf underwater camera

    greenball_placeholder.metric ("Green Ball Conf", f"{conf_class1:.2f}") # Green ball conf
    redball_placeholder.metric   ("Red Ball Conf", f"{conf_class2:.2f}")   # Red ball conf
    mangrove_placeholder.metric  ("Mangrove Conf", f"{conf_class3:.2f}")   # Mangrove conf
    fish_placeholder.metric      ("Fish Conf", f"{conf_class4:.2f}")       # Fish conf

    greendist_placeholder.metric    ("Green Ball Dist", f"{dist_class1:.2f} m") # Green ball dist
    reddist_placeholder.metric      ("Red Ball Dist", f"{dist_class2:.2f} m")   # Red ball dist
    mangrovedist_placeholder.metric ("Mangrove Dist", f"{dist_class3:.2f} m")   # Mangrove dist
    fishdist_placeholder.metric     ("Fish Dist", f"{dist_class4:.2f} m")       # Fish dist

######################
# TAB 3 | AUTONOMOUS #
######################
with tab3:
    with st.container():
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Camera")
            zone_placeholder = st.empty()
            cam_auto_placeholder = st.empty()

            # Camera simulation
            img = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cam_auto_placeholder.image(img, channels="RGB", width='stretch')

        with col2:
            st.subheader("Navigation")

            subcol1, subcol2, subcol3 = st.columns(3)

            with subcol1:
                left_thruster_placeholder = st.empty()
                left_servo_placeholder    = st.empty()
                redball_auto_placeholder  = st.empty()
                angular_placeholder       = st.empty()

            with subcol2:
                bow_thruster_placeholder  = st.empty()
                command_placeholder       = st.empty()

            with subcol3:
                right_thruster_placeholder = st.empty()
                right_servo_placeholder    = st.empty()
                greenball_auto_placeholder = st.empty()
                linear_placeholder         = st.empty()

            angular_value        = np.random.uniform(0, 100)
            linear_value         = np.random.uniform(0, 100)

            left_thruster_value  = np.random.uniform(0, 100)
            bow_thruster_value   = np.random.uniform(0, 100)
            right_thruster_value = np.random.uniform(0, 100)

            left_servo_value     = np.random.uniform(0, 100)
            right_servo_value    = np.random.uniform(0, 100)

            commands             = ["Maju", "Kanan", "Kiri", "Berputar", "Berhenti"]
            command_value        = np.random.choice(commands)

            greenball            = ["True", "False"]
            greenball_value      = np.random.choice(greenball)

            redball              = ["True", "False"]
            redball_value        = np.random.choice(redball )

            st.markdown(
                """
                <style>
                /* Ubah semua label metric */
                div[data-testid="stMetricLabel"] {
                    font-size: 14px !important;
                    color: red !important;
                }

                /* Ubah semua value metric */
                div[data-testid="stMetricValue"] {
                    font-size: clamp(12px, 2vw, 18px); !important;
                    color: red !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            angular_placeholder.metric        ("Angular", f"{angular_value:.0f}")
            linear_placeholder.metric         ("Linear", f"{linear_value:.0f}")

            left_thruster_placeholder.metric  ("Left thruster", f"{left_thruster_value:.0f} Km/h")
            bow_thruster_placeholder.metric   ("Bow thruster", f"{bow_thruster_value:.0f} Km/h")
            right_thruster_placeholder.metric ("Right thruster", f"{right_thruster_value:.0f} Km/h")

            left_servo_placeholder.metric     ("Left servo", f"{left_servo_value:.0f} °")
            right_servo_placeholder.metric    ("Right servo", f"{right_servo_value:.0f} °")

            command_placeholder.metric        ("Command", command_value)

            greenball_auto_placeholder.metric ("Greenball", greenball_value)
            redball_auto_placeholder.metric   ("Redball", redball_value)

    with st.container():
        col1, col2 = st.columns([1,1])
        
        with col1:
            st.subheader("Sensor")

            subcol1, subcol2 = st.columns(2)

            with subcol1:
                gps_placeholder = st.empty()
                imu_placeholder = st.empty()

            with subcol2:
                etc_placeholder = st.empty()

            x         = np.random.uniform(0, 100)
            y         = np.random.uniform(0, 100)
            imu_value = np.random.uniform(0, 360)
            etc_value = np.random.uniform(0, 100)

            gps_placeholder.metric ("GPS [X, Y]", f"{x:.0f}, {y:.0f}")
            imu_placeholder.metric ("IMU", f"{imu_value:.1f} °")
            etc_placeholder.metric ("ETC", f"{etc_value:.0f}")

        with col2:
            st.subheader("Hardware Condition")

            subcol1, subcol2 = st.columns(2)

            with subcol1:
                battery1_placeholder = st.empty()
                battery2_placeholder = st.empty()
                battery3_placeholder = st.empty()

            with subcol2:
                battery4_placeholder = st.empty()
                battery5_placeholder = st.empty()

            percentage_battery1 = np.random.uniform(0, 100)
            percentage_battery2 = np.random.uniform(0, 100)
            percentage_battery3 = np.random.uniform(0, 100)
            percentage_battery4 = np.random.uniform(0, 100)
            percentage_battery5 = np.random.uniform(0, 100)

            battery1_placeholder.metric ("Battery 1 - Bow Thruster", f"{percentage_battery1:.1f} %")
            battery2_placeholder.metric ("Battery 2 - Right Thruster", f"{percentage_battery2:.1f} %")
            battery3_placeholder.metric ("Battery 3 - Left Thruster", f"{percentage_battery3:.1f} %")
            battery4_placeholder.metric ("Battery 4 - PC", f"{percentage_battery4:.1f} %")
            battery5_placeholder.metric ("Battery 5 - Microcontroller", f"{percentage_battery5:.1f} %")