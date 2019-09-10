import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from file_manager import cities,initial_load,all_regions,simple_recommender,filtered_data,cont_recommender
from app import app

layout=[
    html.Div([
        html.H3("Owner"),

        # filters
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='city-o-dp',
                    options=[{'label': i, 'value': i} for i in cities],
                    placeholder='Select City'
                )
            ],className = "four columns"),

            html.Div([
                dcc.Dropdown(
                    id='region-o-dp',
                    placeholder='Select Region'
                )
            ],className = "four columns"),
            html.Div([
                dcc.Dropdown(
                    id='cusine-dp',
                    placeholder='Select Cusines'
                )
            ],className = "four columns")    
        ],className = "row"),
        html.Div(id= "rest-count-graph", children = [
        ],className="row")
    ])    
]

@app.callback(
	Output('region-o-dp', 'options'),
	[Input('city-o-dp', 'value')])
def update_drop_down(value):
    region_list = all_regions(initial_load,value)
    return [{'label': i, 'value': i} for i in region_list]

@app.callback(
    Output('rest-count-graph', 'children'),
	[Input('city-o-dp','value')])
def update_table(city):
    fil_data = filtered_data(city)
    region_list = fil_data.REGION.unique().tolist()
    res_count_list = fil_data.REGION.value_counts().tolist()
    # print(qualified.head())
    return html.Div([
            html.Div([    
                dcc.Graph(
                    id="my-graph",
                    # columns=[{"name": i, "id": i} for i in qualified.columns],
                    figure={
                    'data' : [go.Bar(
                        y=region_list[0:9], 
                        x=res_count_list[0:9],
                        orientation='h'
                        # textinfo='label'
                        )],
                    'layout': go.Layout(
                        title=f"Restro Count by regions")
                    }    
                )],className="six columns")    
                ],className="row")    