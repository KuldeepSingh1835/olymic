import streamlit as st
import pandas as pd
from live_data import fetch_medal_tally, fetch_event_schedule
from historical_data import load_historical_data, get_country_medal_counts
from visualization import (
    plot_interactive_medals,
    plot_country_medal_trend,
    plot_country_pie,
    compare_two_countries,
    radar_compare_countries
)
from prediction import predict_future_medals, predict_multiple_countries_shared_plot
from data_loader import load_athlete_data

df = load_athlete_data()

# Convert 'Medal' column into 'Gold', 'Silver', 'Bronze' if necessary
if 'Gold' not in df.columns or 'Silver' not in df.columns or 'Bronze' not in df.columns:
    df = df[df['Medal'].notna()]
    medal_counts = df.groupby(['Year', 'NOC', 'Medal']).size().unstack(fill_value=0)
    for medal in ['Gold', 'Silver', 'Bronze']:
        if medal not in medal_counts.columns:
            medal_counts[medal] = 0
    medal_counts = medal_counts.reset_index()
    df = medal_counts

# Page config
st.set_page_config(page_title="Olympics Dashboard", layout="wide", page_icon="🏆")

# Apply custom theme
st.markdown("""
    <style>
        .main {
            background-color: #1e1e2f;
            color: #f0f0f0;
        }
        .stApp {
            background-color: #1e1e2f;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #e5c07b;
        }
        .css-1d391kg, .css-1v3fvcr {
            color: #c678dd;
        }
    </style>
""", unsafe_allow_html=True)

# Load default historical data
@st.cache_data
def load_default_historical_data():
    return df

# Initialize historical data if not already loaded
if 'historical_df' not in st.session_state:
    st.session_state['historical_df'] = load_default_historical_data()

# Display Logo
st.title("🏆 Olympics Dashboard")

# Sidebar navigation
menu = st.sidebar.radio("Navigation", [
    "Live Medal Tally",
    "Event Schedule",
    "Countdown to Next Event",
    "Event Highlights",
    "World Medal Map",
    "Top 10 Countries",
    "Country Medal Trend",
    "Predict Future Medals",
    "Country Pie Chart",
    "Compare Two Countries (Bar)",
    "Compare Two Countries (Radar)",
    "Predict Multiple Countries"
])

# Views
import time
import plotly.express as px
from datetime import datetime, timedelta
from dateutil import tz

if menu == "Live Medal Tally":
    st.subheader("📊 Live Medal Tally")
    live_df = fetch_medal_tally()
    if live_df is not None:
        st.dataframe(live_df, use_container_width=True)

elif menu == "Event Schedule":
    st.subheader("📅 Event Schedule")
    event_df = fetch_event_schedule()

    if event_df is not None and not event_df.empty:
        event_df['Date'] = pd.to_datetime(event_df['Date'], errors='coerce')
        event_df['Start Time'] = pd.to_datetime(event_df['Start Time'], errors='coerce', utc=True)
        event_df['End Time'] = pd.to_datetime(event_df['End Time'], errors='coerce', utc=True)
        local_zone = tz.tzlocal()
        event_df['Start Time'] = event_df['Start Time'].dt.tz_convert(local_zone)
        event_df['End Time'] = event_df['End Time'].dt.tz_convert(local_zone)
        event_df = event_df.sort_values("Start Time")
        st.dataframe(event_df[['Date', 'Discipline', 'Event', 'Venue', 'Start Time', 'End Time']], use_container_width=True)
    else:
        st.warning("No upcoming event schedule available.")

elif menu == "Countdown to Next Event":
    st.subheader("⏳ Countdown to Next Olympic Event")
    event_df = fetch_event_schedule()
    if event_df is not None and not event_df.empty:
        event_df['Start Time'] = pd.to_datetime(event_df['Start Time'], utc=True).dt.tz_convert(tz.tzlocal())
        now = datetime.now(tz.tzlocal())
        future_events = event_df[event_df['Start Time'] > now].sort_values('Start Time')
        if not future_events.empty:
            next_event = future_events.iloc[0]
            countdown_target = next_event['Start Time']
            st.markdown(f"**Next Event:** {next_event['Event']} ({next_event['Discipline']})")
            st.markdown(f"**Venue:** {next_event['Venue']}")
            st.markdown(f"**Start Time:** {countdown_target.strftime('%Y-%m-%d %H:%M:%S')}")
            countdown_placeholder = st.empty()
            while True:
                time_left = countdown_target - datetime.now()
                if time_left.total_seconds() <= 0:
                    countdown_placeholder.markdown("## 🟢 Event is Live!")
                    break
                countdown_str = str(time_left).split('.')[0]
                countdown_placeholder.markdown(f"## ⏱ Time Remaining: {countdown_str}")
                time.sleep(1)
        else:
            st.info("No upcoming events found.")

