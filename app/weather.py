from pyowm.owm import OWM
import streamlit as st

owm = OWM(st.secrets["OpenWeatherM_key"])

weather_mgr = owm.weather_manager()