# -*- coding: utf-8 -*-
import json
import csv

import pandas as pd
import pathlib
import requests
import datetime as dt
from os import environ

import dash_core_components as dcc
import dash_html_components as html
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from sqlalchemy import create_engine
import pandas_datareader as pdr
import numpy as np


db_URI = environ.get('DATABASE_URL')
engine = create_engine(db_URI)

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
# Loading historical tick data
currency_pair_data = {
    "EURUSD": pd.read_csv(
        DATA_PATH.joinpath("EURUSD.csv"), index_col=1, parse_dates=["Date"]
    ),
    "USDJPY": pd.read_csv(
        DATA_PATH.joinpath("USDJPY.csv"), index_col=1, parse_dates=["Date"]
    ),
    "GBPUSD": pd.read_csv(
        DATA_PATH.joinpath("GBPUSD.csv"), index_col=1, parse_dates=["Date"]
    ),
    "USDCHF": pd.read_csv(
        DATA_PATH.joinpath("USDCHF.csv"), index_col=1, parse_dates=["Date"]
    ),
}
# symbol_mapping=pd.read_csv(
#     DATA_PATH.joinpath("mapeo_acciones.csv"))

headers_ppi = {
    "Content-Type": "application/json",
    "AuthorizedClient": "321321321",
    "ClientKey": "pp123456",
    "Referer": "https://api.portfoliopersonal.com/Content/html/proxy.html",
    "Sec-Fetch-Mode": "cors",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
}

# Currency pairs
# currencies = ["EURUSD", "USDCHF", "USDJPY", "GBPUSD"]
# stocks=pd.read_sql('''SELECT symbol FROM dg_stocks.orders
# where  status='Open'  ''',
#                  con=engine)['symbol'].unique()
stocks=pd.read_sql("""SELECT symbol FROM follow where follow=True """,
                 con=engine)['symbol'].values
#stock2s=requests.get('http://localhost:5000/rest/follow').json()
#print(stock2s)
# API Requests for news div
news_requests = requests.get(
    "https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey=da8e2e705b914f9f86ed2e9692e66012"
)


def symbol_mapping(symbol):
    return pd.read_sql("""SELECT * FROM follow where follow=True and symbol='{}' """.format(symbol),
                     con=engine)

# API Call to update news
def update_news():
    json_data = news_requests.json()["articles"]
    df = pd.DataFrame(json_data)
    df = pd.DataFrame(df[["title", "url"]])
    max_rows = 10
    return html.Div(
        children=[
            html.P(className="p-news", children="Headlines"),
            html.P(
                className="p-news float-right",
                children="Last update : "
                + dt.datetime.now().strftime("%H:%M:%S"),
            ),
            html.Table(
                className="table-news",
                children=[
                    html.Tr(
                        children=[
                            html.Td(
                                children=[
                                    html.A(
                                        className="td-link",
                                        children=df.iloc[i]["title"],
                                        href=df.iloc[i]["url"],
                                        target="_blank",
                                    )
                                ]
                            )
                        ]
                    )
                    for i in range(min(len(df), max_rows))
                ],
            ),
        ]
    )


# Returns dataset for currency pair with nearest datetime to current time
def first_ask_bid(currency_pair, t):
    # t = t.replace(year=2016, month=1, day=5)
    # items = currency_pair_data[currency_pair]
    # dates = items.index.to_pydatetime()
    # index = min(dates, key=lambda x: abs(x - t))
    # df_row = items.loc[index]
    # int_index = items.index.get_loc(index)
    # print([df_row, int_index])
    # return [df_row, int_index]  # returns dataset row and index of row
    yahoo_symbol=symbol_mapping(currency_pair)['rava'].values[0]
    df=pdr.get_data_yahoo(yahoo_symbol, start=dt.datetime.now() - dt.timedelta(days=7), end=dt.datetime.now()).tail(1)[['High','Low']]
    df['stock']=currency_pair
    df=df.reset_index()
    return df.to_dict('records')



