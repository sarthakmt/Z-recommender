import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app
from apps import customer,owner


# Styles
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
tabs_styles = {
    'height': '44px',
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'text-align':'center',
    'align-items': 'center',
    'justify-content': 'center' 
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}


# html
app.layout = html.Div([
    html.Div([
    
    # Header
    html.Div(
            children=[
                html.Span(
                    className="app-title",
                    children=[
                        dcc.Markdown("**Z-Recommender**"),
                    ],
                ),
            ],
            className="banner"
        ),

    # Tabs
    html.Div([
        dcc.Tabs(
                id='tabs',
                children=[
                    dcc.Tab(label='Customer', value='1', style=tab_style, selected_style=tab_selected_style),
                    dcc.Tab(label='Owner', value='2', style=tab_style, selected_style=tab_selected_style)
                ],
                value='1'
            ),
        html.Div(id='tab-output')
        ],
        className="row")
    ])
])    


# callback handlers
@app.callback(
	Output('tab-output', 'children'),
	[Input('tabs', 'value')])
def show_content(value):
	if value == '1':
		return customer.layout
	elif value == '2':
		return owner.layout
	else:
		html.Div()

if __name__ == '__main__':
    app.run_server(debug=True)