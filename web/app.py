import os
from dotenv import load_dotenv
import streamlit as st
import requests

load_dotenv()

API_URL = os.getenv('API_URL', '').rstrip('/')

# Cold start on a scale-to-zero container can take ~2 minutes.
# These timeouts are deliberately generous so the first request waits
# for the container instead of erroring out.
BOOT_TIMEOUTS = (25, 60, 120)
PREDICT_TIMEOUT = 120


def handle_bool_inputs(answer: str) -> bool:
    return answer.strip().lower() == 'yes'


def approximent_rent(rent: float):
    return round(rent / 500) * 500


@st.cache_data(show_spinner=False)
def fetch_localities():
    """Retry through a cold start before giving up."""
    last_error = None
    for timeout in BOOT_TIMEOUTS:
        try:
            response = requests.get(f'{API_URL}/get-localities', timeout=timeout)
            response.raise_for_status()
            return sorted(response.json()['localities'])
        except Exception as exc:  # noqa: BLE001 - surfaced to the user below
            last_error = exc
    raise last_error if last_error is not None else RuntimeError('Unable to fetch localities')


st.set_page_config(
    page_title='Chennai PG Intelligence',
    layout='wide',
    page_icon='🌴',
    initial_sidebar_state='collapsed',
)

# Visual layer only — no changes to app logic below this point.
# Desktop styling is unchanged; everything mobile lives in the media queries
# at the bottom of this <style> block.
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

    /* Nothing should ever scroll sideways */
    html, body, .stApp { overflow-x: hidden; }

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

    /* ---------------- Hero (transparent, sky shows through) ---------------- */
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
        font-size: clamp(0.85rem, 3vw, 1.05rem);
        color: #fff3e0;
        text-shadow: 0 2px 6px rgba(30,10,45,0.6);
        margin-bottom: 0.6rem;
    }
    .vc-title {
        font-family: 'Bungee', sans-serif;
        font-size: clamp(2.1rem, 9vw, 4rem);
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
        font-size: clamp(0.98rem, 3.6vw, 1.1rem);
        margin-top: 1rem;
        text-shadow: 0 2px 8px rgba(30,10,45,0.55);
        max-width: 640px;
        margin-left: auto;
        margin-right: auto;
    }
    .vc-tagline {
        margin-top: 1rem;
        font-family: 'Teko', sans-serif;
        font-size: clamp(0.85rem, 3.2vw, 1.05rem);
        letter-spacing: 4px;
        color: #ffe6c9;
        text-transform: uppercase;
        text-shadow: 0 2px 6px rgba(30,10,45,0.55);
    }
    .vc-tagline span { color: #fff; opacity: 0.6; margin: 0 0.6rem; }

    /* ---------------- Cold-start notice ---------------- */
    .vc-notice {
        position: relative;
        z-index: 2;
        max-width: 760px;
        margin: 0 auto 1.6rem auto;
        background: rgba(24, 10, 40, 0.55);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 200, 160, 0.35);
        border-left: 4px solid #f6935e;
        border-radius: 10px;
        padding: 0.95rem 1.2rem;
        color: #ffe9d2;
        font-size: 0.95rem;
        font-weight: 600;
        line-height: 1.5;
        text-shadow: 0 2px 6px rgba(20,5,30,0.5);
        box-shadow: 0 20px 50px -20px rgba(20, 5, 30, 0.7);
    }
    .vc-notice b { color: #ffcf9f; }

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
        font-size: clamp(1.3rem, 5.5vw, 2rem);
        font-weight: 700;
        letter-spacing: 3px;
        margin-bottom: 1rem;
    }

    .vc-footer-note {
        font-size: clamp(1.05rem, 4.2vw, 1.45rem);
        font-style: italic;
        font-weight: 600;
        opacity: 0.92;
        margin-bottom: 0.8rem;
    }

    .vc-footer-credit {
        font-size: clamp(0.9rem, 3.4vw, 1.1rem);
        font-weight: 500;
        opacity: 0.68;
        letter-spacing: 1.2px;
    }

    /* =======================================================================
       MOBILE / TABLET ADAPTATION
       Everything above is the desktop design. Below, the same markup is
       re-flowed for narrow viewports: columns stack, the hero tightens,
       palms step back, and tap targets grow.
       ======================================================================= */

    /* Tablets and below: let the 3-up rows wrap instead of squeezing */
    @media (max-width: 1024px) {
        .block-container { padding-left: 1.1rem !important; padding-right: 1.1rem !important; }
    }

    @media (max-width: 820px) {
        /* Force every column row to stack full-width */
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.35rem !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            flex: 1 1 100% !important;
            width: 100% !important;
            min-width: 100% !important;
        }

        .block-container {
            padding-top: 0.5rem !important;
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
        }

        /* Contact links move into normal flow so they can't overlap the hero */
        .vc-contact {
            position: static;
            justify-content: center;
            gap: 1.6rem;
            margin: 0.6rem 0 0.2rem 0;
        }
        .vc-contact a { font-size: 0.95rem; }

        .vc-hero {
            padding: 1.4rem 0.4rem 1.4rem 0.4rem;
            margin-bottom: 1.1rem;
        }
        .vc-eyebrow { letter-spacing: 4px; margin-bottom: 0.45rem; }
        .vc-title { -webkit-text-stroke: 1.5px #2a1140; letter-spacing: 0; }
        .vc-sub { margin-top: 0.75rem; padding: 0 0.3rem; }
        .vc-tagline { letter-spacing: 2.5px; margin-top: 0.8rem; }
        .vc-tagline span { margin: 0 0.35rem; }

        .vc-notice {
            font-size: 0.9rem;
            padding: 0.85rem 1rem;
            margin-bottom: 1.1rem;
        }

        /* Palms: keep the mood, drop the clutter on a narrow screen */
        #palm-overlay { opacity: 0.32; }
        #palm-overlay .palm-right { display: none; }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            padding: 0.35rem;
            border-radius: 12px;
        }
        h3 { font-size: 1rem !important; margin-bottom: 0.9rem !important; }

        /* Comfortable tap targets */
        label[data-testid="stWidgetLabel"] p {
            font-size: 0.74rem !important;
            text-transform: none;
            letter-spacing: 0.3px;
        }
        div[data-baseweb="select"] > div { min-height: 46px !important; }
        div.stButton > button {
            padding: 1rem 0;
            font-size: 0.95rem;
            width: 100% !important;
        }
        /* Hover transforms are meaningless on touch and cause sticky states */
        div.stButton > button:hover { transform: none; }

        div[data-testid="stSuccess"] {
            font-size: 1.05rem;
            padding: 0.9rem 1rem;
            word-break: break-word;
        }
        .vc-caption { font-size: 0.9rem; }

        .vc-footer { margin-top: 3rem; padding: 1.8rem 0.8rem 3rem; }
        .vc-footer-title { letter-spacing: 1.5px; }
    }

    /* Small phones */
    @media (max-width: 420px) {
        .vc-title { font-size: clamp(1.85rem, 10vw, 2.4rem); }
        .vc-tagline { letter-spacing: 1.8px; font-size: 0.8rem; }
        .block-container { padding-left: 0.6rem !important; padding-right: 0.6rem !important; }
    }

    /* Landscape phones: reclaim vertical space */
    @media (max-height: 520px) and (orientation: landscape) {
        .vc-hero { padding: 1rem 0.5rem; }
        .vc-footer { margin-top: 2rem; }
    }