# Creates HTML Bid and Ask (Buy/Sell buttons)
def get_row(data):
    index = data[0]['Date']
    current_row = data[0]

    return html.Div(
        children=[
            # Summary
            html.Div(
                id=current_row['stock'] + "summary",
                className="row summary",
                n_clicks=0,
                children=[
                    html.Div(
                        id= current_row['stock']+ "row",
                        className="row",
                        children=[
                            html.P(
                                current_row['stock'],  # currency pair name
                                id=current_row['stock'],
                                className="three-col",
                            ),
                            html.P(
                                round(current_row['High'],5),  # Bid value
                                id=current_row['stock'] + "bid",
                                className="three-col",
                            ),
                            html.P(
                                round(current_row['Low'],5),  # Ask value
                                id=current_row['stock'] + "ask",
                                className="three-col",
                            ),
                            html.Div(
                                index,
                                id=current_row['stock']
                                + "index",  # we save index of row in hidden div
                                style={"display": "none"},
                            ),
                        ],
                    )
                ],
            ),
            # Contents
            html.Div(
                id=current_row['stock'] + "contents",
                className="row details",
                children=[
                    # Button for buy/sell modal
                    html.Div(
                        className="button-buy-sell-chart",
                        children=[
                            html.Button(
                                id=current_row['stock'] + "Buy",
                                children="Buy/Sell",
                                n_clicks=0,
                            )
                        ],
                    ),
                    # Button to display currency pair chart
                    html.Div(
                        className="button-buy-sell-chart-right",
                        children=[
                            html.Button(
                                id=current_row['stock'] + "Button_chart",
                                children="Chart",
                                n_clicks=0,
                            )
                        ],
                    ),
                ],
            ),
        ]
    )


# color of Bid & Ask rates
def get_color(a, b):
    if a=='--' or b=='--':
        return "white"
    if a == b:
        return "white"
    elif a > b:
        return "#45df7e"
    else:
        return "#da5657"


# Replace ask_bid row for currency pair with colored values
def replace_row(currency_pair, bid, ask):
    now=dt.datetime.now()
    hora=dt.datetime.now().hour
    week_day=dt.datetime.now().weekday()
    if hora >10 and hora<18 and week_day <6:
        ppi_symbol=symbol_mapping(currency_pair)['ppi'].values[0]
        response=requests.get('https://api.portfoliopersonal.com/api/Cotizaciones/Item/{}/LibroOfertas/3'.format(ppi_symbol), headers=headers_ppi)
        payload=response.json()['payload']   # if not the end of the dataset we retrieve next dataset row
        return [
                html.P(
                    currency_pair, id=currency_pair, className="three-col"  # currency pair name
                ),
                html.P(
                    payload['bids'][0]['precio'],  # Bid value
                    id=currency_pair + "bid",
                    className="three-col",
                    style={"color": get_color(payload['bids'][0]['precio'], bid)},
                ),
                html.P(
                    payload['offers'][0]['precio'],  # Ask value
                    className="three-col",
                    id=currency_pair + "ask",
                    style={"color": get_color(payload['offers'][0]['precio'], ask)},
                ),
                html.Div(
                     id=currency_pair + "index", style={"display": "none"}
                ),  # save index in hidden div
            ]
    else:
        return [
            html.P(
                currency_pair, id=currency_pair, className="three-col"  # currency pair name
            ),
            html.P(
                '--',  # Bid value
                id=currency_pair + "bid",
                className="three-col",
            ),
            html.P(
                '--',  # Ask value
                className="three-col",
                id=currency_pair + "ask",
            ),
            html.Div(
                 id=currency_pair + "index", style={"display": "none"}
            ),  # save index in hidden div
        ]
