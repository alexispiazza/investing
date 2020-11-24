# Description: Dual moving average crossover to determine when to buy and sell stock.
# TradeAlgorithm v1.0
#
# To Do:
# 1. Change buy and sell labels on the top to a more friendly visual
# 2. Handle exception in case of less than 1 signal


# Import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import easygui as gui
import adjustText
import calendar
import datetime
from pandas_datareader import data as web


def create_input_dialog():
    gui_text = "Enter the stock symbol and dates"
    gui_title = "TradeAlgorithm v1.0"
    gui_input_list = ["Stock Symbol", "Initial Date (YYYYmmdd)", "End Date (YYYYmmdd)"]
    gui_default_list = ["AAPL", "20150101", datetime.datetime.today().strftime("%Y%m%d")]
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

    # Create a function to calculate gain and loss for each trade
    def calculate_gain_loss(data):
        global buy_signals
        global sell_signals

        buy_signals = []
        sell_signals = []
        gain_loss = []

        global first_is_buy
        first_is_buy = True

        min_date_buy = data["Buy_Signal_Price"].first_valid_index()
        min_date_sell = data["Sell_Signal_Price"].first_valid_index()

        if min_date_buy > min_date_sell:
            first_is_buy = False

        for row in range(len(data)):
            if not pd.isnull(data["Buy_Signal_Price"][row]):
                buy_signals.append(round(data["Buy_Signal_Price"][row], 2))
            if not pd.isnull(data["Sell_Signal_Price"][row]):
                sell_signals.append(round(data["Sell_Signal_Price"][row], 2))

        buy_len = len(buy_signals)
        sell_len = len(sell_signals)

        if buy_len <= sell_len:
            gain_loss_len = buy_len
        else:
            gain_loss_len = sell_len

        if first_is_buy:
            for i in range(gain_loss_len):
                gain_loss.append(round((sell_signals[i] / buy_signals[i] - 1) * 100, 2))
        else:
            for i in range(gain_loss_len - 1):
                gain_loss.append(round((sell_signals[i + 1] / buy_signals[i] - 1) * 100, 2))
        return gain_loss

    # Store the buy and sell data into a variable
    buy_sell = buy_sell(data)
    data["Buy_Signal_Price"] = buy_sell[0]
    data["Sell_Signal_Price"] = buy_sell[1]

    # Store the gains and losses into a variable
    gain_loss = calculate_gain_loss(data)

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
    buy_signal_list = []
    sell_signal_list = []

    for row in range(len(data)):
        if not pd.isnull(data["Buy_Signal_Price"][row]):
            plt.annotate(round(data["Price"][row], 2), xy=(data["Date"][row], max_price/100*90),
                         color="green", size="10")
            buy_signal_list.append([data["Date"][row], data["Price"][row]])

        if not pd.isnull(data["Sell_Signal_Price"][row]):
            plt.annotate(round(data["Price"][row], 2), xy=(data["Date"][row], max_price/100*85),
                         color="red", size="10")
            sell_signal_list.append([data["Date"][row], data["Price"][row]])

    # Add arrow connecting buy to sell points
    if first_is_buy:
        color = ""
        if len(buy_signal_list) == len(sell_signal_list):
            for i in range(len(buy_signal_list)):
                if(sell_signal_list[i][1] - buy_signal_list[i][1]) > 0:
                    color = "green"
                else:
                    color = "red"
                plt.arrow(buy_signal_list[i][0],
                          buy_signal_list[i][1],
                          (sell_signal_list[i][0] - buy_signal_list[i][0]).days,
                          (sell_signal_list[i][1] - buy_signal_list[i][1]),
                          color=color, width=0.2, head_width=1, head_length=5)
                plt.text(
                    buy_signal_list[i][0] + datetime.timedelta((sell_signal_list[i][0] - buy_signal_list[i][0]).days / 2),
                    (sell_signal_list[i][1] + buy_signal_list[i][1]) / 2,
                    str(gain_loss[i]) + "%",
                    size=10,
                    color=color)
        else:
            for i in range(len(buy_signal_list)-1):
                if (sell_signal_list[i][1] - buy_signal_list[i][1]) > 0:
                    color = "green"
                else:
                    color = "red"
                plt.arrow(buy_signal_list[i][0],
                          buy_signal_list[i][1],
                          (sell_signal_list[i][0] - buy_signal_list[i][0]).days,
                          (sell_signal_list[i][1] - buy_signal_list[i][1]),
                          color=color, width=0.2, head_width=1, head_length=5)
                plt.text(buy_signal_list[i][0] + datetime.timedelta((sell_signal_list[i][0] - buy_signal_list[i][0]).days / 2),
                         (sell_signal_list[i][1] + buy_signal_list[i][1]) / 2,
                         str(gain_loss[i]) + "%",
                         size=10,
                         color=color,
                         )

    else:
        if len(buy_signal_list) == len(sell_signal_list):
            for i in range(len(buy_signal_list)):
                if (sell_signal_list[i+1][1] - buy_signal_list[i][1]) > 0:
                    color = "green"
                else:
                    color = "red"
                plt.arrow(buy_signal_list[i][0],
                          buy_signal_list[i][1],
                          (sell_signal_list[i+1][0] - buy_signal_list[i][0]).days,
                          (sell_signal_list[i+1][1] - buy_signal_list[i][1]),
                          color=color, width=0.2, head_width=1, head_length=5)
                plt.text(
                    buy_signal_list[i][0] + datetime.timedelta((sell_signal_list[i+1][0] - buy_signal_list[i][0]).days / 2),
                    (sell_signal_list[i+1][1] + buy_signal_list[i][1]) / 2,
                    str(gain_loss[i]) + "%",
                    size=10,
                    color=color)
        else:
            for i in range(len(buy_signal_list)):
                if (sell_signal_list[i+1][1] - buy_signal_list[i][1]) > 0:
                    color = "green"
                else:
                    color = "red"
            for i in range(len(buy_signal_list)-1):
                plt.arrow(buy_signal_list[i][0],
                          buy_signal_list[i][1],
                          (sell_signal_list[i+1][0] - buy_signal_list[i][0]).days,
                          (sell_signal_list[i+1][1] - buy_signal_list[i][1]),
                          color=color, width=0.2, head_width=1, head_length=5)
                plt.text(
                    buy_signal_list[i][0] + datetime.timedelta((sell_signal_list[i+1][0] - buy_signal_list[i][0]).days / 2),
                    (sell_signal_list[i+1][1] + buy_signal_list[i][1]) / 2,
                    str(gain_loss[i]) + "%",
                    size=10,
                    color=color)

    plt.show()


# Call body
if __name__ == '__main__':
    trade_algorithm()
