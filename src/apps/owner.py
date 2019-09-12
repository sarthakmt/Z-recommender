import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from file_manager import *
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
        ],className="row"),
        html.Div(id= "second-count-graph", children = [
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
	Output('cusine-dp', 'options'),
	[Input('city-o-dp', 'value'),
    Input('region-o-dp', 'value')])
def update_cus_drop_down(city,region):
    filtered_by_city_reg = filtered_data(city,region)
    cusine_count_df = get_cusine_counts(filtered_by_city_reg)
    cusine_count = cusine_count_df.sort_values('Count',ascending=False)
    cusine_list = cusine_count_df.Cusine.unique().tolist()
    return [{'label': i, 'value': i} for i in cusine_list]

@app.callback(
    Output('rest-count-graph', 'children'),
	[Input('city-o-dp','value')])
def update_table(city):
    global filtered_by_city
    filtered_by_city = filtered_data(city)
    region_list = filtered_by_city.REGION.unique().tolist()
    res_count_list = filtered_by_city.REGION.value_counts().tolist()
    cusine_count_df = get_cusine_counts(filtered_by_city)
    cusine_count = cusine_count_df.sort_values('Count',ascending=False)
    cusine_list = cusine_count_df.Cusine.unique().tolist()
    # print(qualified.head())
    return html.Div([
            html.Div([    
                dcc.Graph(
                    id="side-bar-graph",
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
                )],className="six columns"),
                html.Div([
                    dcc.Graph(
                        id="cus-pie-graph",
                        # columns=[{"name": i, "id": i} for i in qualified.columns],
                        figure={
                        'data' : [go.Pie(
                            labels=cusine_count["Cusine"].tolist()[0:9], 
                            values=cusine_count["Count"].tolist()[0:9]
                            # textinfo='label'
                            )],
                        'layout': go.Layout(
                            title=f"Popularity of cusines")
                        }    
                    )],className="six columns")        
                ],className="row")    

# initial_load
@app.callback(
    Output('second-count-graph', 'children'),
	[Input('city-o-dp','value')]
)                
def update_new_chart(city):
    city_data = initial_load[initial_load["CITY"] == city] 
    city_data = city_data.loc[(city_data['VOTES'] == 'NEW') | (city_data['VOTES'] == '-')]
    region_list = city_data.REGION.unique().tolist()
    new_count_list = city_data.REGION.value_counts().tolist()
    # cusine_count_df = get_cusine_counts(filtered_by_city)
    # cusine_count = cusine_count_df.sort_values('Count',ascending=False)
    # cusine_list = cusine_count_df.Cusine.unique().tolist()
    return html.Div([
        html.Div([
            dcc.Graph(
                    id="side-bar-graph-new",
                    # columns=[{"name": i, "id": i} for i in qualified.columns],
                    figure={
                    'data' : [go.Bar(
                        x=region_list[0:9], 
                        y=new_count_list[0:9]
                        # textinfo='label'
                        )],
                    'layout': go.Layout(
                        title=f"New Restro Count by regions")
                    }    
                )],className="six columns")
        # html.Div([
        #     dcc.Graph(
        #             id="cusine-type-new",
        #             # columns=[{"name": i, "id": i} for i in qualified.columns],
        #             figure={
        #             'data' : [go.Bar(
        #                 x=region_list[0:9], 
        #                 y=new_count_list[0:9]
        #                 # textinfo='label'
        #                 )],
        #             'layout': go.Layout(
        #                 title=f"New Restro Count by regions")
        #             }    
        #         )],className="six columns")
    ],className = "row")