def old_replace_row(currency_pair, index, bid, ask):
    index = index + 1  # index of new data row
    new_row = (
        currency_pair_data[currency_pair].iloc[index]
        if index != len(currency_pair_data[currency_pair])
        else first_ask_bid(currency_pair, dt.datetime.now())
    )  # if not the end of the dataset we retrieve next dataset row

    return [
        html.P(
            currency_pair, id=currency_pair, className="three-col"  # currency pair name
        ),
        html.P(
            new_row[1].round(5),  # Bid value
            id=new_row[0] + "bid",
            className="three-col",
            style={"color": get_color(new_row[1], bid)},
        ),
        html.P(
            new_row[2].round(5),  # Ask value
            className="three-col",
            id=new_row[0] + "ask",
            style={"color": get_color(new_row[2], ask)},
        ),
        html.Div(
            index, id=currency_pair + "index", style={"display": "none"}
        ),  # save index in hidden div
    ]

# Display big numbers in readable format
def human_format(num):
    try:
        num = float(num)
        # If value is 0
        if num == 0:
            return 0
        # Else value is a number
        if num < 1000000:
            return num
        magnitude = int(math.log(num, 1000))
        mantissa = str(int(num / (1000 ** magnitude)))
        return mantissa + ["", "K", "M", "G", "T", "P"][magnitude]
    except:
        return num


# Returns Top cell bar for header area
def get_top_bar_cell(cellTitle, cellValue):
    return html.Div(
        className="two-col",
        children=[
            html.P(className="p-top-bar", children=cellTitle),
            html.P(id=cellTitle, className="display-none", children=cellValue),
            html.P(children=human_format(cellValue)),
        ],
    )


# Returns HTML Top Bar for app layout
def get_top_bar(
    balance=50000, equity=50000, margin=0, fm=50000, m_level="%", open_pl=0
):
    balance = pd.read_sql('''SELECT monto
from movements where moneda='p\'''',
                     con=engine)['monto'].sum()
    #print('balance:{}'.format(balance))
    return [
        get_top_bar_cell("Balance", balance),
        get_top_bar_cell("Equity", equity),
        get_top_bar_cell("Margin", margin),
        get_top_bar_cell("Free Margin", fm),
        get_top_bar_cell("Margin Level", m_level),
        get_top_bar_cell("Open P/L", open_pl),
    ]


####### STUDIES TRACES ######

# Moving average
def moving_average_trace(df, fig):
    df2 = df.rolling(window=5).mean()
    trace = go.Scatter(
        x=df2.index, y=df2["close"], mode="lines", showlegend=False, name="MA"
    )
    fig.append_trace(trace, 1, 1)  # plot in first row
    return fig


# Exponential moving average
def e_moving_average_trace(df, fig):
    df2 = df.rolling(window=20).mean()
    trace = go.Scatter(
        x=df2.index, y=df2["close"], mode="lines", showlegend=False, name="EMA"
    )
    fig.append_trace(trace, 1, 1)  # plot in first row
    return fig


# Bollinger Bands
def bollinger_trace(df, fig, window_size=10, num_of_std=5):
    price = df["close"]
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std * num_of_std)
    lower_band = rolling_mean - (rolling_std * num_of_std)

    trace = go.Scatter(
        x=df.index, y=upper_band, mode="lines", showlegend=False, name="BB_upper"
    )

    trace2 = go.Scatter(
        x=df.index, y=rolling_mean, mode="lines", showlegend=False, name="BB_mean"
    )

    trace3 = go.Scatter(
        x=df.index, y=lower_band, mode="lines", showlegend=False, name="BB_lower"
    )

    fig.append_trace(trace, 1, 1)  # plot in first row
    fig.append_trace(trace2, 1, 1)  # plot in first row
    fig.append_trace(trace3, 1, 1)  # plot in first row
    return fig


# Accumulation Distribution
def accumulation_trace(df):
    df["volume"] = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (
        df["high"] - df["low"]
    )
    trace = go.Scatter(
        x=df.index, y=df["volume"], mode="lines", showlegend=False, name="Accumulation"
    )
    return trace


# Commodity Channel Index
def cci_trace(df, ndays=5):
    TP = (df["high"] + df["low"] + df["close"]) / 3
    CCI = pd.Series(
        (TP - TP.rolling(window=10, center=False).mean())
        / (0.015 * TP.rolling(window=10, center=False).std()),
        name="cci",
    )
    trace = go.Scatter(x=df.index, y=CCI, mode="lines", showlegend=False, name="CCI")
    return trace


