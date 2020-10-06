import datetime

import pandas_datareader as pdr
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State

from .functions import *



def register_callbacks(dashapp):


    # Loop through all stocks
    for pair in stocks:

        # Callback for Buy/Sell and Chart Buttons for Left Panel
        dashapp.callback(
            [Output(pair + "contents", "className"), Output(pair + "summary", "className")],
            [Input(pair + "summary", "n_clicks")],
        )(generate_contents_for_left_panel())

        # Callback for className of div for graphs
        dashapp.callback(
            Output(pair + "graph_div", "className"), [Input("charts_clicked", "children")]
        )(generate_show_hide_graph_div_callback(pair))

        # Callback to update the actual graph
        dashapp.callback(
            Output(pair + "chart", "figure"),
            [
                Input("i_tris", "n_intervals"),
                Input(pair + "dropdown_period", "value"),
                Input(pair + "chart_type", "value"),
                Input(pair + "studies", "value"),
                Input("charts_clicked", "children"),
            ],
            [
                State(pair + "ask", "children"),
                State(pair + "bid", "children"),
                State(pair + "chart", "figure"),
            ],
        )(generate_figure_callback(pair))

        # updates the ask and bid prices
        dashapp.callback(
            Output(pair + "row", "children"),
            [Input("i_bis", "n_intervals")],
            [
                State(pair + "index", "children"),
                State(pair + "bid", "children"),
                State(pair + "ask", "children"),
            ],
        )(generate_ask_bid_row_callback(pair))

        # close graph by setting to 0 n_clicks property
        dashapp.callback(
            Output(pair + "Button_chart", "n_clicks"),
            [Input(pair + "close", "n_clicks")],
            [State(pair + "Button_chart", "n_clicks")],
        )(generate_close_graph_callback())

        # show or hide graph menu
        dashapp.callback(
            Output(pair + "menu", "className"),
            [Input(pair + "menu_button", "n_clicks")],
            [State(pair + "menu", "className")],
        )(generate_open_close_menu_callback())

        # stores in hidden div name of clicked tab name
        dashapp.callback(
            [
                Output(pair + "menu_tab", "children"),
                Output(pair + "style_header", "className"),
                Output(pair + "studies_header", "className"),
            ],
            [
                Input(pair + "style_header", "n_clicks_timestamp"),
                Input(pair + "studies_header", "n_clicks_timestamp"),
            ],
        )(generate_active_menu_tab_callback())

        # hide/show STYLE tab content if clicked or not
        dashapp.callback(
            Output(pair + "style_tab", "style"), [Input(pair + "menu_tab", "children")]
        )(generate_style_content_tab_callback())

        # hide/show MENU tab content if clicked or not
        dashapp.callback(
            Output(pair + "studies_tab", "style"), [Input(pair + "menu_tab", "children")]
        )(generate_studies_content_tab_callback())

        # show modal
        dashapp.callback(Output(pair + "modal", "style"), [Input(pair + "Buy", "n_clicks")])(
            generate_modal_open_callback()
        )

        # set modal value SL to O
        dashapp.callback(Output(pair + "SL", "value"), [Input(pair + "Buy", "n_clicks")])(
            generate_clean_sl_callback()
        )

        # set modal value TP to O
        dashapp.callback(Output(pair + "TP", "value"), [Input(pair + "Buy", "n_clicks")])(
            generate_clean_tp_callback()
        )

        # hide modal
        dashapp.callback(
            Output(pair + "Buy", "n_clicks"),
            [
                Input(pair + "closeModal", "n_clicks"),
                Input(pair + "button_order", "n_clicks"),
            ],
        )(generate_modal_close_callback())

        # updates modal figure
        dashapp.callback(
            Output(pair + "modal_graph", "figure"),
            [Input(pair + "index", "children"), Input(pair + "Buy", "n_clicks")],
            [State(pair + "modal_graph", "figure")],
        )(generate_modal_figure_callback(pair))

        # each pair saves its orders in hidden div
        dashapp.callback(
            Output(pair + "orders", "children"),
            [Input(pair + "button_order", "n_clicks")],
            [
                State(pair + "volume", "value"),
                State(pair + "trade_type", "value"),
                State(pair + "SL", "value"),
                State(pair + "TP", "value"),
                State(pair + "orders", "children"),
                State(pair + "ask", "children"),
                State(pair + "bid", "children"),
            ],
        )(generate_order_button_callback(pair))

    # updates hidden div with all the clicked charts
    dashapp.callback(
        Output("charts_clicked", "children"),
        [Input(pair + "Button_chart", "n_clicks") for pair in stocks],
        [State("charts_clicked", "children")],
    )(generate_chart_button_callback())

    # updates hidden orders div with all pairs orders
    dashapp.callback(
        Output("orders", "children"),
        [Input(pair + "orders", "children") for pair in stocks]
        + [Input(pair + "bid", "children") for pair in stocks]
        + [Input(pair + "ask", "children") for pair in stocks]
        + [Input("closable_orders", "value")],
        [State("orders", "children")],
    )(generate_update_orders_div_callback())

    # Callback to update Orders Table
    @dashapp.callback(
        Output("orders_table", "children"),
        [Input("orders", "children"), Input("dropdown_positions", "value")],
    )
    def update_order_table(orders, position):
        headers = [
            "Order Id",
            "Time",
            "Type",
            "Volume",
            "Symbol",
            "TP",
            "SL",
            "Price",
            "Status",
            "Profit",
            "Close Time",
            "Close Price",
        ]

        # If there are no orders
        if orders is None or orders is "[]":
            list_order=requests.get('http://localhost:5000/rest/get_orders').json()
            # return [
            #     html.Table(html.Tr(children=[html.Th(title) for title in headers])),
            #     html.Div(
            #         className="text-center table-orders-empty",
            #         children=[html.P("No " + position + " positions data row")],
            #     ),
            # ]
        else:
            list_order = json.loads(orders)
        rows = []

        #list_order = json.loads(req_order)
        for order in list_order:
            tr_childs = []
            for attr in order:
                if str(order["status"]).lower() == position:
                    tr_childs.append(html.Td(order[attr]))
            # Color row based on profitability of order
            if float(order["profit"]) >= 0:
                rows.append(html.Tr(className="profit", children=tr_childs))
            else:
                rows.append(html.Tr(className="no-profit", children=tr_childs))

        return html.Table(children=[html.Tr([html.Th(title) for title in headers])] + rows)


    # Update Options in dropdown for Open and Close positions
    @dashapp.callback(Output("dropdown_positions", "options"), [Input("orders", "children")])
    def update_positions_dropdown(orders):
        closeOrders = 0
        openOrders = 0
        if orders is not None:
            orders = json.loads(orders)
            for order in orders:
                if order["status"].lower() == "closed":
                    closeOrders += 1
                if order["status"].lower() == "open":
                    openOrders += 1
        return [
            {"label": "Open positions (" + str(openOrders) + ")", "value": "open"},
            {"label": "Closed positions (" + str(closeOrders) + ")", "value": "closed"},
        ]


    # Callback to close orders from dropdown options
    @dashapp.callback(Output("closable_orders", "options"), [Input("orders", "children")])
    def update_close_dropdown(orders):
        options = []
        if orders is not None:
            orders = json.loads(orders)
            for order in orders:
                if order["status"].lower() == "open":
                    options.append({"label": order["id"], "value": order["id"]})
        return options


    # Callback to update Top Bar values
    @dashapp.callback(Output("top_bar", "children"), [Input("orders", "children")])
    def update_top_bar(orders):
        if orders is None or orders is "[]":
            return get_top_bar()

        orders = json.loads(orders)
        open_pl = 0
        balance = 50000
        free_margin = 50000
        margin = 0

        for order in orders:
            if order["status"].lower() == "open":
                open_pl += float(order["profit"])
                conversion_price = (
                    1 if order["symbol"][:3] == "USD" else float(order["price"])
                )
                margin += (float(order["volume"]) * 100000) / (200 * conversion_price)
            else:
                balance += float(order["profit"])

        equity = balance - open_pl
        free_margin = equity - margin
        margin_level = "%" if margin == 0 else "%2.F" % ((equity / margin) * 100) + "%"
        equity = "%.2F" % equity
        balance = "%.2F" % balance
        open_pl = "%.2F" % open_pl
        free_margin = "%.2F" % free_margin
        margin = "%2.F" % margin

        return get_top_bar(balance, equity, margin, free_margin, margin_level, open_pl)


    # Callback to update live clock
    @dashapp.callback(Output("live_clock", "children"), [Input("interval", "n_intervals")])
    def update_time(n):
        return datetime.datetime.now().strftime("%H:%M:%S")


    # Callback to update news
    @dashapp.callback(Output("news", "children"), [Input("i_news", "n_intervals")])
    def update_news_div(n):
        return update_news()
