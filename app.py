import datetime
import pickle
import copy
import pathlib
import urllib.request
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import numpy as np

data = pd.read_csv('data/DATALOG.CSV', delimiter=",",
                   names=['date', 'time', 'lat', 'lon', 'vgps', 'velocity', 'course', 'heading', 'pitch', 'roll'])
data['drift'] = data.apply(lambda row: math.fabs(row['velocity'] *
                                                 math.sin(math.pi / 180 * math.fabs(row['course'] - row['heading']))),
                           axis=1)
data['vhead'] = data.apply(lambda row: math.fabs(row['velocity'] *
                                                 math.cos(math.pi / 180 * (row['course'] - row['heading']))), axis=1)

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

mapbox_access_token = 'pk.eyJ1IjoidGlnciIsImEiOiJjajhvdGNzdHgwN3piMndxdXB0OHh4MHc1In0.6EwnfD1AdR_hQeX6Jl0AmQ'

WELL_STATUSES = {'TWS': 'true wind speed', 'WS': 'wind speed', 'TWD': 'true wind direction', 'BS': 'boat speed',
                 'BD': 'boat direction', 'WVMG': 'wind VMG', 'route': 'boat route', 'RT': 'roll and trim'}

well_status_options = [
    {"label": str(WELL_STATUSES[well_status]), "value": str(well_status)}
    for well_status in WELL_STATUSES
]


layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=50, r=30, b=30, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Данные о записях. Выберите запись для анализа",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lat=data['lat'][100], lon=data['lon'][100]),
        zoom=2,
    ),
)


# data = sorted(data, key=lambda x: x['date'])


'''def gen_marks_for_slider():
    marks = {int(data['date'][0]): {'label': dt.datetime.utcfromtimestamp(data['date'][0]).strftime('%Y/%m/%d')},}
             #int(data[-1]['date']): {'label': dt.datetime.utcfromtimestamp(data[-1]['date']).strftime('%Y-%m-%d')}}
    for d in data[1: -1]:
        marks[int(d['date'])] = {}
    return marks


def get_data_from_main_map(main_graph_data):
    if main_graph_data is None:
        main_graph_data = {
            "points": [
                {"curveNumber": 4, "pointNumber": 569, 'lon': data['lon'][0], 'lat': data['lat'][0]}
            ]
        }
    lon = main_graph_data['points'][0]['lon']
    lat = main_graph_data['points'][0]['lat']
    for d in data:
        if d['lon'] == lon and d['lat'] == lat:
            return d
    return data[0]'''
'''dcc.RangeSlider(
                            id="year_slider",
                            min=data[0]['date'] - 10,
                            max=data[-1]['date'] + 10,
                            value=[data[0]['date']-10, data[-1]['date']+10],
                            marks=gen_marks_for_slider(),
                            className="dcc_control",
                        ),'''

'''html.Div(
           [
               html.Div(
                   [dcc.Graph(id="wind polar graph")],
                   className="pretty_container six columns",

               ),
               html.Div(
                   [dcc.Graph(id="wind rose graph")],
                   className="pretty_container six columns",

               )
           ],
           className="row flex-display",
       ),'''