# Price Rate of Change
def roc_trace(df, ndays=5):
    N = df["close"].diff(ndays)
    D = df["close"].shift(ndays)
    ROC = pd.Series(N / D, name="roc")
    trace = go.Scatter(x=df.index, y=ROC, mode="lines", showlegend=False, name="ROC")
    return trace


# Stochastic oscillator %K
def stoc_trace(df):
    SOk = pd.Series((df["close"] - df["low"]) / (df["high"] - df["low"]), name="SO%k")
    trace = go.Scatter(x=df.index, y=SOk, mode="lines", showlegend=False, name="SO%k")
    return trace


# Momentum
def mom_trace(df, n=5):
    M = pd.Series(df["close"].diff(n), name="Momentum_" + str(n))
    trace = go.Scatter(x=df.index, y=M, mode="lines", showlegend=False, name="MOM")
    return trace


# Pivot points
def pp_trace(df, fig):
    PP = pd.Series((df["high"] + df["low"] + df["close"]) / 3)
    R1 = pd.Series(2 * PP - df["low"])
    S1 = pd.Series(2 * PP - df["high"])
    R2 = pd.Series(PP + df["high"] - df["low"])
    S2 = pd.Series(PP - df["high"] + df["low"])
    R3 = pd.Series(df["high"] + 2 * (PP - df["low"]))
    S3 = pd.Series(df["low"] - 2 * (df["high"] - PP))
    trace = go.Scatter(x=df.index, y=PP, mode="lines", showlegend=False, name="PP")
    trace1 = go.Scatter(x=df.index, y=R1, mode="lines", showlegend=False, name="R1")
    trace2 = go.Scatter(x=df.index, y=S1, mode="lines", showlegend=False, name="S1")
    trace3 = go.Scatter(x=df.index, y=R2, mode="lines", showlegend=False, name="R2")
    trace4 = go.Scatter(x=df.index, y=S2, mode="lines", showlegend=False, name="S2")
    trace5 = go.Scatter(x=df.index, y=R3, mode="lines", showlegend=False, name="R3")
    trace6 = go.Scatter(x=df.index, y=S3, mode="lines", showlegend=False, name="S3")
    fig.append_trace(trace, 1, 1)
    fig.append_trace(trace1, 1, 1)
    fig.append_trace(trace2, 1, 1)
    fig.append_trace(trace3, 1, 1)
    fig.append_trace(trace4, 1, 1)
    fig.append_trace(trace5, 1, 1)
    fig.append_trace(trace6, 1, 1)
    return fig


# MAIN CHART TRACES (STYLE tab)
def line_trace(df):
    trace = go.Scatter(
        x=df.index, y=df["Close"], mode="lines", showlegend=False, name="line"
    )
    return trace


def area_trace(df):
    trace = go.Scatter(
        x=df.index, y=df["Close"], showlegend=False, fill="toself", name="area"
    )
    return trace


def bar_trace(df):
    return go.Ohlc(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        increasing=dict(line=dict(color="#888888")),
        decreasing=dict(line=dict(color="#888888")),
        showlegend=False,
        name="bar",
    )


def colored_bar_trace(df):
    return go.Ohlc(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        showlegend=False,
        name="colored bar",
    )


def candlestick_trace(df):
    return go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        increasing=dict(line=dict(color="#00ff00")),
        decreasing=dict(line=dict(color="white")),
        showlegend=False,
        name="candlestick",
    )


# For buy/sell modal
def ask_modal_trace(currency_pair, index):
    #df = currency_pair_data[currency_pair].iloc[index - 10 : index]  # returns ten rows
    response=requests.get('https://api.portfoliopersonal.com/api/Cotizaciones/Item/10102/Intradiario', headers=headers_ppi)
    df=pd.DataFrame(response.json()['payload']).tail(10)[['ultOperado']]
    return go.Scatter(x=df.index, y=df["ultOperado"], mode="lines", showlegend=False)


