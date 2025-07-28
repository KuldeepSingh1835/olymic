# data_loader.py

import pandas as pd
import streamlit as st

@st.cache_data
def load_athlete_data():
    file_id = '1JNNrACCcGZrNC86R5yEu_2UrJSsP9kfn'
    url = f'https://drive.google.com/uc?id={file_id}'
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error loading data from Google Drive: {e}")
        return None
