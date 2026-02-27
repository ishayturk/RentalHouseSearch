import streamlit as st
from streamlit_geolocation import streamlit_geolocation

st.title("Debug Geolocation")

location = streamlit_geolocation()

st.write("RAW location object:")
st.json(location)  # חשוב! זה יראה לך בדיוק איך זה בנוי

if location:
    st.success("המיקום התקבל ✅")
else:
    st.warning("אין נתוני מיקום עדיין")
