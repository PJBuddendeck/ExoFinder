import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS # Good for dev, safe for prod
import pyvo
import logging

# 1. Setup Logging (Essential for debugging on a real server)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. Initialize Flask
# static_folder points to where 'npm run build' puts the React files
app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app) 

NASA_TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP"

# --- FRONTEND ROUTES ---

@app.route("/")
def serve():
    """Serves the compiled React 'index.html'"""
    if os.path.exists(app.static_folder):
        return send_from_directory(app.static_folder, 'index.html')
    else:
        return "Frontend not built. Run 'npm run build' in the frontend folder.", 404

# --- API ROUTES ---

@app.route('/api/planets', methods=['GET'])
def get_planets():
    """
    Fetches filtered exoplanet data from NASA.
    Usage: /api/planets?search=Kepler
    """
    search_term = request.args.get('search', '').strip()
    
    try:
        service = pyvo.dal.TAPService(NASA_TAP_URL)
        
        # We use a f-string for the query. 
        # Note: In a high-security DB, we'd use parameters to prevent injection.
        # NASA's TAP is read-only, so this is generally acceptable for this use case.
        query = f"""
        SELECT TOP 50 
            pl_name, hostname, disc_year, discoverymethod 
        FROM ps 
        WHERE default_flag = 1 
        AND LOWER(pl_name) LIKE LOWER('%{search_term}%')
        ORDER BY disc_year DESC
        """
        
        logger.info(f"Querying NASA for: {search_term}")
        results = service.search(query)
        
        # Convert the Astropy table to a Pandas DataFrame, then to a List of Dicts
        data = results.to_table().to_pandas().to_dict(orient='records')
        
        return jsonify(data)

    except Exception as e:
        logger.error(f"NASA API Error: {e}")
        return jsonify({"error": "Failed to fetch data from NASA archive"}), 500

# --- CATCH-ALL ---

@app.errorhandler(404)
def not_found(e):
    """Ensures React Router handles page refreshes correctly"""
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    # Use environment variables for Port if available (required for Heroku/Render)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)