import math
import random
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import requests
import streamlit as st


# -----------------------------
# Utils
# -----------------------------
def haversine_m(lat1, lon1, lat2, lon2) -> float:
    """Distance in meters between two lat/lon points."""
    R = 6371000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@st.cache_data(show_spinner=False, ttl=60 * 60)
def geocode_address(address: str) -> Optional[Dict[str, float]]:
    """Free geocoding via Nominatim. Returns {lat, lon} or None."""
    address = address.strip()
    if not address:
        return None

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    headers = {"User-Agent": "rental-house-search-demo/1.0 (streamlit)"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}
    except Exception:
        return None


# -----------------------------
# Data model
# -----------------------------
@dataclass
class Listing:
    id: str
    title: str
    address: str
    price: int
    rooms: float
    seller_type: str  # "private" | "broker" | "unknown"
    features: List[str]  # e.g. ["parking", "elevator", "balcony", "mamad"]
    lat: float
    lon: float
    url: str


# -----------------------------
# Provider (Mock for now)
# -----------------------------
class MockProvider:
    """
    Provider that generates fake listings around the center point.
    Replace this later with MadlanProvider/AgentProvider.
    """

    FEATURE_POOL = ["parking", "elevator", "balcony", "mamad", "storage", "furnished", "ac"]

    def search(self, center_lat: float, center_lon: float, radius_m: int) -> List[Listing]:
        # deterministic seed for stable results per location/radius
        seed = int((center_lat * 1000) + (center_lon * 1000) + radius_m)
        rnd = random.Random(seed)

        listings: List[Listing] = []
        for i in range(60):  # base pool before filtering/pagination
            # random point within ~radius
            angle = rnd.random() * 2 * math.pi
            dist = rnd.random() * radius_m
            # rough meters->degrees conversion
            dlat = (dist * math.cos(angle)) / 111_320.0
            dlon = (dist * math.sin(angle)) / (111_320.0 * math.cos(math.radians(center_lat)) + 1e-9)

            lat = center_lat + dlat
            lon = center_lon + dlon

            price = rnd.randrange(3500, 14500, 100)
            rooms = rnd.choice([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0])
            seller_type = rnd.choice(["private", "broker", "unknown"])

            feats = [f for f in self.FEATURE_POOL if rnd.random() < 0.35]

            listings.append(
                Listing(
                    id=f"mock-{seed}-{i}",
                    title=f"דירה להשכרה · {rooms:g} חדרים",
                    address=f"כתובת לדוגמה #{i+1}",
                    price=price,
                    rooms=rooms,
                    seller_type=seller_type,
                    features=feats,
                    lat=lat,
                    lon=lon,
                    url="https://example.com/listing",
                )
            )
        return listings


# -----------------------------
# Filtering
# -----------------------------
def apply_filters(
    listings: List[Listing],
    center_lat: float,
    center_lon: float,
    radius_m: int,
    max_price: Optional[int],
    rooms_min: Optional[float],
    rooms_max: Optional[float],
    seller_filter: str,  # "any" | "private_only" | "broker_only"
    required_features: List[str],
) -> List[Listing]:
    out = []
    for x in listings:
        # radius
        if haversine_m(center_lat, center_lon, x.lat, x.lon) > radius_m:
            continue
        # price
        if max_price is not None and x.price > max_price:
            continue
        # rooms
        if rooms_min is not None and x.rooms < rooms_min:
            continue
        if rooms_max is not None and x.rooms > rooms_max:
            continue
        # seller
        if seller_filter == "private_only" and x.seller_type != "private":
            continue
        if seller_filter == "broker_only" and x.seller_type != "broker":
            continue
        # features
        if any(f not in x.features for f in required_features):
            continue

        out.append(x)

    # sort: nearest first, then cheaper
    out.sort(key=lambda a: (haversine_m(center_lat, center_lon, a.lat, a.lon), a.price))
    return out


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="חיפוש דירות (MVP)", layout="wide")
st.title("חיפוש דירות להשכרה (MVP)")

