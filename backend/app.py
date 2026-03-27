import logging
import pandas as pd
from datetime import datetime
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

from config import Config
from data.planet_repo import PlanetRepository
from services.nasa_service import NasaService

# Setup
logging.basicConfig(level=logging.INFO)
app = Flask(__name__, static_folder=Config.STATIC_FOLDER, static_url_path='/')
CORS(app)

# Instantiate our logic layers
planet_repo = PlanetRepository()
nasa_service = NasaService()

@app.route('/api/planets', methods=['GET'])
def get_planets():
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'sy_dist')
    order = request.args.get('order', 'asc')
    
    repo = PlanetRepository()
    planets = repo.search_planets(search_term=search, sort_by=sort_by, sort_order=order)
    return jsonify(planets)

@app.route('/api/sync-status', methods=['GET'])
def get_last_sync():
    try:
        last_sync = planet_repo.get_last_sync_time()
        last_sync = datetime.fromtimestamp(last_sync) if last_sync else None
        last_sync = pd.to_datetime(last_sync) if last_sync else None
        return jsonify({"last_sync": last_sync.isoformat()})
    except Exception as e:
        app.logger.error(f"Error fetching last sync time: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/")
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=Config.PORT)