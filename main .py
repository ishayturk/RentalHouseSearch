import streamlit as st
from streamlit_js_eval import get_geolocation

st.title("המיקום שלי")

st.write("לחץ על הכפתור כדי לבקש הרשאת מיקום מהדפדפן")

if st.button("קבל מיקום"):
    location = get_geolocation()

    if location:
        lat = location["coords"]["latitude"]
        lon = location["coords"]["longitude"]
        acc = location["coords"]["accuracy"]

        st.success("המיקום התקבל ✅")
        st.write(f"Latitude: {lat}")
        st.write(f"Longitude: {lon}")
        st.write(f"דיוק (מטרים): {acc}")
    else:
        st.error("לא התקבלה הרשאה או שהדפדפן חסם את המיקום")
