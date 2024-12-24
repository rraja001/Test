
from flask import Flask, render_template, request, jsonify
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Initialize Flask app
app = Flask(__name__)

# Prepopulated datasets
datasets = {
    "sample1": pd.DataFrame({
        "A": [1, 2, 3, 4],
        "B": [10, 20, 30, 40],
        "C": [100, 200, 300, 400]
    }),
    "sample2": pd.DataFrame({
        "X": [5, 6, 7, 8],
        "Y": [50, 60, 70, 80],
        "Z": [500, 600, 700, 800]
    })
}

# Store uploaded datasets
uploaded_data = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    df = pd.read_csv(file)
    uploaded_data[file.filename] = df
    return jsonify({"message": f"File {file.filename} uploaded successfully"}), 200

# Dash app integration
dash_app = Dash(__name__, server=app, url_base_pathname="/dashboard/")

dash_app.layout = html.Div([
    html.H1("Data Explorer Dashboard"),
    dcc.Dropdown(
        id="dataset-selector",
        options=[{"label": name, "value": name} for name in list(datasets.keys()) + list(uploaded_data.keys())],
        placeholder="Select a dataset"
    ),
    dcc.Dropdown(id="column-selector", placeholder="Select a column"),
    dcc.Graph(id="data-visualization"),
])

@dash_app.callback(
    Output("column-selector", "options"),
    Input("dataset-selector", "value")
)
def update_columns(dataset_name):
    if dataset_name in datasets:
        df = datasets[dataset_name]
    elif dataset_name in uploaded_data:
        df = uploaded_data[dataset_name]
    else:
        return []
    return [{"label": col, "value": col} for col in df.columns]

@dash_app.callback(
    Output("data-visualization", "figure"),
    [Input("dataset-selector", "value"), Input("column-selector", "value")]
)
def update_graph(dataset_name, column_name):
    if not dataset_name or not column_name:
        return {}
    if dataset_name in datasets:
        df = datasets[dataset_name]
    elif dataset_name in uploaded_data:
        df = uploaded_data[dataset_name]
    else:
        return {}
    return px.histogram(df, x=column_name)

if __name__ == "__main__":
    app.run(debug=True)