# For buy/sell modal
def bid_modal_trace(currency_pair, index):
    # df = currency_pair_data[currency_pair].iloc[index - 10 : index]  # returns ten rows
    # return go.Scatter(x=df.index, y=df["Bid"], mode="lines", showlegend=False)
    response=requests.get('https://api.portfoliopersonal.com/api/Cotizaciones/Item/10102/Intradiario', headers=headers_ppi)
    df=pd.DataFrame(response.json()['payload']).tail(10)[['ultOperado']]
    return go.Scatter(x=df.index, y=df["ultOperado"], mode="lines", showlegend=False)


# returns modal figure for a currency pair
def get_modal_fig(currency_pair, index):
    fig = make_subplots(
        rows=2, shared_xaxes=True, shared_yaxes=False, cols=1, print_grid=False
    )

    #fig.append_trace(ask_modal_trace(currency_pair, index), 1, 1)
    #fig.append_trace(bid_modal_trace(currency_pair, index), 2, 1)

    fig["layout"]["autosize"] = True
    fig["layout"]["height"] = 375
    fig["layout"]["margin"] = {"t": 5, "l": 50, "b": 0, "r": 5}
    fig["layout"]["yaxis"]["showgrid"] = True
    fig["layout"]["yaxis"]["gridcolor"] = "#3E3F40"
    fig["layout"]["yaxis"]["gridwidth"] = 1
    fig["layout"].update(paper_bgcolor="#21252C", plot_bgcolor="#21252C")

    return fig


# Returns graph figure
def get_fig(currency_pair, ask, bid, type_trace, studies, period):
    # Get OHLC data
    # data_frame = currency_pair_data[currency_pair]
    # t = dt.datetime.now()
    # data = data_frame.loc[
    #     : t.strftime(
    #         "2016-01-05 %H:%M:%S"
    #     )  # all the data from the beginning until current time
    # ]
    # data_bid = data["Bid"]
    # response=requests.get('https://api.portfoliopersonal.com/api/Cotizaciones/Item/10102/Intradiario', headers=headers_ppi)
    # data_bid=pd.DataFrame(response.json()['payload'])
    # data_bid['Date'] = pd.to_datetime(data_bid['fechaCotizacion'])
    # data_bid = data_bid.set_index('Date')
    CSV_URL='https://www.rava.com/empresas/precioshistoricos.php?e={}&csv=1'.format('ALUA')
    with requests.Session() as s:
        download = s.get(CSV_URL)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        data_bid=pd.DataFrame(my_list[1:], columns=['Date','Open','Low','High','Close','Volume','openint'])
        data_bid['Date'] = pd.to_datetime(data_bid['Date'])
        data_bid = data_bid.set_index('Date')
    #df = data_bid.resample(period).ohlc()
    df = data_bid

    subplot_traces = [  # first row traces
        "accumulation_trace",
        "cci_trace",
        "roc_trace",
        "stoc_trace",
        "mom_trace",
    ]
    selected_subplots_studies = []
    selected_first_row_studies = []
    row = 1  # number of subplots

    if studies:
        for study in studies:
            if study in subplot_traces:
                row += 1  # increment number of rows only if the study needs a subplot
                selected_subplots_studies.append(study)
            else:
                selected_first_row_studies.append(study)

    fig = make_subplots(
        rows=row,
        shared_xaxes=True,
        shared_yaxes=True,
        cols=1,
        print_grid=False,
        vertical_spacing=0.12,
    )

    # Add main trace (style) to figure
    fig.append_trace(eval(type_trace)(df), 1, 1)

    # Add trace(s) on fig's first row
    for study in selected_first_row_studies:
        fig = eval(study)(df, fig)

    row = 1
    # Plot trace on new row
    for study in selected_subplots_studies:
        row += 1
        fig.append_trace(eval(study)(df), row, 1)

    fig["layout"][
        "uirevision"
    ] = "The User is always right"  # Ensures zoom on graph is the same on update
    fig["layout"]["margin"] = {"t": 50, "l": 50, "b": 50, "r": 25}
    fig["layout"]["autosize"] = True
    fig["layout"]["height"] = 400
    fig["layout"]["xaxis"]["rangeslider"]["visible"] = False
    fig["layout"]["xaxis"]["tickformat"] = "%H:%M"
    fig["layout"]["yaxis"]["showgrid"] = True
    fig["layout"]["yaxis"]["gridcolor"] = "#3E3F40"
    fig["layout"]["yaxis"]["gridwidth"] = 1
    fig["layout"].update(paper_bgcolor="#21252C", plot_bgcolor="#21252C")

    return fig



