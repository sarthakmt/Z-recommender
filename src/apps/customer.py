import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from file_manager import cities,initial_load,all_regions,simple_recommender,filtered_data,cont_recommender
from app import app
import pandas as pd

def make_card(row,index):
    return html.Div([
        html.Div([
            html.Div([
                html.Div(row["NAME"], className = 'boxHeader'),
                html.Div(row["CUSINE_CATEGORY"], className = 'boxLabel'),
                # html.Div('916k', className = 'boxNumbers')
            ], className = 'boxText')
        ], className = 'innerBox' )
    ], className='cardBox', id=str(index))


# divs = []
# for index, row in qualified.head(10).iterrows():
#     print(index)
#     divs.append(make_card(row,index))

layout=[
    html.Div([
        html.H3("Customer"),
        
        # filters
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='city-dp',
                    options=[{'label': i, 'value': i} for i in cities],
                    placeholder='Select City'
                )
            ],className = "four columns"),

            html.Div([
                dcc.Dropdown(
                    id='region-dp',
                    placeholder='Select Region'
                )
            ],className = "four columns"),
            html.Div([
                dcc.Dropdown(
                    id='restaurants-dp',
                    placeholder='Select Restaurants'
                )
            ],className = "four columns")    
        ],className = "row"),
        # html.Div(divs, className='container')
        html.Div(id= "recco", children = [
        ],className="row"),
        html.Div(id= "cont-recco", children = [
            html.Div(id = "bar-plot",children=[

            ],className="six columns"),
            html.Div(id = "cont-recco-tab",children=[

            ],className="six columns")
        ],className="row"),
        # html.Div([
        #     html.Div([
        #         dcc.Dropdown(
        #             id='cusine-type-dp',
        #             placeholder='Select Cusine type'
        #         )
        #     ]),
        #     html.Div([

        #     ])
        # ])    
    ])
]

# Callbacks
@app.callback(
	Output('region-dp', 'options'),
	[Input('city-dp', 'value')])
def update_drop_down(value):
    region_list = all_regions(initial_load,value)
    return [{'label': i, 'value': i} for i in region_list]

@app.callback(
    Output('recco', 'children'),
	[Input('city-dp','value'),
    Input('region-dp','value')])
def update_table(city,region):
    fil_data = filtered_data(city,region)
    # Simple Call
    qualified = simple_recommender(fil_data)
    cols = ["NAME","CUSINE_CATEGORY","PRICE","RATING","VOTES","score"]
    qualified = qualified[cols]

    # quali_table = df_to_table(qualified)
    # print(qualified.head())
    return html.Div([
            html.Div([
                html.H6("Top Options in the city "+city +" and region "+region),
                dash_table.DataTable(
                    id='rec-table',
                    columns=[{"name": i, "id": i} for i in qualified.columns],
                    data=qualified.head(10).to_dict('records'),
                )],className="six columns"),
            html.Br(),    
            html.Div([    
                dcc.Graph(
                    id="my-graph",
                    # columns=[{"name": i, "id": i} for i in qualified.columns],
                    figure={
                    'data' : [go.Pie(
                        labels=qualified["CUSINE_CATEGORY"].unique().tolist()[0:9], 
                        values=qualified["CUSINE_CATEGORY"].value_counts().tolist()[0:9]
                        # textinfo='label'
                        )],
                    'layout': go.Layout(
                        title=f"Popularity of cusines")
                    }    
                )],className="six columns"),

                html.Div(id="top_open_opportunities", className="table")    
                ],className="row")


@app.callback(
    Output('restaurants-dp', 'options'),
	[Input('city-dp','value'),
    Input('region-dp','value')])
def update_dp(city,region):
    fil_data = filtered_data(city,region)
    res_list = fil_data.NAME.unique().tolist()
    return [{'label': i, 'value': i} for i in res_list]

@app.callback(
    Output('bar-plot', 'children'),
	[Input('city-dp','value'),
    Input('region-dp','value')])
def update_price_counts(city,region):
    if region != None:
        fil_data = filtered_data(city,region)
    return html.Div([
            dcc.Graph(
                    id="scatter-graph",
                    figure={
                    'data' : [go.Bar(
                        x=fil_data["PRICE"].value_counts().to_dense().keys(), 
                        y=fil_data["PRICE"].value_counts(),
                        # textinfo='label'
                        )],
                    'layout': go.Layout(
                        title=f"Price Range Counts")
                    }    
                )])

@app.callback(
    Output('cont-recco-tab', 'children'),
	[Input('city-dp','value'),
    Input('region-dp','value'),
    Input('restaurants-dp', 'value')])    
def update_cont_rec(city,region,rest):
    fil_data = filtered_data(city,region)
    cont_qualified = cont_recommender(fil_data,region,rest)
    ranges = [0,250,500,750,1000,1250,1500,2000]
    dummy = fil_data ["PRICE"].groupby(pd.cut(fil_data.PRICE, ranges)).count()
    return  html.Div([
                html.H6("Similar restaurants like "+rest),
                dash_table.DataTable(
                    id='cont-rec-table',
                    columns=[{"name": i, "id": i} for i in cont_qualified.columns],
                    data=cont_qualified.head(10).to_dict('records'),
                )]),