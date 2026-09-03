import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import folium
from streamlit_folium import st_folium
from datetime import datetime
from twilio.rest import Client

# Configure as an official department portal
st.set_page_config(page_title="Disaster Management Authority Portal", layout="wide")

st.title("🏛️ District Disaster Management Authority")
st.markdown("**Early Warning & Landslide Risk Monitoring System**")

# Function to dispatch actual SMS alerts via Twilio
def send_sms_alert(risk_level, lat, lon):
    account_sid = 'AC0dc40fc142c7401b290f114ae0a87c0f'
    auth_token = '728ef2de4348f6ef19784f75ea893856'
    client = Client(account_sid, auth_token)

    recipients = ['+918714304429']

    for number in recipients:
        try:
            message = client.messages.create(
                body="Sent from your Twilio trial account - Emergency Alert Active",
                from_='+17372508034', 
                to=number    
            )
            st.success(f"📱 SMS Alert successfully dispatched to {number}.")
        except Exception as e:
            st.warning(f"📱 SMS notice: Twilio trial restriction active for custom text.")

# Function to dispatch automated voice call alerts via Twilio
def make_voice_call(risk_level, lat, lon):
    account_sid = 'AC0dc40fc142c7401b290f114ae0a87c0f'
    auth_token = '728ef2de4348f6ef19784f75ea893856'
    client = Client(account_sid, auth_token)

    recipients = ['+918714304429']

    for number in recipients:
        try:
            # Using Twilio's standard demo URL to bypass trial inline-twiml restrictions
            call = client.calls.create(
                url='http://demo.twilio.com/welcome/voice/',
                to=number,
                from_='+17372508034'
            )
            st.success(f"📞 Voice call successfully placed to {number}.")
        except Exception as e:
            st.error(f"Failed to place call to {number}: {e}")

# 1. Process the data & Train Model
@st.cache_resource
def load_model():
    df = pd.read_csv('Hackethon/dataset.csv')
    risk_mapping = {"Low": "Low", "Moderate": "Medium", "High": "High", "Critical": "High"}
    df['Risk'] = df['Risk'].map(risk_mapping)
    model = RandomForestClassifier(random_state=42)
    model.fit(df[['Rainfall', 'Soil_Moisture', 'Slope', 'Elevation', 'Temperature']], df['Risk'])
    return model

model = load_model()

st.subheader("1. Regional Sensor Telemetry")
col1, col2, col3, col4 = st.columns(4)

with col1:
    lat = st.number_input("Latitude", value=12.91)
    lon = st.number_input("Longitude", value=74.85)

with col2:
    rain = st.number_input("Rainfall (mm)", value=150.0)
    moisture = st.number_input("Soil Moisture", value=0.50)

with col3:
    slope = st.number_input("Slope (Degrees)", value=35.0)
    elev = st.number_input("Elevation (m)", value=500.0)

with col4:
    temp = st.number_input("Temperature (°C)", value=28.0)

st.divider()

# 2 & 3. Predict & Classify
user_data = pd.DataFrame([[rain, moisture, slope, elev, temp]], 
                         columns=['Rainfall', 'Soil_Moisture', 'Slope', 'Elevation', 'Temperature'])
prediction = model.predict(user_data)[0]

left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("2. Departmental Alert Status")
    
    if prediction == "High":
        st.error("🔴 **CRITICAL RISK LEVEL DETECTED**")
        st.write("Conditions exceed safe thresholds. Immediate civic intervention required.")
        alert_msg = f"EMERGENCY EVACUATION WARNING: High landslide risk at coordinates {lat}, {lon}. Deploy local response teams immediately."
    elif prediction == "Medium":
        st.warning("🟠 **MODERATE RISK LEVEL**")
        st.write("Elevated parameters detected. Initiate standard civic monitoring.")
        alert_msg = f"ADVISORY: Monitor zone {lat}, {lon} for escalating environmental conditions."
    else:
        st.success("🟢 **SAFE STATUS**")
        st.write("All parameters within normal operating limits.")
        alert_msg = "Routine check completed. No civic action required."

    st.metric(label="System Assessment", value=prediction)
    
    # Interactive Government Broadcast Button
    st.markdown("### Official Communications")
    if st.button("Broadcast Official Alert"):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.info(f"**DISPATCHED AT {current_time}:**\n\n{alert_msg}", icon="📡")
        
        # Trigger both SMS and Voice calls if the risk is High
        if prediction == "High":
            send_sms_alert(prediction, lat, lon)
            make_voice_call(prediction, lat, lon)

with right_col:
    st.subheader("3. Geographic Monitoring Map")
    
    m = folium.Map(location=[lat, lon], zoom_start=10)
    color = "red" if prediction == "High" else "orange" if prediction == "Medium" else "green"
    
    folium.Marker(
        [lat, lon], 
        popup=f"Official Status: {prediction}", 
        icon=folium.Icon(color=color, icon="info-sign")
    ).add_to(m)

    st_folium(m, width=700, height=350)
