import streamlit as st
from streamlit_js_eval import get_geolocation

st.title("המיקום שלי (iOS)")

# מצב/אחסון
if "geo_requested" not in st.session_state:
    st.session_state.geo_requested = False
if "geo_result" not in st.session_state:
    st.session_state.geo_result = None

# כפתור "רגיל" — אבל אנחנו רק מסמנים מצב
st.button("קבל מיקום", key="geo_btn")
if st.session_state.get("geo_btn"):
    st.session_state.geo_requested = True

# הקריאה עצמה (לא “בתוך” if של הכפתור)
if st.session_state.geo_requested:
    loc = get_geolocation()
    st.session_state.geo_result = loc
    st.session_state.geo_requested = False

# הצגת תוצאה / שגיאה
loc = st.session_state.geo_result
if loc is None:
    st.info("לחץ 'קבל מיקום' ואשר הרשאה בדפדפן.")
elif isinstance(loc, dict) and "error" in loc:
    st.error(f"שגיאת מיקום (code={loc['error'].get('code')}): {loc['error'].get('message')}")
else:
    st.success("המיקום התקבל ✅")
    st.write("Latitude:", loc["coords"]["latitude"])
    st.write("Longitude:", loc["coords"]["longitude"])
    st.write("Accuracy (m):", loc["coords"].get("accuracy"))
