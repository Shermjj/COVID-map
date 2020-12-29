import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import json
import calendar
from datetime import date
from datetime import timedelta

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
f = open("london_simp.json")
lb = json.load(f)


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
df = pd.read_csv('bigdata.csv')
available_months = calendar.month_abbr[3:13] 

app.layout = html.Div([
    html.Div(["Time Period: ",dcc.RadioItems(id='type',
                   options=[{'label':'Five-day period','value':1},{'label':'Monthly period','value':2}],
                   value=2,
                   labelStyle={'display':'inline-block'})]),
    html.Div(["Variable:",dcc.Dropdown(
        id='variable',
        options=[{'label':'New Cases','value':'new_cases'},
                 {'label':'Total Cases','value':'total_cases'}],
        value='new_cases')]),
    html.Div(
    id='month-slider-container',
    children=[dcc.Slider(
        id='month-slider',
        min=3,
        max=12,
        value=3,
        marks={list(calendar.month_abbr).index(month):str(month) for month in available_months},
        step=None)],
        style={'display':'block'}
        ),
    html.Div(
    id='date-picker-container',
    children=["Initial date:",dcc.DatePickerSingle(id='date-picker',
                         min_date_allowed=date(2020, 3, 1),
                         max_date_allowed=date(2020,12, 14),
                         initial_visible_month=date(2020,3,1),
                         date=date(2020,3,1))],
    style={'display':'block'}
    ),
    html.Br(),
    dcc.Graph(id='graph-with-slider')
])
@app.callback(
        [Output('date-picker-container',component_property='style'),
        Output('month-slider-container',component_property='style')],
        [Input('type','value')]
        )
def show_hide_element(vis_state):
    if vis_state==1:
        return {'display':'block'}, {'display':'none'}
    else:
        return {'display':'none'}, {'display':'block'}

@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('variable','value'),
    Input('month-slider', 'value'),
    Input('date-picker','date'),
    Input('type','value'))
def update_figure(variable,selected_month,selected_date,type_value):
    if type_value == 1:
        date_first_object = date.fromisoformat(selected_date)
        date_final_object = date_first_object + timedelta(days=5)
        filtered_df = df[df.date.between(date_first_object.strftime('%Y-%m-%d'),
                                            date_final_object.strftime('%Y-%m-%d'))]
        fig = px.choropleth_mapbox(filtered_df, 
                           geojson=lb, locations='area_code',
                           color=variable,
                           animation_frame="date",
                           range_color=[filtered_df[variable].min(),filtered_df[variable].max()],
                           color_continuous_scale="Inferno",
                           mapbox_style="carto-positron",
                           opacity=0.5,featureidkey='properties.code',
                           hover_data=['area_name','date','new_cases','total_cases'],
                           zoom=9,
                           width=1000,height=700,
                           center = {"lat": 51.5074, "lon": -0.1277}
                          )
    else:
        filtered_df = df[df.date.str.match('2020-' + str(selected_month).zfill(2))]
        fig = px.choropleth_mapbox(filtered_df, 
                           geojson=lb, locations='area_code',
                           color=variable,
                           animation_frame="date",
                           range_color=[filtered_df[variable].min(),filtered_df[variable].max()],
                           color_continuous_scale="Inferno",
                           mapbox_style="carto-positron",
                           opacity=0.5,featureidkey='properties.code',
                           zoom=9,
                           width=1000,height=700,
                           center = {"lat": 51.5074, "lon": -0.1277}
                          )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(transition_duration=200)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
