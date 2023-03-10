# RUN USING `py visualise.py` and
# visit http://127.0.0.1:8050/ in your web browser.
# Vscode debug does not work for some reason, despite name indeed == "__main__".

# Look into Write Ahead Logging for faster simulatneous sqlite read & writes. https://stackoverflow.com/questions/10325683/can-i-read-and-write-to-a-sqlite-database-concurrently-from-multiple-connections

# May wish to have orjson installed to improve performance. pip install orjson

# For even better performance looking into clientside callbacks
# also background callbacks, only useful for calls longer than ~30s (I think) so not useful for our ends

import os

import pandas as pd
import numpy as np

import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Output, Input

# import deployment
import servicesqlite as serv

app = Dash(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__)) # path python file is located in. Which is DIFFERENT to current working directory (where the python file is being run from).
db_path = dir_path + "\\servicesqlite2.db"
db = serv.DB(dir_path + "\\servicesqlite2.db")

# try:
#     os.remove(db_path)
# except FileNotFoundError:
#     pass

db = serv.DB(db_path)
print(db.show_tables())
dbf = pd.DataFrame(columns=["id", "timestamp", "car_speed", "temperature", "humidity"])

app.layout = html.Div(children=[

    dcc.Graph(
        id='live-graph',
    ),
    dcc.Graph(
        id='live-graph-2',
    ),

    dcc.Interval(
        id = "graph-update",
        interval = 1000,
        n_intervals = 0
    )
])

@app.callback(
    [Output('live-graph', 'figure'), Output('live-graph-2', 'figure')], [Input('graph-update', 'n_intervals')]
)
def update_graph_scatter(n):
    global dbf
    new_data = db.read_new()
    dbf = dbf.append(new_data, ignore_index=True)

    # using webgl to plot with much better performance than SVG
    fig = px.line(dbf, x="timestamp", y=["car_speed", "temperature", "humidity"], render_mode="webgl")
    fig.update_layout(uirevision="const") # makes plot only reset the scale when auto-zoom is enabled in browser

    return fig, fig

if __name__ == '__main__':
    app.run_server(debug=False, threaded=False)