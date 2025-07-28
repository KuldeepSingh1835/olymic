from live_data import fetch_medal_tally, fetch_event_schedule
from historical_data import load_historical_data, get_country_medal_counts
from visualization import (
    plot_interactive_medals,
    plot_country_medal_trend,
    plot_country_pie,
    compare_two_countries,
    radar_compare_countries
)
from prediction import predict_future_medals
from multi_country_prediction import predict_multiple_countries_shared_plot

def main_menu():
    historical_df = None
    while True:
        print("\n=== Olympics Dashboard ===")
        print("1. View Live Medal Tally")
        print("2. View Event Schedule")
        print("3. Load Historical Data")
        print("4. Plot Top 10 Countries (Historical)")
        print("5. Plot Country Medal Trend")
        print("6. Predict Future Medals for a Country")
        print("7. Country Pie Chart (Historical)")
        print("8. Compare Two Countries (Bar)")
        print("9. Compare Two Countries (Radar)")
        print("10. Predict Multiple Countries (Shared Plot)")
        print("11. Exit")
        choice = input("Enter your choice (1-11): ").strip()

        if choice == '1':
            live_df = fetch_medal_tally()
            if live_df is not None:
                print(live_df.to_string(index=False))

        elif choice == '2':
            event_df = fetch_event_schedule()
            if event_df is not None:
                print(event_df.to_string(index=False))

        elif choice == '3':
            filepath = input("Enter path to historical dataset CSV: ").strip()
            try:
                historical_df = load_historical_data(filepath)
                print("Historical data loaded successfully.")
            except Exception as e:
                print(f"Error loading data: {e}")

        elif choice == '4':
            if historical_df is not None:
                plot_interactive_medals(historical_df)
            else:
                print("Please load historical data first.")

        elif choice == '5':
            if historical_df is not None:
                country_code = input("Enter country NOC code (e.g., USA, IND): ").strip().upper()
                medal_counts = get_country_medal_counts(historical_df, country_code)
                plot_country_medal_trend(medal_counts, country_code)
            else:
                print("Please load historical data first.")

        elif choice == '6':
            if historical_df is not None:
                country_code = input("Enter country NOC code (e.g., USA, IND): ").strip().upper()
                medal_counts = get_country_medal_counts(historical_df, country_code)
                predict_future_medals(medal_counts, country_code)
            else:
                print("Please load historical data first.")

        elif choice == '7':
            if historical_df is not None:
                country_code = input("Enter country NOC code (e.g., USA, IND): ").strip().upper()
                plot_country_pie(historical_df, country_code)
            else:
                print("Please load historical data first.")

        elif choice == '8':
            if historical_df is not None:
                c1 = input("Enter first country NOC code: ").strip().upper()
                c2 = input("Enter second country NOC code: ").strip().upper()
                compare_two_countries(historical_df, c1, c2)
            else:
                print("Please load historical data first.")

        elif choice == '9':
            if historical_df is not None:
                c1 = input("Enter first country NOC code: ").strip().upper()
                c2 = input("Enter second country NOC code: ").strip().upper()
                radar_compare_countries(historical_df, c1, c2)
            else:
                print("Please load historical data first.")

        elif choice == '10':
            if historical_df is not None:
                codes = input("Enter comma-separated NOC codes (e.g., USA, IND, CHN): ").strip().upper().split(',')
                try:
                    degree = int(input("Enter polynomial degree (e.g., 2): ").strip())
                except ValueError:
                    degree = 2
                    print("Invalid input. Using default degree = 2.")
                predict_multiple_countries_shared_plot(historical_df, [c.strip() for c in codes], degree)
            else:
                print("Please load historical data first.")

        elif choice == '11':
            print("Exiting the dashboard. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 11.")

if __name__ == "__main__":
    main_menu()
