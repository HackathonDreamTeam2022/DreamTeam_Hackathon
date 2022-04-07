import os
import pandas as pd
import numpy as np

from datetime import datetime


def load_historic_stock_data():
    """ Load historic stock prices dataset.

    """
    df = pd.read_csv("/Users/danjampro/Desktop/testdata/nasdaq.csv")

    # Pivot to get price as columns
    table = pd.pivot_table(df,
                           values='Open',
                           index=['Company'],
                           columns=['Date'],
                           aggfunc=np.sum).reset_index(level=[0])
    df = table.set_index("Company")

    # Sort prices by date
    dates = [datetime.strptime(d, "%d/%m/%Y") for d in df.columns]
    sorted_cols = [x for _, x in sorted(zip(dates, df.columns))]

    # Transpose to get company code as columns
    df = df.reindex(sorted_cols, axis=1).T

    return df, np.array([sorted(dates)])


def load_gdelt_events():
    """ Load historic GDELT events dataset.

    """

    dir = "/Users/danjampro/Desktop/testdata/gdelt"

    dfs = []

    for fname in os.listdir(dir):
        if fname.endswith(".csv"):
            dfs.append(pd.read_csv(os.path.join(dir, fname),
                                   names=("url",
                                          "article_date",
                                          "artcile_title",
                                          "mid",
                                          "gkg_name",
                                          "corpus_score",
                                          "sentiment_magnitude",
                                          "sentiment_score",
                                          "sentiment_salience")))

    df = pd.concat(dfs, ignore_index=False)

    # Merge to get tickers
    df_c = pd.read_csv("/Users/danjampro/Desktop/testdata/company_name_mappings_mid.csv")
    df = df.merge(df_c, on="mid", how="inner")

    return df


def calculate_profits(df_stocks, stock_dates, df_gdelt, decision_func):

    results = {}
    for i, series in df_gdelt.iterrows():  # Loop over GDELT events

        # Check if code is in stocks dataset
        code = series["Code"]
        if code not in df_stocks.columns:
            continue

        # Get price at date of event
        date = datetime.strptime(series["article_date"][:10], "%Y-%m-%d")
        idx = np.argmin(abs(date - stock_dates))
        price = df_stocks[code][idx]

        try:
            result = results[code]
        except KeyError:
            result = {"units": 0, "cost": 0}

        # Decide if we are going to buy or not
        if decision_func(series):
            result["units"] += 1
            result["cost"] += price

        results[code] = result

    # Calculate profit per code
    final_profits = {}
    for code, result in results.items():
        final_price = df_stocks[code][-1]
        final_value = result["units"] * final_price
        final_profits[code] = final_value - result["cost"]

    # Calculate total cost and profit
    final_profit = sum(final_profits.values())
    total_cost = sum([r["cost"] for r in results.values()])

    # Normalise profit by total cost
    # i.e. How much do you get back for what you put in
    normalised_profit = final_profit / total_cost

    return normalised_profit


def decision_func_0(series):
    return True


def decision_func_1(series):
    if series["sentiment_score"] < 0:
        return True


def decision_func_2(series):
    if (series["sentiment_score"] > 0.2) and (series["sentiment_salience"] > 0.5):
        return True


if __name__ == "__main__":

    df_stocks, stock_dates = load_historic_stock_data()
    df_gdelt = load_gdelt_events()

    final_profit0 = calculate_profits(df_stocks, stock_dates, df_gdelt, decision_func_0)
    final_profit1 = calculate_profits(df_stocks, stock_dates, df_gdelt, decision_func_1)
    final_profit2 = calculate_profits(df_stocks, stock_dates, df_gdelt, decision_func_2)

    print(final_profit0, final_profit1, final_profit2)
