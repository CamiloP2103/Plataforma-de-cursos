# run.py
from waitress import serve
from app import app  # Tu archivo principal app.py

serve(app, host='172.31.6.90', port=8000)
