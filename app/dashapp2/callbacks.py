from datetime import datetime as dt

import pandas_datareader as pdr
from dash.dependencies import Input
from dash.dependencies import Output
import requests
import csv
import pandas as pd

def register_callbacks(dashapp):
    @dashapp.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
    def update_graph(selected_dropdown_value):
        df = pdr.get_data_yahoo(selected_dropdown_value, start=dt(2017, 1, 1), end=dt.now())
        if df.shape[0]<2:
            CSV_URL='https://www.rava.com/empresas/precioshistoricos.php?e={}&csv=1'.format(selected_dropdown_value[:-3])
            print(CSV_URL)
            with requests.Session() as s:
                download = s.get(CSV_URL)

                decoded_content = download.content.decode('utf-8')

                cr = csv.reader(decoded_content.splitlines(), delimiter=',')
                my_list = list(cr)
                df=pd.DataFrame(my_list[1:], columns=['Date','Open','Min','Max','Close','Volume','openint'])
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.set_index('Date')
        return {
            'data': [{
                'x': df.index,
                'y': df.Close
            }],
            'layout': {'margin': {'l': 40, 'r': 0, 't': 20, 'b': 30}}
        }