with st.sidebar:
    st.header("חיפוש")
    address = st.text_input("כתובת (עיר/רחוב/מספר)", placeholder="לדוגמה: דיזנגוף 100 תל אביב")
    radius_m = st.selectbox("רדיוס", [500, 1000, 2000, 3000, 5000], index=1)

    st.divider()
    st.subheader("פילטרים")

    max_price = st.number_input("מחיר מקסימלי (ש״ח)", min_value=0, max_value=100_000, value=0, step=100)
    max_price = None if max_price == 0 else int(max_price)

    rooms_min = st.selectbox("חדרים מינ׳", [None, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0], index=0)
    rooms_max = st.selectbox("חדרים מקס׳", [None, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0], index=0)

    seller_filter = st.radio(
        "תיווך",
        options=[("any", "הכל"), ("private_only", "ללא תיווך בלבד"), ("broker_only", "רק תיווך")],
        format_func=lambda x: x[1],
        index=0,
    )[0]

    st.markdown("**מאפיינים** (חייבים להיות קיימים במודעה)")
    feature_labels = {
        "parking": "חניה",
        "elevator": "מעלית",
        "balcony": "מרפסת",
        "mamad": "ממ״ד",
        "storage": "מחסן",
        "furnished": "מרוהט",
        "ac": "מיזוג",
    }
    required_features = []
    for k, label in feature_labels.items():
        if st.checkbox(label, value=False):
            required_features.append(k)

    st.divider()
    per_page = 10

    if "page" not in st.session_state:
        st.session_state.page = 0

    run_search = st.button("חפש")

# Geocode + Search trigger logic
if run_search:
    st.session_state.page = 0

if not address.strip():
    st.info("הכנס כתובת כדי להתחיל.")
    st.stop()

coords = geocode_address(address)
if not coords:
    st.error("לא הצלחתי למצוא את הכתובת. נסה לנסח אחרת (עיר + רחוב).")
    st.stop()

center_lat, center_lon = coords["lat"], coords["lon"]

provider = MockProvider()  # TODO: replace later
all_listings = provider.search(center_lat, center_lon, radius_m)

filtered = apply_filters(
    all_listings,
    center_lat=center_lat,
    center_lon=center_lon,
    radius_m=radius_m,
    max_price=max_price,
    rooms_min=rooms_min,
    rooms_max=rooms_max,
    seller_filter=seller_filter,
    required_features=required_features,
)

total = len(filtered)
page = st.session_state.page
start = page * per_page
end = start + per_page
page_items = filtered[start:end]

col1, col2 = st.columns([2, 1])
with col1:
    st.caption(f"מרכז: ({center_lat:.5f}, {center_lon:.5f}) · רדיוס: {radius_m}m · נמצאו {total} תוצאות")
with col2:
    prev_disabled = page <= 0
    next_disabled = end >= total
    b1, b2 = st.columns(2)
    with b1:
        if st.button("⬅ הקודם", disabled=prev_disabled):
            st.session_state.page = max(0, st.session_state.page - 1)
            st.rerun()
    with b2:
        if st.button("הבא ➡", disabled=next_disabled):
            st.session_state.page = st.session_state.page + 1
            st.rerun()

if not page_items:
    st.warning("אין תוצאות בעמוד הזה. נסה להגדיל רדיוס או להקל בפילטרים.")
    st.stop()

for x in page_items:
    dist = int(haversine_m(center_lat, center_lon, x.lat, x.lon))
    seller_txt = {"private": "ללא תיווך", "broker": "תיווך", "unknown": "לא ידוע"}.get(x.seller_type, "לא ידוע")
    feats_txt = " · ".join([feature_labels.get(f, f) for f in x.features]) or "—"
    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            st.markdown(f"### {x.title}")
            st.write(f"{x.address} · {dist} מטר מהמרכז")
            st.write(f"מאפיינים: {feats_txt}")
        with c2:
            st.metric("מחיר", f"₪{x.price:,}")
            st.write(f"חדרים: {x.rooms:g}")
        with c3:
            st.write(f"סוג מוכר: **{seller_txt}**")
            st.link_button("למודעה", x.url)
