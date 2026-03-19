import sqlite3
import time
import os
from config import Config

# This class abstracts all database interactions related to exoplanet data and metadata (like last sync time).
class PlanetRepository:
    # Establishes a connection to the SQLite database.
    @staticmethod
    def get_connection():
        conn = sqlite3.connect(Config.DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

    # Retrieves the last synchronization time from the metadata table.
    # If the table or entry doesn't exist, it returns 0.
    def get_last_sync_time(self):
        if not os.path.exists(Config.DB_FILE):
            return 0
        try:
            with self.get_connection() as conn:
                res = conn.execute("SELECT last_sync FROM metadata").fetchone()
                return res[0] if res else 0
        except sqlite3.OperationalError:
            return 0

    # Updates the planets table with new data and sets the last synchronization time in the metadata table.
    # This operation is atomic to ensure data integrity.
    def update_planets(self, df):
        with self.get_connection() as conn:
            # Atomic update: Replace table and update metadata in one transaction
            df.to_sql('planets', conn, if_exists='replace', index=False)
            conn.execute("CREATE TABLE IF NOT EXISTS metadata (last_sync REAL)")
            conn.execute("DELETE FROM metadata")
            conn.execute("INSERT INTO metadata VALUES (?)", (time.time(),))

    # Searches for planets in the database based on a search term that matches either the planet name or host star name.
    # Results are ordered by distance and limited to a specified number (defined in config.py).
    def search_planets(self, search_term="", limit=50):
        query = "SELECT * FROM planets"
        params = []
        
        if search_term:
            query += " WHERE LOWER(pl_name) LIKE ? OR LOWER(hostname) LIKE ?"
            term = f"%{search_term.lower()}%"
            params = [term, term]
        
        query += " ORDER BY sy_dist ASC NULLS LAST LIMIT ?"
        params.append(limit)

        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]