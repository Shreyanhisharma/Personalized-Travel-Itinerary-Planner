import json
import os
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import streamlit as st

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
TRIPS_FILE = DATA_DIR / "trips.json"
DATA_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="WanderWise | Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Styling ---------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
:root { --ink:#17332e; --muted:#60736d; --cream:#f7f7f0; --green:#286653; --lime:#d9edb6; }
.stApp { background: linear-gradient(135deg,#f7f7f0 0%,#eef5eb 55%,#f8f3e9 100%); color:var(--ink); }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
h1,h2,h3 { color:var(--ink); }
.hero { padding:1.5rem 1.7rem; border-radius:24px; color:#fff; background:linear-gradient(115deg,#174b40,#31745d 65%,#a4b979); margin-bottom:1.1rem; }
.hero h1 { color:white; font-family:'Playfair Display',serif; font-size:2.5rem; margin:0; }
.hero p { color:#edf6e9; margin:.45rem 0 0; font-size:1.02rem; }
.eyebrow { text-transform:uppercase; letter-spacing:.16em; font-size:.72rem; font-weight:700; color:#d9edb6; }
.metric-card { background:rgba(255,255,255,.78); border:1px solid #dce7d7; padding:1rem 1.1rem; border-radius:17px; height:100%; }
.metric-label { font-size:.8rem; color:#60736d; }
.metric-value { font-size:1.55rem; font-weight:700; color:#17332e; margin-top:.25rem; }
.place-card { background:rgba(255,255,255,.82); border:1px solid #dce7d7; padding:1rem; border-radius:18px; margin-bottom:.6rem; }
.tag { display:inline-block; background:#e5f1d8; color:#2a614b; border-radius:999px; padding:.25rem .6rem; font-size:.75rem; margin:.15rem .2rem .15rem 0; }
.day-head { background:#e3eddb; border-radius:12px; padding:.65rem .9rem; margin:.6rem 0; font-weight:700; }
div.stButton > button { border-radius:12px; font-weight:600; border:1px solid #c8d8c1; }
[data-testid="stSidebar"] { background:#edf3e8; }
small, .muted { color:#60736d; }
</style>
""", unsafe_allow_html=True)

# ----------------------------- Demo data -------------------------------------
DESTINATIONS = {
    "Goa": {
        "vibes": ["Beach", "Friends", "Relaxed", "Food", "Nightlife"],
        "tags": ["Beach sunsets", "Seafood & cafés", "Night markets"],
        "budget": "Moderate",
        "activities": [
            ("Morning Sightseeing", "Old Goa heritage walk", "History", 350, "Old Goa"),
            ("Morning Sightseeing", "Beach walk and swim", "Beach", 0, "North Goa"),
            ("Lunch Recommendation", "Local Goan thali", "Food", 450, "North Goa"),
            ("Afternoon Leisure", "Spice plantation visit", "Nature", 700, "Ponda"),
            ("Afternoon Leisure", "Kayaking or water sports", "Adventure", 1200, "North Goa"),
            ("Evening Dining & Entertainment", "Sunset at a beach shack", "Beach", 650, "North Goa"),
            ("Evening Dining & Entertainment", "Night market browsing", "Shopping", 300, "North Goa"),
            ("Evening Dining & Entertainment", "Live music café", "Nightlife", 800, "North Goa"),
        ],
    },
    "Jaipur": {
        "vibes": ["Cultural", "History", "Food", "Family", "Moderate"],
        "tags": ["Royal architecture", "Craft bazaars", "Rajasthani food"],
        "budget": "Budget",
        "activities": [
            ("Morning Sightseeing", "Amber Fort visit", "History", 500, "Amer"),
            ("Morning Sightseeing", "City Palace and old city", "History", 450, "Old Jaipur"),
            ("Lunch Recommendation", "Vegetarian Rajasthani thali", "Food", 300, "Old Jaipur"),
            ("Afternoon Leisure", "Hawa Mahal photo stop", "Culture", 200, "Old Jaipur"),
            ("Afternoon Leisure", "Jantar Mantar visit", "History", 250, "Old Jaipur"),
            ("Evening Dining & Entertainment", "Explore local craft bazaar", "Shopping", 250, "Old Jaipur"),
            ("Evening Dining & Entertainment", "Rooftop dinner", "Food", 600, "Old Jaipur"),
        ],
    },
    "Manali": {
        "vibes": ["Mountains", "Adventure", "Nature", "Couple", "Relaxed"],
        "tags": ["Mountain views", "Outdoor adventures", "Cosy cafés"],
        "budget": "Moderate",
        "activities": [
            ("Morning Sightseeing", "Old Manali village walk", "Culture", 100, "Old Manali"),
            ("Morning Sightseeing", "Hadimba Temple and cedar forest", "History", 50, "Manali"),
            ("Lunch Recommendation", "Himalayan café lunch", "Food", 400, "Old Manali"),
            ("Afternoon Leisure", "Vashisht hot springs area", "Nature", 100, "Vashisht"),
            ("Afternoon Leisure", "Short guided nature hike", "Adventure", 900, "Solang side"),
            ("Evening Dining & Entertainment", "Riverside sunset walk", "Nature", 0, "Manali"),
            ("Evening Dining & Entertainment", "Dinner at a mountain-view café", "Food", 650, "Old Manali"),
        ],
    },
    "Delhi": {
        "vibes": ["Urban", "Cultural", "History", "Food", "Nightlife"],
        "tags": ["Historic landmarks", "Street food", "Arts & markets"],
        "budget": "Budget",
        "activities": [
            ("Morning Sightseeing", "Humayun's Tomb", "History", 400, "Central Delhi"),
            ("Morning Sightseeing", "India Gate and central avenue", "Culture", 0, "Central Delhi"),
            ("Lunch Recommendation", "Old Delhi vegetarian food walk", "Food", 350, "Old Delhi"),
            ("Afternoon Leisure", "National museum visit", "History", 300, "Central Delhi"),
            ("Afternoon Leisure", "Lodhi Garden stroll", "Nature", 0, "South Delhi"),
            ("Evening Dining & Entertainment", "Browse Dilli Haat crafts", "Shopping", 150, "South Delhi"),
            ("Evening Dining & Entertainment", "Dinner in a neighbourhood café", "Food", 650, "South Delhi"),
        ],
    },
    "Udaipur": {
        "vibes": ["Cultural", "Couple", "Relaxed", "History", "Food"],
        "tags": ["Lake views", "Palace architecture", "Slow travel"],
        "budget": "Moderate",
        "activities": [
            ("Morning Sightseeing", "City Palace complex", "History", 500, "Lake Pichola"),
            ("Morning Sightseeing", "Old town heritage walk", "Culture", 250, "Old town"),
            ("Lunch Recommendation", "Vegetarian Mewari lunch", "Food", 350, "Old town"),
            ("Afternoon Leisure", "Saheliyon-ki-Bari gardens", "Nature", 100, "North Udaipur"),
            ("Afternoon Leisure", "Artisan shops and galleries", "Shopping", 200, "Old town"),
            ("Evening Dining & Entertainment", "Lakefront sunset viewpoint", "Nature", 0, "Lake Pichola"),
            ("Evening Dining & Entertainment", "Rooftop dinner with lake views", "Food", 750, "Lake Pichola"),
        ],
    },
    "Mumbai": {
        "vibes": ["Urban", "Food", "Nightlife", "Friends", "Culture"],
        "tags": ["Coastal city energy", "Street food", "Arts & nightlife"],
        "budget": "Moderate",
        "activities": [
            ("Morning Sightseeing", "Gateway of India and waterfront", "History", 0, "Colaba"),
            ("Morning Sightseeing", "Kala Ghoda art district", "Culture", 200, "Fort"),
            ("Lunch Recommendation", "Vegetarian Mumbai street-food crawl", "Food", 350, "South Mumbai"),
            ("Afternoon Leisure", "Chhatrapati Shivaji Maharaj Vastu Sangrahalaya", "History", 500, "Fort"),
            ("Afternoon Leisure", "Marine Drive stroll", "Nature", 0, "Marine Drive"),
            ("Evening Dining & Entertainment", "Sunset at Marine Drive", "Nature", 0, "Marine Drive"),
            ("Evening Dining & Entertainment", "Dinner at a local café", "Food", 700, "Bandra"),
        ],
    },
}
VIBES = ["Beach", "Mountains", "Cultural", "Urban", "Nature", "Adventure", "Food", "Nightlife"]
INTERESTS = ["Food", "Adventure", "History", "Nightlife", "Nature", "Shopping", "Culture", "Beach"]
BUDGET_MULTIPLIER = {"Budget": 0.72, "Moderate": 1.0, "Luxury": 1.85}
PARTY_MULTIPLIER = {"Solo": 1.0, "Couple": 1.75, "Family": 2.8, "Friends": 2.4}
SLOT_ORDER = ["Morning Sightseeing", "Lunch Recommendation", "Afternoon Leisure", "Evening Dining & Entertainment"]

# ----------------------------- Persistence -----------------------------------
def load_trips() -> list[dict[str, Any]]:
    try:
        if TRIPS_FILE.exists():
            data = json.loads(TRIPS_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        st.warning("Trip history could not be read. Starting with an empty history.")
    return []

def save_trips(trips: list[dict[str, Any]]) -> None:
    try:
        TRIPS_FILE.write_text(json.dumps(trips, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError as exc:
        st.error(f"Could not save trip history: {exc}")

def money(amount: float, currency: str) -> str:
    if currency == "USD":
        return f"${amount:,.0f}"
    return f"₹{amount:,.0f}"

def get_city_activities(city: str) -> list[tuple]:
    if city in DESTINATIONS:
        return DESTINATIONS[city]["activities"]
    return DESTINATIONS["Jaipur"]["activities"]

def recommend_destinations(vibe: str, budget: str, interests: list[str], month: int) -> list[tuple[str, int, list[str]]]:
    results = []
    season_tags = {
        "Goa": "Best in cooler months; monsoon changes beach plans",
        "Jaipur": "Pleasant for heritage walks in cooler months",
        "Manali": "Mountain scenery; check seasonal road conditions",
        "Delhi": "Museums and urban culture; summer can be very hot",
        "Udaipur": "Lake views and heritage experiences",
        "Mumbai": "Food, arts and coastal city life",
    }
    for city, info in DESTINATIONS.items():
        score = 0
        city_vibes = [v.lower() for v in info["vibes"]]
        if vibe.lower() in city_vibes:
            score += 4
        score += sum(2 for interest in interests if interest.lower() in city_vibes or interest.lower() in [a[2].lower() for a in info["activities"]])
        if budget == info["budget"]:
            score += 2
        if month in [11, 12, 1, 2] and city in ["Goa", "Jaipur", "Udaipur"]:
            score += 1
        if month in [4, 5, 6] and city == "Manali":
            score += 1
        results.append((city, score, [*info["tags"], season_tags[city]]))
    return sorted(results, key=lambda item: item[1], reverse=True)[:3]

def make_itinerary(city: str, days: int, budget: str, party: str, pace: str, interests: list[str], start_date: date, currency: str) -> list[dict]:
    activities = get_city_activities(city)
    target_count = {"Relaxed": 3, "Moderate": 4, "Fast-Paced": 5}[pace]
    itinerary = []
    for day_index in range(days):
        day_activities = []
        # Cycle through a destination's activities while preferring the user's interests.
        candidates = list(activities)
        random.Random(f"{city}-{day_index}-{','.join(interests)}").shuffle(candidates)
        chosen = []
        for slot in SLOT_ORDER:
            pool = [a for a in candidates if a[0] == slot and (not interests or a[2] in interests or slot in ["Lunch Recommendation", "Morning Sightseeing"])]
            if not pool:
                pool = [a for a in candidates if a[0] == slot]
            if pool:
                activity = pool[day_index % len(pool)]
                if activity not in chosen:
                    chosen.append(activity)
            if len(chosen) >= target_count:
                break
        # Fill missing slots so the itinerary always has a sensible structure.
        for slot in SLOT_ORDER:
            if len(chosen) >= min(target_count, len(SLOT_ORDER)):
                break
            pool = [a for a in candidates if a[0] == slot and a not in chosen]
            if pool:
                chosen.append(pool[0])
        for slot in SLOT_ORDER:
            activity = next((a for a in chosen if a[0] == slot), None)
            if activity is None:
                continue
            _, title, category, base_cost, area = activity
            estimated = int(base_cost * BUDGET_MULTIPLIER[budget] * PARTY_MULTIPLIER[party])
            if "Food" in interests and slot == "Lunch Recommendation" and "vegetarian" not in title.lower():
                title = "Vegetarian-friendly local lunch (confirm availability)"
            day_activities.append({
                "slot": slot,
                "time": {"Morning Sightseeing":"09:00", "Lunch Recommendation":"12:30", "Afternoon Leisure":"14:30", "Evening Dining & Entertainment":"18:30"}[slot],
                "title": title,
                "category": category,
                "area": area,
                "estimated_cost": estimated,
                "notes": "Demo estimate; confirm opening hours, prices and availability before travel."
            })
        itinerary.append({
            "day": day_index + 1,
            "date": (start_date + timedelta(days=day_index)).isoformat(),
            "area_cluster": day_activities[0]["area"] if day_activities else city,
            "activities": day_activities,
        })
    return itinerary

def trip_total(trip: dict) -> int:
    return sum(a.get("estimated_cost", 0) for d in trip.get("itinerary", []) for a in d.get("activities", []))

def build_pdf_bytes(trip: dict) -> bytes:
    from io import BytesIO
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TripTitle", parent=styles["Title"], textColor=colors.HexColor("#174b40"), alignment=TA_LEFT, fontSize=24, leading=28, spaceAfter=8))
    styles.add(ParagraphStyle(name="DayTitle", parent=styles["Heading2"], textColor=colors.HexColor("#286653"), spaceBefore=12, spaceAfter=7))
    styles.add(ParagraphStyle(name="SmallText", parent=styles["BodyText"], fontSize=8, leading=11, textColor=colors.HexColor("#53665f")))
    story = [
        Paragraph("WanderWise", styles["TripTitle"]),
        Paragraph(f"<b>{trip.get('city','Your Trip')} — Personalized Travel Guide</b>", styles["Heading2"]),
        Paragraph(f"{trip.get('start_date','')} · {trip.get('days', 1)} days · {trip.get('budget','Moderate')} budget · {trip.get('party','Solo')}", styles["BodyText"]),
        Spacer(1, 12),
        Paragraph("Estimated activity spend", styles["Heading3"]),
        Paragraph(f"<b>{money(trip_total(trip), trip.get('currency','INR'))}</b> — activity estimates only; transport, lodging and other costs may be excluded.", styles["BodyText"]),
        Spacer(1, 14),
    ]
    for day in trip.get("itinerary", []):
        story.append(Paragraph(f"Day {day['day']} · {day['date']}", styles["DayTitle"]))
        rows = [["Time", "Plan", "Area", "Estimate"]]
        for a in day.get("activities", []):
            rows.append([a.get("time",""), a.get("title",""), a.get("area",""), money(a.get("estimated_cost",0), trip.get("currency","INR"))])
        table = Table(rows, colWidths=[52, 220, 95, 70], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#174b40")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),8),
            ("LEADING",(0,0),(-1,-1),10),
            ("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#d6e1d2")),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#f3f7ef")]),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("LEFTPADDING",(0,0),(-1,-1),6),
            ("RIGHTPADDING",(0,0),(-1,-1),6),
            ("TOPPADDING",(0,0),(-1,-1),6),
            ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ]))
        story.extend([table, Spacer(1, 8)])
    story.extend([
        PageBreak(),
        Paragraph("Before You Go", styles["DayTitle"]),
        Paragraph("□ Confirm accommodation and transport bookings", styles["BodyText"]),
        Paragraph("□ Check attraction opening hours and ticket requirements", styles["BodyText"]),
        Paragraph("□ Check local weather and any travel advisories", styles["BodyText"]),
        Paragraph("□ Save offline maps and copies of essential documents", styles["BodyText"]),
        Paragraph("□ Share your itinerary with a trusted contact", styles["BodyText"]),
        Spacer(1, 12),
        Paragraph("Emergency contacts checklist", styles["DayTitle"]),
        Paragraph("Local emergency number: __________________________", styles["BodyText"]),
        Paragraph("Accommodation / host: _____________________________", styles["BodyText"]),
        Paragraph("Trusted contact: ___________________________________", styles["BodyText"]),
        Spacer(1, 14),
        Paragraph("Planning note: This guide uses demo destination data and approximate costs. Verify details with official or local sources before booking.", styles["SmallText"]),
    ])
    doc.build(story)
    return buffer.getvalue()

# ----------------------------- Header ----------------------------------------
st.markdown("""
<div class="hero">
  <div class="eyebrow">YOUR NEXT CHAPTER STARTS HERE</div>
  <h1>WanderWise 🌿</h1>
  <p>Thoughtful trips, less transit fatigue, more moments worth remembering.</p>
</div>
""", unsafe_allow_html=True)

if "trips" not in st.session_state:
    st.session_state.trips = load_trips()
if "active_trip" not in st.session_state:
    st.session_state.active_trip = None

# ----------------------------- Sidebar ---------------------------------------
with st.sidebar:
    st.markdown("## ✈️ Trip preferences")
    city_options = ["Surprise me"] + list(DESTINATIONS.keys())
    city_choice = st.selectbox("Destination", city_options, index=0)
    vibe = st.selectbox("Travel vibe", VIBES, index=0)
    days = st.slider("Trip duration (days)", 1, 10, 3)
    start_date = st.date_input("Start date", value=date.today() + timedelta(days=14), min_value=date.today())
    budget = st.selectbox("Budget level", ["Budget", "Moderate", "Luxury"], index=1)
    party = st.selectbox("Travel party", ["Solo", "Couple", "Family", "Friends"])
    pace = st.selectbox("Travel pace", ["Relaxed", "Moderate", "Fast-Paced"], index=1)
    interests = st.multiselect("Interests", INTERESTS, default=["Food", "History"])
    currency = st.radio("Display currency", ["INR", "USD"], horizontal=True)
    st.caption("Demo mode works without an API key.")
    with st.expander("Optional AI connection"):
        provider = st.selectbox("Provider", ["Demo mode", "Gemini", "Groq"])
        api_key = st.text_input("API key", type="password", help="Only used during this session; do not commit API keys to GitHub.")
        st.caption("AI provider connection is an extension point; demo itinerary generation does not require a key.")

tabs = st.tabs(["✨ Destination Match", "🗓️ Itinerary Builder", "🎨 Customize Plan", "📚 My Trips & PDF"])

# ----------------------------- Tab 1 -----------------------------------------
with tabs[0]:
    st.subheader("Find a place that fits your mood")
    st.write("Choose a fixed city or let your travel vibe guide the recommendations.")
    month = start_date.month
    recs = recommend_destinations(vibe, budget, interests, month)
    if city_choice != "Surprise me":
        st.info(f"You selected **{city_choice}**. The recommendations below are alternatives based on your vibe and interests.")
    cols = st.columns(3)
    for idx, (city, score, tags) in enumerate(recs):
        info = DESTINATIONS[city]
        with cols[idx]:
            st.markdown(f"""
            <div class="place-card">
              <div style="font-size:2rem">{['🏖️','🏰','🏔️','🌆','🌅','🌊'][list(DESTINATIONS).index(city)]}</div>
              <h3 style="margin:.35rem 0">{city}</h3>
              <div class="muted">Preference match: {score} points</div>
              <p>{' · '.join(info['tags'])}</p>
              {''.join(f'<span class="tag">{tag}</span>' for tag in info['vibes'][:3])}
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Plan a trip to {city}", key=f"recommend_{city}", use_container_width=True):
                st.session_state.recommended_city = city
                st.success(f"{city} selected. Open Itinerary Builder to generate your plan.")
    st.caption("Recommendations use bundled demo profiles and simple preference scoring, not live weather or live booking data.")

# ----------------------------- Tab 2 -----------------------------------------
with tabs[1]:
    st.subheader("Build your day-by-day plan")
    default_city = getattr(st.session_state, "recommended_city", None)
    if default_city is None and city_choice != "Surprise me":
        default_city = city_choice
    city_index = list(DESTINATIONS).index(default_city) if default_city in DESTINATIONS else 0
    chosen_city = st.selectbox("Trip destination", list(DESTINATIONS.keys()), index=city_index, key="builder_city")
    if st.button("Generate itinerary", type="primary", use_container_width=True):
        plan = make_itinerary(chosen_city, days, budget, party, pace, interests, start_date, currency)
        st.session_state.active_trip = {
            "id": f"{chosen_city.lower()}-{date.today().isoformat()}-{len(st.session_state.trips)+1}",
            "city": chosen_city,
            "days": days,
            "start_date": start_date.isoformat(),
            "budget": budget,
            "party": party,
            "pace": pace,
            "interests": interests,
            "currency": currency,
            "itinerary": plan,
            "created_at": date.today().isoformat(),
        }
    trip = st.session_state.active_trip
    if trip:
        metric_cols = st.columns(3)
        for col, label, value in zip(metric_cols, ["Destination", "Trip length", "Activity estimate"], [trip["city"], f'{trip["days"]} days', money(trip_total(trip), trip.get("currency","INR"))]):
            with col:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)
        st.write("")
        cumulative = 0
        for day in trip["itinerary"]:
            st.markdown(f'<div class="day-head">Day {day["day"]} · {day["date"]} &nbsp; <span style="font-weight:400">| Suggested area cluster: {day["area_cluster"]}</span></div>', unsafe_allow_html=True)
            for activity in day["activities"]:
                cumulative += activity["estimated_cost"]
                with st.container(border=True):
                    left, right = st.columns([4, 1])
                    with left:
                        st.markdown(f"**{activity['time']} — {activity['slot']}**")
                        st.write(f"### {activity['title']}")
                        st.caption(f"{activity['category']} · Area: {activity['area']}")
                        st.caption(activity["notes"])
                    with right:
                        st.metric("Estimate", money(activity["estimated_cost"], trip.get("currency","INR")))
                        st.caption(f"Running total: {money(cumulative, trip.get('currency','INR'))}")
        st.warning("Estimates cover the listed activities only. Accommodation, intercity travel, local transport and personal purchases may be extra.")
    else:
        st.info("Set your preferences in the sidebar, then click **Generate itinerary**.")

# ----------------------------- Tab 3 -----------------------------------------
with tabs[2]:
    st.subheader("Make the plan feel like yours")
    trip = st.session_state.active_trip
    if not trip:
        st.info("Generate an itinerary first in the Itinerary Builder tab.")
    else:
        day_numbers = [d["day"] for d in trip["itinerary"]]
        selected_day = st.selectbox("Choose a day to edit", day_numbers)
        day = trip["itinerary"][selected_day - 1]
        activity_names = [f'{a["time"]} · {a["title"]}' for a in day["activities"]]
        selected_activity_idx = st.selectbox("Choose a time slot", range(len(activity_names)), format_func=lambda i: activity_names[i])
        selected_activity = day["activities"][selected_activity_idx]
        st.markdown(f"**Current activity:** {selected_activity['title']}")
        swap_type = st.selectbox("What would you prefer instead?", ["Outdoor market", "Vegetarian lunch spot", "Museum or heritage site", "Nature walk", "Adventure activity", "Quiet café", "Free-time / rest"])
        swap_cost = st.number_input("Estimated cost for replacement (in selected currency)", min_value=0, max_value=100000, value=int(selected_activity["estimated_cost"]), step=100)
        if st.button("Swap selected activity", type="primary"):
            replacements = {
                "Outdoor market": ("Explore a local outdoor market", "Shopping"),
                "Vegetarian lunch spot": ("Vegetarian-friendly local restaurant (verify hours)", "Food"),
                "Museum or heritage site": ("Visit a local museum or heritage site", "History"),
                "Nature walk": ("Scenic nature walk in a nearby area", "Nature"),
                "Adventure activity": ("Book a locally guided adventure activity", "Adventure"),
                "Quiet café": ("Relax at a quiet local café", "Food"),
                "Free-time / rest": ("Unscheduled rest and personal exploration", "Leisure"),
            }
            title, category = replacements[swap_type]
            selected_activity.update({"title": title, "category": category, "estimated_cost": int(swap_cost), "notes": "User-customized activity. Verify details before travel."})
            st.session_state.active_trip = trip
            st.success("Activity updated. The rest of your itinerary remains unchanged.")
            st.rerun()
        if st.button("Regenerate this day only"):
            replacement_day = make_itinerary(trip["city"], 1, trip["budget"], trip["party"], trip["pace"], trip["interests"], date.fromisoformat(day["date"]), trip["currency"])[0]
            replacement_day["day"] = selected_day
            trip["itinerary"][selected_day - 1] = replacement_day
            st.session_state.active_trip = trip
            st.success(f"Day {selected_day} regenerated. Other days were preserved.")
            st.rerun()

# ----------------------------- Tab 4 -----------------------------------------
with tabs[3]:
    st.subheader("Your saved trips")
    trip = st.session_state.active_trip
    left, right = st.columns([1, 1])
    with left:
        if trip and st.button("💾 Save current trip", type="primary", use_container_width=True):
            existing_ids = {t.get("id") for t in st.session_state.trips}
            if trip["id"] in existing_ids:
                trip["id"] = f'{trip["id"]}-{len(st.session_state.trips)+1}'
            st.session_state.trips.insert(0, trip.copy())
            save_trips(st.session_state.trips)
            st.success("Trip saved to local JSON history.")
    with right:
        if trip:
            try:
                pdf_bytes = build_pdf_bytes(trip)
                st.download_button("⬇️ Export travel guide PDF", data=pdf_bytes, file_name=f'{trip["city"].lower()}_travel_guide.pdf', mime="application/pdf", use_container_width=True)
            except Exception as exc:
                st.error(f"PDF export failed. Check that ReportLab is installed. Details: {exc}")
        else:
            st.button("⬇️ Export travel guide PDF", disabled=True, use_container_width=True)
    st.caption("Local JSON storage is ideal for a demo. On Streamlit Community Cloud, local files may not be durable across app restarts or redeployments.")
    st.markdown("---")
    if not st.session_state.trips:
        st.info("No saved trips yet. Generate a plan and save it here.")
    else:
        for idx, saved in enumerate(st.session_state.trips):
            with st.expander(f'{saved.get("city","Trip")} · {saved.get("start_date","")} · {saved.get("days",1)} days'):
                st.write(f"Budget: {saved.get('budget')} · Party: {saved.get('party')} · Pace: {saved.get('pace')}")
                st.write(f"Estimated activities: {money(trip_total(saved), saved.get('currency','INR'))}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Load this trip", key=f"load_{idx}"):
                        st.session_state.active_trip = saved
                        st.success("Trip loaded into the itinerary builder.")
                        st.rerun()
                with c2:
                    try:
                        pdf = build_pdf_bytes(saved)
                        st.download_button("Download PDF", data=pdf, file_name=f'{saved.get("city","trip").lower()}_guide.pdf', mime="application/pdf", key=f"pdf_{idx}")
                    except Exception as exc:
                        st.error(f"PDF issue: {exc}")

st.markdown("---")
st.caption("WanderWise demo · Estimates and recommendations are illustrative, not live travel advice. Verify local details before booking.")
