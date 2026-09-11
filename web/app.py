import os
from dotenv import load_dotenv
import streamlit as st
import requests

load_dotenv()

def handle_bool_inputs(answer: str) -> bool:
    return answer.strip().lower() == 'yes'

def approximent_rent(rent: float):
    return round(rent / 500) * 500

@st.cache_data()
def fetch_localities():
    response = requests.get(f'{os.getenv('API_URL')}/get-localities', timeout=5)
    response.raise_for_status()
    return sorted(response.json()['localities'])

st.set_page_config(page_title='Chennai PG Intelligence', layout='wide')
st.title('Chennai PG Intelligence')
st.caption('By Applying your preferences, it will gives the real approximation Rent price of the locality')

with st.container(border=True):
    st.subheader('Apply Preferences for Result')

    left_1, middle_1, right_1 = st.columns(3, vertical_alignment='bottom')
    left_2, middle_2, right_2 = st.columns(3, vertical_alignment='bottom')
    left_3, middle_3, right_3 = st.columns(3, vertical_alignment='bottom')

    locality = left_1.selectbox('Select the area you are looking for.', fetch_localities())
    gender = middle_1.selectbox('Choose Gender', ['Male', 'Female', 'Both'])
    occupancy = right_1.selectbox('Choose how many people will share the room', ['Single', 'Double', 'Three', 'Four'])
    
    available_for = left_2.selectbox('Select who the PG should be suitable for', ['Student', 'Working Professional', 'Anyone'])
    food_included = middle_2.selectbox('Choose whether you want food or mess included', ['Yes', 'No'])
    wifi = right_2.selectbox('Choose whether WiFi should be included', ['Yes', 'No'])

    laundry = left_3.selectbox('Choose whether laundry facilities are required', ['Yes', 'No'])
    room_ac = middle_3.selectbox('Choose whether you want an air conditioned room', ['Yes', 'No'])
    parking = right_3.selectbox('Select the parking option you need', ['Car', 'Bike', 'Bike and Car', 'No Parking'])

with st.container(border=True, horizontal_alignment='left'):
    if st.button('Fetch price in {locality}', width='stretch', ):
        data = {
            'locality': locality,
            'gender': gender.upper(),
            'occupancy': occupancy.title(),
            'available_for': available_for.title(),
            'food_included': handle_bool_inputs(food_included),
            'wifi': handle_bool_inputs(wifi),
            'laundry': handle_bool_inputs(laundry),
            'room_ac': handle_bool_inputs(room_ac),
            'parking': parking,
        }

        response = requests.post(f'{os.getenv('API_URL')}/prediction', json=data)
        if response.status_code == 200:
            result = response.json()
            st.subheader("Estimated Monthly Rent")
            st.success(f"₹{approximent_rent(result['predicted_rent'])} / month")
            st.write(f'Actutal Rent for {occupancy.lower()} sharing room in {locality} ranges from ₹{approximent_rent(result['lower'])} to ₹{approximent_rent(result['upper'])}')
        else:
            st.error("Prediction failed. Please try again.")