# Dynamic Callbacks

# Replace currency pair row
def generate_ask_bid_row_callback(pair):
    def output_callback(n, i, bid, ask):
        return replace_row(pair, bid, ask)

    return output_callback


# returns string containing clicked charts
def generate_chart_button_callback():
    def chart_button_callback(*args):
        pairs = ""
        for i in range(len(stocks)):
            if args[i] > 0:
                pair = stocks[i]
                if pairs:
                    pairs = pairs + "," + pair
                else:
                    pairs = pair
        return pairs

    return chart_button_callback


# Function to update Graph Figure
def generate_figure_callback(pair):
    def chart_fig_callback(n_i, p, t, s, pairs, a, b, old_fig):

        if pairs is None:
            return {"layout": {}, "data": {}}

        pairs = pairs.split(",")
        if pair not in pairs:
            return {"layout": {}, "data": []}

        if old_fig is None or old_fig == {"layout": {}, "data": {}}:
            return get_fig(pair, a, b, t, s, p)

        fig = get_fig(pair, a, b, t, s, p)
        return fig

    return chart_fig_callback


# Function to close currency pair graph
def generate_close_graph_callback():
    def close_callback(n, n2):
        if n == 0:
            if n2 == 1:
                return 1
            return 0
        return 0

    return close_callback


# Function to open or close STYLE or STUDIES menu
def generate_open_close_menu_callback():
    def open_close_menu(n, className):
        if n == 0:
            return "not_visible"
        if className == "visible":
            return "not_visible"
        else:
            return "visible"

    return open_close_menu


# Function for hidden div that stores the last clicked menu tab
# Also updates style and studies menu headers
def generate_active_menu_tab_callback():
    def update_current_tab_name(n_style, n_studies):
        if n_style >= n_studies:
            return "Style", "span-menu selected", "span-menu"
        return "Studies", "span-menu", "span-menu selected"

    return update_current_tab_name


# Function show or hide studies menu for chart
def generate_studies_content_tab_callback():
    def studies_tab(current_tab):
        if current_tab == "Studies":
            return {"display": "block", "textAlign": "left", "marginTop": "30"}
        return {"display": "none"}

    return studies_tab


# Function show or hide style menu for chart
def generate_style_content_tab_callback():
    def style_tab(current_tab):
        if current_tab == "Style":
            return {"display": "block", "textAlign": "left", "marginTop": "30"}
        return {"display": "none"}

    return style_tab


# Open Modal
def generate_modal_open_callback():
    def open_modal(n):
        if n > 0:
            return {"display": "block"}
        else:
            return {"display": "none"}

    return open_modal


# Function to close modal
def generate_modal_close_callback():
    def close_modal(n, n2):
        return 0

    return close_modal


# Function for modal graph - set modal SL value to none
def generate_clean_sl_callback():
    def clean_sl(n):
        return 0

    return clean_sl


# Function for modal graph - set modal SL value to none
def generate_clean_tp_callback():
    def clean_tp(n):
        return 0

    return clean_tp


# Function to create figure for Buy/Sell Modal
def generate_modal_figure_callback(pair):
    def figure_modal(index, n, old_fig):
        if (n == 0 and old_fig is None) or n == 1:
            return get_modal_fig(pair, index)
        return old_fig  # avoid to compute new figure when the modal is hidden

    return figure_modal


