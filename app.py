import streamlit as st
import pandas as pd
import pydeck as pdk
import requests

'''
# TaxiFareModel front
'''

# Section to ask the user to select parameters for the ride
st.header("Ride Parameters")

# Ask for the date and time of the ride
ride_date = st.date_input('Select date of ride')
ride_time = st.time_input('Select time of ride')

# Ask for pickup and dropoff coordinates (longitude and latitude)
pickup_lon = st.number_input('Enter pickup longitude', value=-73.777271)
pickup_lat = st.number_input('Enter pickup latitude', value=40.643714)
dropoff_lon = st.number_input('Enter dropoff longitude', value=-73.965007)
dropoff_lat = st.number_input('Enter dropoff latitude', value=40.776621)

# Ask for the number of passengers
passenger_count = st.slider('Select number of passengers', min_value=1, max_value=6, value=1)

# Display the selected values
st.write('Ride Date:', ride_date)
st.write('Ride Time:', ride_time)
st.write('Pickup Coordinates:', (pickup_lat, pickup_lon))
st.write('Dropoff Coordinates:', (dropoff_lat, dropoff_lon))
st.write('Number of Passengers:', passenger_count)

# Prepare data for the API request
data = {
    'pickup_datetime': f"{ride_date} {ride_time}",  # format datetime properly
    'pickup_longitude': pickup_lon,
    'pickup_latitude': pickup_lat,
    'dropoff_longitude': dropoff_lon,
    'dropoff_latitude': dropoff_lat,
    'passenger_count': passenger_count
}

url = 'https://taxifare-30694630212.europe-west1.run.app/predict'

# Make the API call
response = requests.get(url, params=data)

# Check the response and display the result
if response.status_code == 200:
    prediction = response.json()  # Assuming the prediction comes as a JSON object
    fare = prediction.get('fare')  # Extracting the fare from the response

    # Display the prediction result
    if fare:
        st.success(f"The predicted fare for your ride is: ${fare:.2f}")
    else:
        st.warning("The API response did not contain a predicted fare.")
else:
    st.error("Failed to retrieve prediction. Please try again later.")

# Create a dataframe to show pickup and dropoff points
points_data = pd.DataFrame({
    'lat': [pickup_lat, dropoff_lat],
    'lon': [pickup_lon, dropoff_lon],
    'location': ['Pickup', 'Dropoff']
})

# Create a dataframe for text labels to display on the map
text_data = pd.DataFrame({
    'lat': [pickup_lat - 0.007, dropoff_lat - 0.007],
    'lon': [pickup_lon, dropoff_lon],
    'text': ['Pickup', 'Dropoff']
})

# Create a pydeck Layer to display markers (pickup and dropoff)
deck = pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=(pickup_lat + dropoff_lat) / 2,
        longitude=(pickup_lon + dropoff_lon) / 2,
        zoom=10
    ),
    layers=[
        # Add the markers for pickup and dropoff points
        pdk.Layer(
            'ScatterplotLayer',
            points_data,
            get_position='[lon, lat]',
            get_color='[255, 0, 0]',
            get_radius=100,
            pickable=True
        ),
        pdk.Layer(
            'TextLayer',
            text_data,
            get_position='[lon, lat]',
            get_text='text',
            get_size=13,
            get_color='[0, 250, 250]',
            get_angle=0,
            pickable=True
        )
    ]
)

# Display the map in Streamlit
st.subheader("Map Showing Pickup and Dropoff Locations")
st.pydeck_chart(deck)