elif menu == "Event Highlights":
    st.subheader("🎯 Event Highlights")
    event_df = fetch_event_schedule()
    if event_df is not None:
        event_df['Date'] = pd.to_datetime(event_df['Date'])
        today = datetime.now().date()
        recent_events = event_df[event_df['Date'].dt.date == today]
        if not recent_events.empty:
            st.write("### Today's Events:")
            st.dataframe(recent_events, use_container_width=True)
        else:
            st.info("No highlights available for today.")

elif menu == "World Medal Map":
    st.subheader("🌍 World Medal Map")
    medal_type = st.radio("Choose Medal Data Source", ["Historical", "Live"], horizontal=True)
    if medal_type == "Historical":
        df = st.session_state['historical_df']
        if df is not None:
            country_totals = df.groupby('NOC')[['Gold', 'Silver', 'Bronze']].sum()
            country_totals['Total'] = country_totals.sum(axis=1)
            country_totals = country_totals.reset_index()
            noc_map = pd.read_csv("data/noc_regions.csv")
            merged = pd.merge(country_totals, noc_map, on="NOC", how="left")
            color_scale = [
                [0.0, "rgb(211, 211, 211)"],
                [0.2, "rgb(95, 15, 64)"],
                [0.4, "rgb(5, 140, 66)"],
                [0.6, "rgb(206, 212, 218)"],
                [0.8, "rgb(0, 166, 251)"],
                [1.0, "rgb(3, 4, 94)"]
            ]
            fig = px.choropleth(
                merged,
                locations="region",
                locationmode="country names",
                color="Total",
                hover_name="region",
                color_continuous_scale=color_scale,
                title="Total Historical Medals by Country"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        live_df = fetch_medal_tally()
        if live_df is not None:
            color_scale = [
                [0.0, "rgb(255, 255, 217)"],
                [0.2, "rgb(237, 248, 177)"],
                [0.4, "rgb(199, 233, 180)"],
                [0.6, "rgb(127, 205, 187)"],
                [0.8, "rgb(65, 182, 196)"],
                [1.0, "rgb(34, 94, 168)"]
            ]
            fig = px.choropleth(
                live_df,
                locations="Country",
                locationmode="country names",
                color="Total",
                hover_name="Country",
                color_continuous_scale=color_scale,
                title="Live Medal Tally by Country"
            )
            st.plotly_chart(fig, use_container_width=True)
    st.subheader("📅 Event Schedule")
    event_df = fetch_event_schedule()
    if event_df is not None:
        st.dataframe(event_df, use_container_width=True)

elif menu == "Top 10 Countries":
    st.subheader("🏆 Top 10 Countries (Historical)")
    if st.session_state['historical_df'] is not None:
        plot_interactive_medals(st.session_state['historical_df'])
    else:
        st.warning("Historical data not loaded.")

elif menu == "Country Medal Trend":
    st.subheader("📈 Medal Trend by Country")
    code = st.text_input("Enter Country NOC Code (e.g., USA, IND):").upper()
    if code and st.session_state['historical_df'] is not None:
        data = get_country_medal_counts(st.session_state['historical_df'], code)
        plot_country_medal_trend(data, code)

elif menu == "Predict Future Medals":
    st.subheader("🔮 Predict Future Medals")
    code = st.text_input("Enter Country NOC Code:").upper()
    if code and st.session_state['historical_df'] is not None:
        data = get_country_medal_counts(st.session_state['historical_df'], code)
        predict_future_medals(data, code)

elif menu == "Country Pie Chart":
    st.subheader("🥇 Medal Distribution Pie Chart")
    code = st.text_input("Enter Country NOC Code:").upper()
    if code and st.session_state['historical_df'] is not None:
        plot_country_pie(st.session_state['historical_df'], code)

elif menu == "Compare Two Countries (Bar)":
    st.subheader("🇨🇳🇺🇸 Compare Countries - Bar Chart")
    c1 = st.text_input("Country 1 NOC Code:").upper()
    c2 = st.text_input("Country 2 NOC Code:").upper()
    if c1 and c2 and st.session_state['historical_df'] is not None:
        compare_two_countries(st.session_state['historical_df'], c1, c2)

elif menu == "Compare Two Countries (Radar)":
    st.subheader("📡 Compare Countries - Radar Chart")
    c1 = st.text_input("Country 1 NOC Code:").upper()
    c2 = st.text_input("Country 2 NOC Code:").upper()
    if c1 and c2 and st.session_state['historical_df'] is not None:
        radar_compare_countries(st.session_state['historical_df'], c1, c2)

elif menu == "Predict Multiple Countries":
    st.subheader("📊 Predict Multiple Countries")
    codes = st.text_input("Enter comma-separated NOC codes (e.g., USA, IND, CHN):")
    if codes and st.session_state['historical_df'] is not None:
        country_list = [c.strip().upper() for c in codes.split(',') if c.strip()]
        predict_multiple_countries_shared_plot(st.session_state['historical_df'], country_list)
