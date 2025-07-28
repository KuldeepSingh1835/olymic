import pandas as pd

def load_historical_data(filepath):
    df = pd.read_csv(filepath)
    df = df[df['Medal'].notna()]
    df['Gold'] = df['Medal'] == 'Gold'
    df['Silver'] = df['Medal'] == 'Silver'
    df['Bronze'] = df['Medal'] == 'Bronze'
    df['Gold'] = df['Gold'].astype(int)
    df['Silver'] = df['Silver'].astype(int)
    df['Bronze'] = df['Bronze'].astype(int)
    return df

def get_country_medal_counts(df, country_code):
    country_data = df[df['NOC'] == country_code]
    medal_counts = country_data.groupby('Year')[['Gold', 'Silver', 'Bronze']].sum()
    medal_counts['Total'] = medal_counts.sum(axis=1)
    medal_counts = medal_counts.reset_index()
    return medal_counts