# Function updates the pair orders div
def generate_order_button_callback(pair):
    def order_callback(n, vol, type_order, sl, tp, pair_orders, ask, bid):
        if n > 0:
            t = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            l = [] if pair_orders is None else json.loads(pair_orders)
            price = bid if type_order == "sell" else ask
            # if tp != 0:
            #     tp = (
            #         price + tp * 0.001
            #         if tp != 0 and pair[3:] == "JPY"
            #         else price + tp * 0.00001
            #     )
            #
            # if sl != 0:
            #     sl = price - sl * 0.001 if pair[3:] == "JPY" else price + sl * 0.00001
            print(pair)
            order = {
                "id": pair + str(len(l)),
                "time": t,
                "type": type_order,
                "volume": vol,
                "symbol": pair,
                "tp": tp,
                "sl": sl,
                "price": price,
                "profit": 0.00,
                "status": "open",
            }
            l.append(order)

            return json.dumps(l)
        return json.dumps(requests.get('http://localhost:5000/rest/get_order/{}'.format(pair)).json())

    return order_callback


# Function to update orders
def update_orders(orders, current_bids, current_asks, id_to_close):
    for order in orders:
        if order["status"] == "open":
            type_order = order["type"]
            #current_bids=( 2.72, 5.46, 37.1, 83.25, 100, 2722, 4395, 2.73, 5.53, 37.2, 83.9, 100.3)
            #current_asks=( 2.73, 5.53, 37.2, 83.9, 100.3)

            current_bid = current_bids[np.where(stocks == order["symbol"])[0][0]]
            current_ask = current_asks[np.where(stocks == order["symbol"])[0][0]]

            profit = (100 * ((current_bid - order["price"]) / order["price"])
                if type_order == "buy"
                else (
                    order["volume"]
                    * ((order["price"] - current_ask) / order["price"])
                )
            )

            order["profit"] = "%.2f" % profit
            price = current_bid if order["type"] == "buy" else current_ask

            if order["id"] == id_to_close:
                order["status"] = "closed"
                order["close Time"] = dt.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                order["close Price"] = price

            if order["tp"] != 0 and price >= order["tp"]:
                order["status"] = "closed"
                order["close Time"] = dt.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                order["close Price"] = price

            if order["sl"] != 0 and order["sl"] >= price:
                order["status"] = "closed"
                order["close Time"] = dt.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                order["close Price"] = price
    #print(orders)
    return orders


# Function to update orders div
def generate_update_orders_div_callback():
    def update_orders_callback(*args):
        orders = []
        current_orders = args[-1]
        close_id = args[-2]
        args = args[:-2]  # contains list of orders for each pair + asks + bids
        len_args = len(args)
        current_bids = args[len_args // 3 : 2 * len_args]
        current_asks = args[2 * len_args // 3 : len_args]
        args = args[: len_args // 3]
        ids = []
        if current_orders is not None:
            orders = json.loads(current_orders)
            for order in orders:
                ids.append(
                    order["id"]  # ids that allready have been added to current orders
                )
        for list_order in args:  # each currency pair has its list of orders
            if list_order != "[]":
                list_order = json.loads(list_order)
                for order in list_order:
                    if order["id"] not in ids:  # only add new orders
                        orders.append(order)
        if len(orders) == 0:
            return None
        #print(current_bids)
        # we update status and profit of orders
        orders = update_orders(orders, current_bids, current_asks, close_id)
        #print(orders)
        return json.dumps(orders)

    return update_orders_callback


# Resize pair div according to the number of charts displayed
def generate_show_hide_graph_div_callback(pair):
    def show_graph_div_callback(charts_clicked):
        if pair not in charts_clicked:
            return "display-none"

        charts_clicked = charts_clicked.split(",")  # [:4] max of 4 graph
        len_list = len(charts_clicked)

        classes = "chart-style"
        if len_list % 2 == 0:
            classes = classes + " six columns"
        elif len_list == 3:
            classes = classes + " four columns"
        else:
            classes = classes + " twelve columns"
        return classes

    return show_graph_div_callback


# Generate Buy/Sell and Chart Buttons for Left Panel
def generate_contents_for_left_panel():
    def show_contents(n_clicks):
        if n_clicks is None:
            return "display-none", "row summary"
        elif n_clicks % 2 == 0:
            return "display-none", "row summary"
        return "row details", "row summary-open"

    return show_contents