app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [

                html.Div(
                    [
                        html.Div(
                            [
                                html.H2(
                                    "Sail race analytics",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H3(
                                    "Все данные о ветре и лодке в одном месте", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="column",
                    id="title",
                ),

            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "35px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H4(
                            "Панель для управления данными."),
                        html.H6(
                            "Выберите диапазон времени (Можно выбрать на гистограмме справа):",
                            className="control_label",
                        ),
                dcc.RangeSlider(
                            id="year_slider",
                            min=0,
                            max=2,
                            value=[1],
                            className="dcc_control",
                        ),

                        html.H6(
                            "Выберите необходимые графики.",
                            #className="control_label",
                        ),
                        dcc.Dropdown(
                            id="well_statuses",
                            options=well_status_options,
                            multi=True,
                            value=list(WELL_STATUSES.keys()),
                            className="dcc_control",
                        ),
                        html.P(
                            "Графики будут отображены ниже после выбора соответствующей точки на карте снизу"
                        )



                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),

            ],
            className="row flex-display",
        ),


        html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="well_text"), html.P("Дата")],
                                    id="wells",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="gasText"), html.P("Средняя скорость ветра")],
                                    id="gas",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="oilText"), html.P("Среднее направление ветра")],
                                    id="oil",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="waterText"), html.P("Средняя скорость лодки")],
                                    id="water",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        )
                    ],
                    id="right-column",
                    className="eight columns",
                ),

        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="route graph", style={"height": "650px"})],
                    className="pretty_container twelwe columns",

                )
            ],
            className="row flex-display",
        ),


        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="wind speed graph", style={'margin-bottom': '35px'})],
                    className="pretty_container twelwe columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="vhead graph", style={'margin-bottom': '35px'})],
                    className="pretty_container twelwe columns",
                ),
            ],
            className="row flex-display",
        ),

        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="wind direction graph")],
                    className="pretty_container twelwe columns",

                )
            ],
            className="row flex-display",
        ),


        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="boat speed graph")],
                    className="pretty_container twelwe columns",

                )
            ],
            className="row flex-display",
        ),

        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="roll graph")],
                    className="pretty_container twelwe columns",

                )
            ],
            className="row flex-display",
        ),

    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


@app.callback(Output("route graph", "figure"), Input("year_slider", "value"))
def make_route_figure(value):
    #dat = get_data_from_main_map(main_graph_hover)
    layout_individual = copy.deepcopy(layout)
    traces = []
    trace = dict(
        type="scattermapbox",
        lat=data['lat'],
        lon=data['lon'],
        mode='lines+markers',
        text=data['velocity'],
        #customdata=int(dt.datetime.utcfromtimestamp(data['date'][0]).strftime('%Y/%m/%d')),
        #name=str(dt.datetime.utcfromtimestamp(data['date']).strftime('%Y/%m/%d')),
        marker=dict(size=6, opacity=0.9, color=data['velocity'], colorscale='Viridis', showscale=True),
    )
    traces.append(trace)
    layout_individual['mapbox']['center']['lat'] = data['lat']
    layout_individual['mapbox']['center']['lon'] = data['lon']
    layout_individual['mapbox']['zoom'] = 10
    layout_individual['title'] = 'Маршрут'
    figure = dict(data=traces, layout=layout_individual)
    return figure


@app.callback(Output("wind speed graph", "figure"), Input("year_slider", "value"))
def make_wind_speed_figure(value):
    layout_individual = copy.deepcopy(layout)
    # dat = get_data_from_main_map(main_graph_hover)
    x = [i for i in range(len(data['velocity']))]
    dat = [
        dict(
            type="scatter",
            mode="lines+markers",
            name="Velocity",
            x=x,
            y=data['velocity'],
            text='mps',
            line=dict(shape="spline", smoothing=2, width=2, color="#59C3C3"),
            marker=dict(symbol="circle-open", color=data['velocity'], colorscale='Viridis', showscale=True),
        ),
        dict(
            type="scatter",
            mode="lines+markers",
            name="VGPS",
            x=x,
            y=data['vgps'],
            text='mps',
            line=dict(shape="spline", smoothing=2, width=2, color="#00cc00"),
            marker=dict(symbol="circle-open", color=data['vgps'], colorscale='Viridis', showscale=False)
        )
    ]
    layout_individual["title"] = 'velocity'
    layout_individual['hovermode'] = "x"
    xaxis = {
        "showline": True,
        "zeroline": True,
        "title": "Time",
            }
    yaxis = {
        "showline": True,
        "zeroline": True,
        "title": "velocity, mps",
    }
    layout_individual['xaxis'] = xaxis
    layout_individual['yaxis'] = yaxis

    figure = dict(data=dat, layout=layout_individual)
    return figure


