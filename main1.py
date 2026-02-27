import streamlit as st
from streamlit_geolocation import streamlit_geolocation

st.title("המיקום שלי (iOS)")

st.write("לחץ על הכפתור ואשר הרשאת מיקום בדפדפן.")

location = streamlit_geolocation()

# הספרייה מחזירה dict; אם אין הרשאה/אין נתונים זה יכול להיות None/ריק
if location:
    st.success("המיקום התקבל ✅")
    st.write("Latitude:", location.get("latitude"))
    st.write("Longitude:", location.get("longitude"))
    st.write("Accuracy (m):", location.get("accuracy"))
else:
    st.info("עדיין אין מיקום. אשר הרשאה או נסה שוב.")
