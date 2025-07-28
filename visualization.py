import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.colors import MEDAL_COLORS, COUNTRY_COLORS

def plot_interactive_medals(df):
    if df is None or df.empty:
        print("No data available for plotting.")
        return

    medal_counts = df.groupby('NOC')[['Gold', 'Silver', 'Bronze']].sum()
    medal_counts['Total'] = medal_counts.sum(axis=1)
    top_countries = medal_counts.sort_values(by='Total', ascending=False).head(10).reset_index()

    melted_df = top_countries.melt(id_vars='NOC', value_vars=['Gold', 'Silver', 'Bronze'],
                                   var_name='Medal', value_name='Count')

    fig = px.bar(melted_df, x='NOC', y='Count', color='Medal', barmode='group',
                 color_discrete_map=MEDAL_COLORS,
                 title='Top 10 Countries by Medal Count')
    fig.show()

def plot_country_medal_trend(medal_counts, country_code):
    if medal_counts is None or medal_counts.empty:
        print(f"No data available for {country_code}.")
        return

    line_color = COUNTRY_COLORS.get(country_code, None)
    fig = px.line(medal_counts, x='Year', y='Total', markers=True,
                  title=f'{country_code} Medal Trend Over Years')
    if line_color:
        fig.update_traces(line=dict(color=line_color, width=3))
    else:
        fig.update_traces(line=dict(width=3))
    fig.show()

def plot_country_pie(df, country_code):
    if df is None or df.empty or country_code not in df['NOC'].unique():
        print(f"No data available for {country_code}.")
        return

    country_data = df[df['NOC'] == country_code][['Gold', 'Silver', 'Bronze']].sum()
    fig = px.pie(values=country_data.values, names=country_data.index,
                 title=f"{country_code} Medal Distribution",
                 color=country_data.index,
                 color_discrete_map=MEDAL_COLORS)
    fig.show()

def compare_two_countries(df, country1, country2):
    if df is None or df.empty:
        print("No data available.")
        return

    countries = [country1, country2]
    if any(code not in df['NOC'].unique() for code in countries):
        print("One or both country codes not found.")
        return

    data = df[df['NOC'].isin(countries)].groupby('NOC')[['Gold', 'Silver', 'Bronze']].sum()
    data = data.reset_index()

    fig = go.Figure()

    for medal in ['Gold', 'Silver', 'Bronze']:
        fig.add_trace(go.Bar(
            x=data['NOC'],
            y=data[medal],
            name=medal,
            marker_color=MEDAL_COLORS[medal]
        ))

    fig.update_layout(
        title='Country Comparison by Medal Type',
        barmode='group',
        xaxis_title='Country',
        yaxis_title='Medals'
    )
    fig.show()

def radar_compare_countries(df, country1, country2):
    if df is None or df.empty:
        print("No data available.")
        return

    countries = [country1, country2]
    if any(code not in df['NOC'].unique() for code in countries):
        print("One or both countries not found.")
        return

    medal_sums = df[df['NOC'].isin(countries)].groupby('NOC')[['Gold', 'Silver', 'Bronze']].sum()
    categories = ['Gold', 'Silver', 'Bronze']

    fig = go.Figure()

    for country in countries:
        values = medal_sums.loc[country].values.tolist()
        values += values[:1]  # to close the radar chart
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=country,
            line=dict(color=COUNTRY_COLORS.get(country, None))
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        title="Country Comparison Radar Chart",
        showlegend=True
    )
    fig.show()
