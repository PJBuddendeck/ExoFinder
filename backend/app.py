import logging
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
    search_term = request.args.get('search', '').strip()
    
    try:
        # Ensure data is fresh before querying
        nasa_service.sync_if_expired()
        
        data = planet_repo.search_planets(search_term)
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"API Error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/")
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=Config.PORT)