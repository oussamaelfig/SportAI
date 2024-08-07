from flask import Flask
from dash import Dash, page_container
from dash import html
from services.preprocess import Preprocessor
import dash_bootstrap_components as dbc
import os

server = Flask(__name__)

file_path = os.path.join(os.path.dirname(__file__), 'static', 'EURO_2020_DATA.xlsx')

# Initialize Preprocessor singleton instance with the specified data file path
preprocessor = Preprocessor(file_path)

app = Dash(__name__, use_pages=True, server=server, url_base_pathname='/', external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css'  # Include Font Awesome
], )

app.layout = html.Div([
    html.H1("UEFA Euro 2020 Team Performance", style={'textAlign': 'center', 'padding': '20px'}),
    page_container  # Placeholder for page content
])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
