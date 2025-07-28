import requests
import pandas as pd

BASE_URL = "https://apis.codante.io/olympic-games"

def fetch_medal_tally():
    try:
        response = requests.get(f"{BASE_URL}/countries")
        response.raise_for_status()
        data = response.json().get('data', [])
        df = pd.DataFrame(data)
        if df.empty:
            print("No medal data available.")
            return None
        df = df[['name', 'gold_medals', 'silver_medals', 'bronze_medals', 'total_medals', 'rank']]
        df.columns = ['Country', 'Gold', 'Silver', 'Bronze', 'Total', 'Rank']
        df = df.sort_values(by='Rank')
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching medal tally: {e}")
        return None

def fetch_event_schedule():
    try:
        response = requests.get(f"{BASE_URL}/events")
        response.raise_for_status()
        data = response.json().get('data', [])
        if not data:
            print("No event data available.")
            return None
        df = pd.DataFrame(data)
        df = df[['day', 'discipline_name', 'event_name', 'venue_name', 'start_date', 'end_date']]
        df.columns = ['Date', 'Discipline', 'Event', 'Venue', 'Start Time', 'End Time']
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching event schedule: {e}")
        return None
