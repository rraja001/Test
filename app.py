
from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os
from dash import Dash

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

PREDEFINED_DATASETS = {
    "Sample A": "static/datasets/sample_a.csv",
    "Sample B": "static/datasets/sample_b.csv"
}

dataframes = {}

@app.route('/')
def index():
    return render_template('index.html', datasets=list(PREDEFINED_DATASETS.keys()))

@app.route('/upload', methods=['POST'])
def upload_dataset():
    if 'dataset' not in request.files:
        return "No file uploaded", 400
    file = request.files['dataset']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    dataframes["uploaded"] = pd.read_csv(filepath)
    return redirect(url_for('explore_data'))

@app.route('/explore')
def explore_data():
    return render_template('dash_embed.html')

@app.route('/get_data/<dataset_key>')
def get_data(dataset_key):
    if dataset_key in dataframes:
        return dataframes[dataset_key].to_json(orient='records')
    return jsonify({"error": "Dataset not found"}), 404

if __name__ == '__main__':
    from dash_app import init_dash
    init_dash(app)
    app.run(debug=True)