</style>

<svg id="palm-overlay" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMax slice" xmlns="http://www.w3.org/2000/svg">
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
  <g class="palm-left">
    <use href="#palmTree" transform="translate(-40,340) scale(1.35)"/>
    <use href="#palmTree" transform="translate(30,420) scale(1.0)"/>
    <use href="#palmTree" transform="translate(-10,520) scale(0.75)"/>
  </g>

  <!-- right cluster (mirrored, anchored higher) -->
  <g class="palm-right">
    <use href="#palmTree" transform="translate(1040,300) scale(-1.4,1.4)"/>
    <use href="#palmTree" transform="translate(970,380) scale(-1.05,1.05)"/>
  </g>
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
        Went to Chennai for a job and got tired of searching for a PG? Twin i got you, set your preferences and get an estimated local rent instantly.
    </div>
    <div class="vc-tagline">ECR <span>·</span> OMR <span>·</span> ADYAR <span>·</span> Velachery</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="vc-notice">
    <b>First visit? Give it a minute.</b> This demo runs on a scale-to-zero container,
    so it sleeps when nobody is using it and the very first request has to wake it up —
    that can take up to ~2 minutes. If the page looks stuck or throws an error while it is
    still waking, just refresh once and it will come right up. Everything after that is instant.
</div>
""", unsafe_allow_html=True)

# --- Wake the API up (this is where a cold start is actually felt) -----------
try:
    with st.spinner('Waking the server up — first load after a while can take up to 2 minutes. Thanks for your patience!'):
        localities = fetch_localities()
except Exception:
    st.error(
        'The server is still waking up and did not answer in time. '
        'This is the cold start, not a broken app — give it a few seconds and try again.'
    )
    if st.button('Try again', width='stretch'):
        fetch_localities.clear()
        st.rerun()
    st.stop()

with st.container(border=True):
    st.subheader('Apply Preferences for Result')

    left_1, middle_1, right_1 = st.columns(3, vertical_alignment='bottom')
    left_2, middle_2, right_2 = st.columns(3, vertical_alignment='bottom')
    left_3, middle_3, right_3 = st.columns(3, vertical_alignment='bottom')

    locality = left_1.selectbox('Select the area you are looking for.', localities)
    gender = middle_1.selectbox('Choose Gender', ['Male', 'Female', 'Both'])
    occupancy = right_1.selectbox('Choose how many people will share the room', ['Single', 'Double', 'Three', 'Four'])

    available_for = left_2.selectbox('Select who the PG should be suitable for', ['Student', 'Working Professional', 'Anyone'])
    food_included = middle_2.selectbox('Choose whether you want food or mess included', ['Yes', 'No'])
    wifi = right_2.selectbox('Choose whether WiFi should be included', ['Yes', 'No'])

    laundry = left_3.selectbox('Choose whether laundry facilities are required', ['Yes', 'No'])
    room_ac = middle_3.selectbox('Choose whether you want an air conditioned room', ['Yes', 'No'])
    parking = right_3.selectbox('Select the parking option you need', ['Car', 'Bike', 'Bike and Car', 'No Parking'])

with st.container(border=True, horizontal_alignment='left'):
    if st.button(f'Fetch price in {locality}', width='stretch'):
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

        try:
            with st.spinner('Crunching the numbers…'):
                response = requests.post(f'{API_URL}/prediction', json=data, timeout=PREDICT_TIMEOUT)
        except requests.exceptions.RequestException:
            st.error(
                'The server nodded off again. Give it a few seconds and hit the button once more — '
                'it wakes up on demand.'
            )
        else:
            if response.status_code == 200:
                result = response.json()
                st.subheader('Estimated Monthly Rent')
                st.success(f"₹{approximent_rent(result['predicted_rent'])} / month")
                st.markdown(
                    f'<p class="vc-caption">Actual rent for {occupancy.lower()} sharing room in {locality} '
                    f'ranges from ₹{approximent_rent(result["lower"])} to ₹{approximent_rent(result["upper"])}</p>',
                    unsafe_allow_html=True
                )
            else:
                st.error('Prediction failed. Please try again.')

st.markdown("""
<div class="vc-footer"><div class="vc-footer-title">🎵 Theme inspired by GTA Vice City</div><div class="vc-footer-note">Because why not? I built a GTA themed UI before GTA 6 :)</div><div class="vc-footer-credit">Grand Theft Auto: Vice City © Rockstar Games</div></div>
""", unsafe_allow_html=True)