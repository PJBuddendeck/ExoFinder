import os
import time
import json
import pandas as pd
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import pyvo
import logging

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)

# Constants for NASA TAP and caching
NASA_TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP"
CACHE_FILE = "exoplanet_cache.json"
CACHE_TIMEOUT = 86400  # 24 hours in seconds

# Function used by the API endpoint to get data, either from cache or NASA
# If the cached data is older than 24 hours, it will fetch fresh data from NASA and update the cache
# If NASA is down, it will attempt to return expired cache as a fallback
def get_cached_data():
    now = time.time()
    
    # Check if cache exists and is fresh
    if os.path.exists(CACHE_FILE):
        file_age = now - os.path.getmtime(CACHE_FILE)
        if file_age < CACHE_TIMEOUT:
            logger.info("Valid local cache located. Serving from local cache.")
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)

    # Cache is expired or missing: Fetch from NASA
    logger.info("Cache expired/missing. Fetching fresh data from NASA.")
    try:
        service = pyvo.dal.TAPService(NASA_TAP_URL)
        # Fetch a larger set so we can filter locally
        query = """
        SELECT 
            pl_name, hostname, disc_year, discoverymethod, pl_orbper 
        FROM ps 
        WHERE default_flag = 1 
        ORDER BY disc_year DESC
        """
        results = service.search(query)
        data = results.to_table().to_pandas().to_dict(orient='records')
        
        # Save to local file
        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f)
            
        return data
    
    except Exception as e:
        logger.error(f"NASA Sync Error: {e}")
        # If NASA is down, try to return expired cache as fallback
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                logger.info("Serving expired cache as fallback.")
                return json.load(f)
        return []

@app.route('/api/planets', methods=['GET'])
def get_planets():
    search_term = request.args.get('search', '').strip().lower()
    logger.info(f"API request received with search term: '{search_term}'")
    
    all_planets = get_cached_data()
    
    # Filter the list locally in Python
    if search_term:
        filtered = [
            p for p in all_planets 
            if search_term in p['pl_name'].lower() or search_term in p['hostname'].lower()
        ]
    else:
        filtered = all_planets[:100] # Return top 100 if no search

    return jsonify(filtered[:50]) # Limit return to 50 for performance

# Catch-all route to serve React app for any non-API requests (supports client-side routing)
@app.errorhandler(404)
def not_found(e):
    logger.info("404 error occurred.")
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    # Use environment variables for Port if available (required for Heroku/Render)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)