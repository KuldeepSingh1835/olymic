from prophet import Prophet
import pandas as pd
import plotly.graph_objects as go
from historical_data import get_country_medal_counts

def predict_future_medals(medal_counts, country_code):
    if medal_counts is None or medal_counts.empty:
        print(f"No data available for {country_code}.")
        return

    df = medal_counts[['Year', 'Total']].rename(columns={'Year': 'ds', 'Total': 'y'})
    df['ds'] = pd.to_datetime(df['ds'], format='%Y')

    if len(df) < 2:
        print(f"Not enough data to predict for {country_code}.")
        return

    model = Prophet()
    model.fit(df)

    next_year = df['ds'].dt.year.max() + 4
    future = pd.date_range(start=df['ds'].max(), periods=2, freq='4YS')
    forecast = model.predict(pd.DataFrame({'ds': future}))

    # Convert predictions and bounds to integers
    predicted_next = max(0, int(forecast.iloc[-1]['yhat']))
    yhat_upper = int(forecast.iloc[-1]['yhat_upper'])
    yhat_lower = int(forecast.iloc[-1]['yhat_lower'])

    # Plotting
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], mode='lines+markers', name='Historical'))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'].astype(int), mode='lines', name='Prediction'))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'].astype(int), mode='lines', name='Upper Bound', line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'].astype(int), mode='lines', name='Lower Bound', line=dict(dash='dot')))

    fig.update_layout(title=f"{country_code} Medal Forecast with Prophet",
                      xaxis_title="Year",
                      yaxis_title="Total Medals")
    fig.show()

    print(f"\nProphet Prediction for {country_code} in {next_year}: {predicted_next} medals")
    print(f"Upper Bound: {yhat_upper} medals")
    print(f"Lower Bound: {yhat_lower} medals")


def predict_multiple_countries_shared_plot(historical_df, country_codes):
    fig = go.Figure()
    future_preds = []

    for code in country_codes:
        medal_counts = get_country_medal_counts(historical_df, code)
        if medal_counts is None or medal_counts.empty:
            print(f"No data available for {code}.")
            continue

        df = medal_counts[['Year', 'Total']].rename(columns={'Year': 'ds', 'Total': 'y'})
        df['ds'] = pd.to_datetime(df['ds'], format='%Y')

        if len(df) < 2:
            print(f"Not enough data to predict for {code}.")
            continue

        model = Prophet()
        model.fit(df)

        next_year = df['ds'].dt.year.max() + 4
        future = pd.date_range(start=df['ds'].max(), periods=2, freq='4YS')
        forecast = model.predict(pd.DataFrame({'ds': future}))
        predicted_next = max(0, int(forecast.iloc[-1]['yhat']))

        fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], mode='lines+markers', name=f'{code} Historical'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name=f'{code} Prediction'))

        future_preds.append((code, predicted_next))

    fig.update_layout(title="Prophet Medal Predictions for Multiple Countries",
                      xaxis_title="Year",
                      yaxis_title="Total Medals",
                      showlegend=True)
    fig.show()

    print("\nProphet Medal Predictions:")
    for code, val in future_preds:
        print(f"{code}: {val} medals")
