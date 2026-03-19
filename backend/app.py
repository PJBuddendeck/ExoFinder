import os
import time
import sqlite3
import pandas as pd
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import pyvo
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)

NASA_TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP"
DB_FILE = "exoplanets.db"
CACHE_TIMEOUT = 86400  # 24 hours

# Sync with NASA TAP and store results in SQLite
def sync_with_nasa():
    try:
        logger.info("Syncing with NASA TAP...")
        service = pyvo.dal.TAPService(NASA_TAP_URL)
        query = "SELECT " \
        "pl_name, hostname, disc_year, discoverymethod, pl_orbper " \
        "FROM ps WHERE default_flag = 1"
        
        # Use a timeout if supported, otherwise pyvo uses default
        results = service.search(query)
        df = results.to_table().to_pandas()

        with sqlite3.connect(DB_FILE) as conn:
            # Save the dataframe to SQLite, replacing the old table
            df.to_sql('planets', conn, if_exists='replace', index=False)
            # Record the last sync time in a separate metadata table
            conn.execute("CREATE TABLE IF NOT EXISTS metadata (last_sync REAL)")
            conn.execute("DELETE FROM metadata")
            conn.execute("INSERT INTO metadata VALUES (?)", (time.time(),))
        
        logger.info("Sync complete.")
        return True
    except Exception as e:
        logger.error(f"NASA Sync Failed: {e}")
        return False

# Query the database with optional search term and filters
def get_planets_from_db(search_term=""):
    if not os.path.exists(DB_FILE):
        sync_with_nasa()

    # Check if cache is expired
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        try:
            last_sync = cursor.execute("SELECT last_sync FROM metadata").fetchone()[0]
            if (time.time() - last_sync) > CACHE_TIMEOUT:
                logger.info("Cache expired. Syncing with NASA TAP...")
                sync_with_nasa()
        except:
            logger.info("No cache found. Syncing with NASA TAP...")
            sync_with_nasa()

        # Query the data
        query = "SELECT * FROM planets"
        params = []
        if search_term:
            query += " WHERE LOWER(pl_name) LIKE ? OR LOWER(hostname) LIKE ?"
            search_param = f"%{search_term}%"
            params = [search_param, search_param]
        
        query += " ORDER BY disc_year DESC LIMIT 50"
        
        conn.row_factory = sqlite3.Row # Allows accessing columns by name
        cursor = conn.cursor()
        rows = cursor.execute(query, params).fetchall()
        
        return [dict(row) for row in rows]

# API endpoint to get planets with optional search query and filters
@app.route('/api/planets', methods=['GET'])
def get_planets():
    search_term = request.args.get('search', '').strip().lower()
    try:
        data = get_planets_from_db(search_term)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

# Catch-all route to serve React app for any non-API requests (supports client-side routing)
@app.errorhandler(404)
def not_found(e):
    logger.info("404 error occurred.")
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    # Use environment variables for Port if available (required for Heroku/Render)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)