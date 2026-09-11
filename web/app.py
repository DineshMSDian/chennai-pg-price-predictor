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

st.set_page_config(page_title='Chennai PG Intelligence', layout='wide', page_icon='🌴')

# ---------------------------------------------------------------------------
# Visual layer only — no changes to app logic below this point.
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bungee&family=Teko:wght@500;600&family=Rajdhani:wght@500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Rajdhani', sans-serif;
    }

    /* Full-page sunset gradient, top (dusk) to bottom (horizon) */
    .stApp {
        background: linear-gradient(
            180deg,
            #241245 0%,
            #3d1c66 10%,
            #6c2e86 24%,
            #a2469a 38%,
            #d0619a 50%,
            #ee7f83 62%,
            #f59f68 75%,
            #f7b769 88%,
            #f8c46f 100%
        );
        background-attachment: fixed;
    }

    /* Palm silhouettes, fixed to viewport edges */
    #palm-overlay {
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        pointer-events: none;
        z-index: 0;
        opacity: 0.65;
    }

    /* Push actual app content above the palm overlay */
    .stApp > header, section.main {
        position: relative;
        z-index: 1;
    }

    /* ---------------- Hero (transparent, sky shows through) ---------------- */

    /* ---------------- Contact links ---------------- */
    .vc-contact {
        position: absolute;
        top: 1.2rem;
        left: 1.5rem;
        z-index: 10;
        display: flex;
        gap: 1rem;
    }

    .vc-contact a {
        color: #fff3e6;
        text-decoration: none;
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-shadow: 0 2px 6px rgba(30, 10, 45, 0.5);
        transition: all 0.2s ease;
    }

    .vc-contact a:hover {
        color: #ffcf9f;
        transform: translateY(-1px);
    }
    .vc-hero {
        position: relative;
        z-index: 2;
        padding: 3.2rem 1rem 2.4rem 1rem;
        margin-bottom: 1.6rem;
        text-align: center;
    }
    .vc-eyebrow {
        font-family: 'Teko', sans-serif;
        font-weight: 600;
        letter-spacing: 6px;
        font-size: 1.05rem;
        color: #fff3e0;
        text-shadow: 0 2px 6px rgba(30,10,45,0.6);
        margin-bottom: 0.6rem;
    }
    .vc-title {
        font-family: 'Bungee', sans-serif;
        font-size: 4rem;
        line-height: 1.05;
        margin: 0;
        color: #fff8ec;
        -webkit-text-stroke: 2px #2a1140;
        text-shadow:
            3px 3px 0 #2a1140,
            -2px -2px 0 #2a1140,
            2px -2px 0 #2a1140,
            -2px 2px 0 #2a1140,
            0 10px 24px rgba(20, 5, 30, 0.55);
        letter-spacing: 1px;
    }
    .vc-sub {
        font-family: 'Rajdhani', sans-serif;
        color: #fff3e6;
        font-weight: 600;
        font-size: 1.1rem;
        margin-top: 1rem;
        text-shadow: 0 2px 8px rgba(30,10,45,0.55);
        max-width: 640px;
        margin-left: auto;
        margin-right: auto;
    }
    .vc-tagline {
        margin-top: 1rem;
        font-family: 'Teko', sans-serif;
        font-size: 1.05rem;
        letter-spacing: 4px;
        color: #ffe6c9;
        text-transform: uppercase;
        text-shadow: 0 2px 6px rgba(30,10,45,0.55);
    }
    .vc-tagline span { color: #fff; opacity: 0.6; margin: 0 0.6rem; }

    /* ---------------- Preference panel (glass over the sky) ---------------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(24, 10, 40, 0.55);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 200, 160, 0.35);
        border-radius: 10px;
        padding: 0.5rem;
        box-shadow: 0 20px 50px -20px rgba(20, 5, 30, 0.7);
    }

    h3 {
        font-family: 'Bungee', sans-serif !important;
        color: #ffe0c2 !important;
        font-weight: 400 !important;
        font-size: 1.15rem !important;
        letter-spacing: 1px;
        border-left: 4px solid #f6935e;
        padding-left: 0.8rem;
        margin-bottom: 1.2rem !important;
        text-shadow: 0 2px 6px rgba(20,5,30,0.6);
    }

    label[data-testid="stWidgetLabel"] p {
        color: #ffd9b0 !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }

    div[data-baseweb="select"] > div {
        background-color: rgba(15, 6, 28, 0.65) !important;
        border-radius: 6px !important;
        border: 1px solid rgba(255, 180, 130, 0.4) !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: #ffb168 !important;
        box-shadow: 0 0 14px rgba(255, 130, 90, 0.4);
    }
    div[data-baseweb="select"] span { color: #fff3e6 !important; }

    /* ---------------- CTA button ---------------- */
    div.stButton > button {
        background: linear-gradient(90deg, #f6935e, #ee6aa0);
        color: #2a1140;
        font-family: 'Bungee', sans-serif;
        font-weight: 400;
        font-size: 1rem;
        letter-spacing: 1px;
        border: none;
        border-radius: 8px;
        padding: 0.85rem 0;
        box-shadow: 0 12px 28px -8px rgba(238, 106, 160, 0.6);
        transition: all 0.18s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 34px -8px rgba(246, 147, 94, 0.75);
        color: #2a1140;
    }

    /* ---------------- Result ---------------- */
    div[data-testid="stSuccess"] {
        background: rgba(24, 10, 40, 0.6);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 180, 130, 0.5);
        border-radius: 8px;
        font-family: 'Bungee', sans-serif;
        font-size: 1.25rem;
        padding: 1.1rem 1.4rem;
        color: #ffe0c2;
        text-shadow: 0 2px 6px rgba(20,5,30,0.6);
    }
    div[data-testid="stError"] {
        border-radius: 8px;
        border: 1px solid rgba(255, 130, 90, 0.5);
    }

    .vc-caption {
        color: #fff3e6;
        font-size: 0.98rem;
        font-weight: 600;
        margin-top: 0.4rem;
        text-shadow: 0 2px 6px rgba(20,5,30,0.5);
    }
    /* ---------------- Footer ---------------- */
    .vc-footer {
        text-align: center;
        margin-top: 6rem;
        padding: 2.5rem 1rem 4rem;
        color: #fff3e6;
        font-family: 'Rajdhani', sans-serif;
        text-shadow: 0 3px 12px rgba(30, 10, 45, 0.7);
    }

    .vc-footer-title {
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: 3px;
        margin-bottom: 1rem;
    }

    .vc-footer-note {
        font-size: 1.45rem;
        font-style: italic;
        font-weight: 600;
        opacity: 0.92;
        margin-bottom: 0.8rem;
    }

    .vc-footer-credit {
        font-size: 1.1rem;
        font-weight: 500;
        opacity: 0.68;
        letter-spacing: 1.2px;
    }
</style>

<svg id="palm-overlay" viewBox="0 0 1000 1000" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <g id="frond">
      <path d="M0,0 C25,-55 70,-85 130,-100 C90,-70 45,-35 0,0 Z" fill="#2a1a4d"/>
    </g>
    <g id="palmTree">
      <path d="M0,600 C-4,470 10,340 6,210" stroke="#2a1a4d" stroke-width="14" fill="none" stroke-linecap="round"/>
      <use href="#frond" transform="translate(6,210) rotate(-100)"/>
      <use href="#frond" transform="translate(6,210) rotate(-55)"/>
      <use href="#frond" transform="translate(6,210) rotate(-15)"/>
      <use href="#frond" transform="translate(6,210) rotate(20) scale(-1,1)"/>
      <use href="#frond" transform="translate(6,210) rotate(60) scale(-1,1)"/>
      <use href="#frond" transform="translate(6,210) rotate(100) scale(-1,1)"/>
    </g>
  </defs>

  <!-- left cluster -->
  <use href="#palmTree" transform="translate(-40,340) scale(1.35)"/>
  <use href="#palmTree" transform="translate(30,420) scale(1.0)"/>
  <use href="#palmTree" transform="translate(-10,520) scale(0.75)"/>

  <!-- right cluster (mirrored, anchored higher) -->
  <use href="#palmTree" transform="translate(1040,300) scale(-1.4,1.4)"/>
  <use href="#palmTree" transform="translate(970,380) scale(-1.05,1.05)"/>
</svg>
""", unsafe_allow_html=True)

st.markdown("""
<div class="vc-contact">
    <a href="https://github.com/DineshMSDian" target="_blank">↗ GitHub</a>
    <a href="mailto:dinesh2742004@gmail.com">✉ Email</a>
</div>

<div class="vc-hero">
    <div class="vc-eyebrow">DINESH PRESENTS</div>
    <div class="vc-title">CHENNAI PG<br/>INTELLIGENCE</div>
    <div class="vc-sub">
        Went to Chennai for a job and got tired of searching for a PG? Twin i got you,Set your preferences and get an estimated local rent instantly.
    </div>
    <div class="vc-tagline">ECR <span>·</span> OMR <span>·</span> ADYAR <span>·</span> Velachery</div>
</div>
""", unsafe_allow_html=True)

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
    if st.button(f'Fetch price in {locality}', width='stretch', ):
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
            st.markdown(
                f'<p class="vc-caption">Actual rent for {occupancy.lower()} sharing room in {locality} '
                f'ranges from ₹{approximent_rent(result["lower"])} to ₹{approximent_rent(result["upper"])}</p>',
                unsafe_allow_html=True
            )
        else:
            st.error("Prediction failed. Please try again.")

st.markdown("""
<div class="vc-footer"><div class="vc-footer-title">🎵 Theme inspired by GTA Vice City</div><div class="vc-footer-note">Because why not? I built a GTA themed UI before GTA 6 :)</div><div class="vc-footer-credit">Grand Theft Auto: Vice City © Rockstar Games</div></div>
""", unsafe_allow_html=True)