@app.callback(Output("vhead graph", "figure"), Input("year_slider", "value"))
def make_wind_speed_figure(value):
    layout_individual = copy.deepcopy(layout)
    # dat = get_data_from_main_map(main_graph_hover)
    x = [i for i in range(len(data['velocity']))]
    dat = [
        dict(
            type="scatter",
            mode="lines+markers",
            name="V head",
            x=x,
            y=data['vhead'],
            text='mps',
            line=dict(shape="spline", smoothing=1, width=1, color="#59C3C3"),
            marker=dict(symbol="circle-open", color=data['vhead'], colorscale='Viridis', showscale=True),
        ),
        dict(
            type="scatter",
            mode="lines+markers",
            name="Drift",
            x=x,
            y=data['drift'],
            text='mps',
            line=dict(shape="spline", smoothing=5, width=1, color="#00cc00"),
            marker=dict(symbol="circle-open", color=data['drift'], colorscale='Viridis', showscale=False)
        )
    ]
    layout_individual["title"] = 'vhead, drift'
    layout_individual['hovermode'] = "x"
    xaxis = {
        "showline": True,
        "zeroline": True,
        "title": "Time",
            }
    yaxis = {
        "showline": True,
        "zeroline": True,
        "title": "v, mps",
    }
    layout_individual['xaxis'] = xaxis
    layout_individual['yaxis'] = yaxis

    figure = dict(data=dat, layout=layout_individual)
    return figure


@app.callback(Output("boat speed graph", "figure"), Input("year_slider", "value"))
def make_boat_speed_figure(value):
    layout_individual = copy.deepcopy(layout)
    # dat = get_data_from_main_map(main_graph_hover)
    x = [i for i in range(len(data['course']))]
    dat = [
        dict(
            type="scatter",
            mode="lines+markers",
            name="Course",
            x=x,
            y=data['course'],
            text='deg',
            line=dict(shape="spline", smoothing=2, width=2, color="#33CCCC"),
            marker=dict(symbol="circle-open")
        ),
        dict(
            type="scatter",
            mode="lines+markers",
            name="Heading",
            x=x,
            y=data['heading'],
            text='deg',
            line=dict(shape="spline", smoothing=2, width=2, color="#00cc00"),
            marker=dict(symbol="circle-open")
        )
    ]
    layout_individual["title"] = 'course'
    layout_individual['hovermode'] = "x"
    xaxis = {
        "showline": True,
        "zeroline": True,
        "title": "Time",
    }
    yaxis = {
        "showline": True,
        "zeroline": True,
        "title": "course, deg",
    }
    layout_individual['xaxis'] = xaxis
    layout_individual['yaxis'] = yaxis
    figure = dict(data=dat, layout=layout_individual)
    return figure


@app.callback(Output("wind direction graph", "figure"), Input("year_slider", "value"))
def make_wind_direction_figure(value):
    layout_individual = copy.deepcopy(layout)
    #dat = get_data_from_main_map(main_graph_hover)
    x = [i for i in range(len(data['pitch']))]
    dat = [
        dict(
            type="scatter",
            mode="lines+markers",
            name="Pitch",
            x=x,
            y=data['pitch'],
            line=dict(shape="spline", smoothing=2, width=2, color="#219C9C"),
            marker=dict(symbol="circle-open")
        )
    ]
    layout_individual["title"] = 'Pitch'
    layout_individual['hovermode'] = "x"
    xaxis = {
        "showline": True,
        "zeroline": True,
        "title": "Time",
    }
    yaxis = {
        "showline": True,
        "zeroline": True,
        "title": "Pitch, °",
    }
    layout_individual['xaxis'] = xaxis
    layout_individual['yaxis'] = yaxis
    figure = dict(data=dat, layout=layout_individual)
    return figure


@app.callback(Output("roll graph", "figure"), Input("year_slider", "value"))
def make_roll_figure(value):
    layout_individual = copy.deepcopy(layout)
    #dat = get_data_from_main_map(main_graph_hover)
    x = [i for i in range(len(data['roll']))]
    dat = [
        dict(
            type="scatter",
            mode="lines+markers",
            name="Roll",
            x=x,
            y=data['roll'],
            line=dict(shape="spline", smoothing=2, width=2, color="#219C9C"),
            marker=dict(symbol="circle-open")
        )
    ]
    layout_individual["title"] = 'Roll'
    layout_individual['hovermode'] = "x"
    xaxis = {
        "showline": True,
        "zeroline": True,
        "title": "Time",
    }
    yaxis = {
        "showline": True,
        "zeroline": True,
        "title": "Roll, °",
    }
    layout_individual['xaxis'] = xaxis
    layout_individual['yaxis'] = yaxis
    figure = dict(data=dat, layout=layout_individual)
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)