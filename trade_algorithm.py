# Description: Dual moving average crossover to determine when to buy and sell stock.
# TradeAlgorithm v1.0

# Import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import easygui as gui
import adjustText
import calendar
from datetime import datetime
from pandas_datareader import data as web


def create_input_dialog():
    gui_text = "Enter the following details"
    gui_title = "TradeAlgorithm v1.0"
    gui_input_list = ["Stock Symbol", "Initial Date (YYYYmmdd)", "End Date (YYYYmmdd)"]
    gui_default_list = ["AAPL", "20150101", datetime.today().strftime("%Y%m%d")]
    gui_output = gui.multenterbox(gui_text, gui_title, gui_input_list, gui_default_list)
    return gui_output

# Program body
def trade_algorithm():
    # Set plot style
    plt.style.use("fivethirtyeight")

    # Input symbol and date dialog
    output = create_input_dialog()

    # Set stock symbol
    symbol = output[0]

    # Set initial and end date
    initial_date = output[1]
    end_date = output[2]

    # Create time window string for x axis
    time_window_str = (calendar.month_abbr[int(initial_date[4:6].lstrip('0'))] + " " + initial_date[-2:] + ", " + initial_date[0:4] +
                       " - " +
                       calendar.month_abbr[int(end_date[4:6].lstrip('0'))] + " " + end_date[-2:] + ", " + end_date[0:4])

    # Create dataframe
    df = pd.DataFrame()

    # Retrieve stock price in range of initial and end date
    df["Adj Close Price"] = web.DataReader(symbol, data_source="yahoo", start=initial_date, end=end_date)["Adj Close"]
    my_stock = df

    # Create Date column with the value from index
    my_stock["DateColumn"] = df.index

    # Create a simple moving average with a 30 day window
    SMA30 = pd.DataFrame()
    SMA30["Adj Close Price"] = my_stock["Adj Close Price"].rolling(window=30).mean()

    # Create a simple moving average with a 100 day window
    SMA100 = pd.DataFrame()
    SMA100["Adj Close Price"] = my_stock["Adj Close Price"].rolling(window=100).mean()

    # Create a new dataframe and store all the data
    data = pd.DataFrame()

    data["Date"] = my_stock["DateColumn"]
    data["Price"] = my_stock["Adj Close Price"]
    data["SMA30"] = SMA30["Adj Close Price"]
    data["SMA100"] = SMA100["Adj Close Price"]

    # Create a function to signal when to buy and sell the stock
    def buy_sell(data):
        sig_price_buy = []
        sig_price_sell = []

        cross = -1

        for i in range(len(data)):
            if data["SMA30"][i] > data["SMA100"][i]:
                if cross != 1:
                    sig_price_buy.append(data["Price"][i])
                    sig_price_sell.append(np.nan)
                    cross = 1
                else:
                    sig_price_buy.append(np.nan)
                    sig_price_sell.append(np.nan)
            elif data["SMA30"][i] < data["SMA100"][i]:
                if cross != 0:
                    sig_price_buy.append(np.nan)
                    sig_price_sell.append(data["Price"][i])
                    cross = 0
                else:
                    sig_price_buy.append(np.nan)
                    sig_price_sell.append(np.nan)
            else:
                sig_price_buy.append(np.nan)
                sig_price_sell.append(np.nan)

        return sig_price_buy, sig_price_sell

    # Store the buy and sell data into a variable
    buy_sell = buy_sell(data)
    data["Buy_Signal_Price"] = buy_sell[0]
    data["Sell_Signal_Price"] = buy_sell[1]

    # Visualize the data and the strategy to buy and sell the stock
    max_price = data["Price"].max()

    plt.figure(figsize=(13, 8), num='Trade Algorithm v1.0')
    plt.plot(data["Price"], label=symbol, alpha=0.35)
    plt.plot(data["SMA30"], label = "SMA30", alpha=0.35)
    plt.plot(data["SMA100"], label = "SMA100", alpha=0.35)
    plt.scatter(data.index, data["Buy_Signal_Price"], label="Buy", marker='^', color="green")
    plt.scatter(data.index, data["Sell_Signal_Price"], label="Sell", marker='v', color="red")
    plt.title(symbol + " Adj. Close Price History with Buy & Sell Signals")
    plt.xlabel(time_window_str)
    plt.ylabel("Adj. Close Price USD ($)")
    plt.legend(loc="upper right")

    # Show labels
    # To Do: switch annotate() to text() and use adjustText lib to avoid overlap
    # To Do: add arrow from buy to sell
    # To Do: add gain and loss (percentage) per trade [ (sell signal value - buy signal value) * 100 ]
    for row in range(len(data)):
        if not pd.isnull(data["Buy_Signal_Price"][row]):
            y_adjust = int(max_price - 20 - data["Price"][row])
            plt.annotate(round(data["Price"][row],2), xy=(data["Date"][row], int(data["Price"][row])+y_adjust), color="green", size="10")
        if not pd.isnull(data["Sell_Signal_Price"][row]):
            y_adjust = int(max_price - 25 - data["Price"][row])
            plt.annotate(round(data["Price"][row],2), xy=(data["Date"][row], int(data["Price"][row])+y_adjust), color="red", size="10")
    plt.show()


# Call body
if __name__ == '__main__':
    trade_algorithm()