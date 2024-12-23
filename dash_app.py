
from dash import Dash, dcc, html, Input, Output, dash_table, State
import pandas as pd
import requests
import plotly.express as px

def init_dash(server):
    dash_app = Dash(__name__, server=server, url_base_pathname='/dashboard/')

    dash_app.layout = html.Div([
        html.H1("Advanced Data Explorer"),

        html.Label("Select X-Axis Column:"),
        dcc.Dropdown(id='x-axis-dropdown', placeholder="Select X-axis column"),

        html.Label("Select Y-Axis Column (Optional):"),
        dcc.Dropdown(id='y-axis-dropdown', placeholder="Select Y-axis column (optional)"),

        html.Label("Select Visualization Type:"),
        dcc.Dropdown(
            id='viz-type-dropdown',
            options=[
                {'label': 'Scatter Plot', 'value': 'scatter'},
                {'label': 'Line Plot', 'value': 'line'},
                {'label': 'Box Plot', 'value': 'box'},
                {'label': 'Histogram', 'value': 'histogram'},
                {'label': '3D Scatter Plot', 'value': 'scatter_3d'},
                {'label': 'Heatmap', 'value': 'heatmap'},
            ],
            placeholder="Select Visualization Type"
        ),

        html.Div(id='filter-container'),

        html.Button("Apply Filters", id="apply-filters-button", n_clicks=0),

        dash_table.DataTable(id='data-table', page_size=10, style_table={'overflowX': 'auto'}),

        dcc.Graph(id='data-visualization'),

        html.Button("Download CSV", id="download-csv-button", n_clicks=0),
        html.Button("Download Graph", id="download-graph-button", n_clicks=0),
        dcc.Download(id="csv-download"),
        dcc.Download(id="graph-download")
    ])

    @dash_app.callback(
        [Output('x-axis-dropdown', 'options'), 
         Output('y-axis-dropdown', 'options'), 
         Output('data-table', 'columns'), 
         Output('data-table', 'data'),
         Output('filter-container', 'children')],
        Input('url', 'pathname')
    )
    def load_data(pathname):
        dataset_key = "uploaded"
        response = requests.get(f'http://localhost:5000/get_data/{dataset_key}')
        
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            options = [{'label': col, 'value': col} for col in df.columns]
            columns = [{'name': col, 'id': col} for col in df.columns]
            data = df.to_dict('records')
            
            filters = []
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    filters.append(html.Div([
                        html.Label(f"Filter {col}:"),
                        dcc.RangeSlider(
                            id=f'filter-{col}',
                            min=df[col].min(),
                            max=df[col].max(),
                            step=(df[col].max() - df[col].min()) / 100,
                            marks={int(val): str(int(val)) for val in [df[col].min(), df[col].max()]},
                            value=[df[col].min(), df[col].max()]
                        )
                    ]))
                else:
                    filters.append(html.Div([
                        html.Label(f"Filter {col}:"),
                        dcc.Dropdown(
                            id=f'filter-{col}',
                            options=[{'label': val, 'value': val} for val in df[col].unique()],
                            multi=True,
                            placeholder=f"Filter {col}"
                        )
                    ]))
            return options, options, columns, data, filters
        return [], [], [], [], []

    @dash_app.callback(
        Output('data-visualization', 'figure'),
        [Input('apply-filters-button', 'n_clicks')],
        [State('x-axis-dropdown', 'value'),
         State('y-axis-dropdown', 'value'),
         State('viz-type-dropdown', 'value')]
    )
    def update_graph(n_clicks, x_col, y_col, viz_type):
        if not x_col or not viz_type:
            return {}

        dataset_key = "uploaded"
        response = requests.get(f'http://localhost:5000/get_data/{dataset_key}')
        if response.status_code != 200:
            return {}

        df = pd.DataFrame(response.json())

        if viz_type == 'scatter':
            return px.scatter(df, x=x_col, y=y_col, title="Scatter Plot")
        elif viz_type == 'line':
            return px.line(df, x=x_col, y=y_col, title="Line Plot")
        elif viz_type == 'box':
            return px.box(df, x=x_col, y=y_col, title="Box Plot")
        elif viz_type == 'histogram':
            return px.histogram(df, x=x_col, title="Histogram")
        elif viz_type == 'scatter_3d':
            return px.scatter_3d(df, x=x_col, y=y_col, title="3D Scatter Plot")
        elif viz_type == 'heatmap':
            return px.density_heatmap(df, x=x_col, y=y_col, title="Heatmap")
        return {}
