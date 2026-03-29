import sqlite3
import time
import os
from warnings import filters
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
            # 1. Atomic update of the main planets table
            df.to_sql('planets', conn, if_exists='replace', index=False)
            
            # 2. Get the row count from the processed DataFrame
            total_planets = len(df)
            
            # 3. Ensure metadata table exists with two columns: last_sync and total_count
            conn.execute("CREATE TABLE IF NOT EXISTS metadata (last_sync REAL, total_count INTEGER)")
            
            # 4. Clear old metadata
            conn.execute("DELETE FROM metadata")
            
            # 5. Insert current timestamp and the planet count
            conn.execute(
                "INSERT INTO metadata (last_sync, total_count) VALUES (?, ?)", 
                (time.time(), total_planets)
            )

    # Searches for planets in the database based on a search term that matches either the planet name or host star name.
    # Results are ordered by distance and limited to a specified number defined by 
    def search_planets(self, search_term="", sort_by="sy_dist", sort_order="asc", limit=48, has_eqt=False, has_esi=False):
        allowed_columns = {
            "sy_dist": "sy_dist",
            "pl_bmasse": "pl_bmasse",
            "pl_rade": "pl_rade",
            "disc_year": "disc_year",
            "pl_eqt": "pl_eqt",
            "pl_esi": "pl_esi"
        }
        
        column = allowed_columns.get(sort_by, "sy_dist")
        direction = "ASC" if sort_order.lower() == "asc" else "DESC"
        
        # 1. Start with the base query
        query = "SELECT * FROM planets"
        conditions = []
        params = []
        
        # 2. Collect all conditions
        if search_term:
            conditions.append("(LOWER(pl_name) LIKE ? OR LOWER(hostname) LIKE ?)")
            term = f"%{search_term.lower()}%"
            params.extend([term, term])
        
        if has_eqt:
            conditions.append("pl_eqt IS NOT NULL")
            
        if has_esi:
            conditions.append("pl_esi IS NOT NULL")

        # 3. Add WHERE clause ONLY if we have conditions
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # 4. CRITICAL: Add a space BEFORE the ORDER BY
        query += f" ORDER BY ({column} IS NULL) ASC, {column} {direction}, pl_name ASC LIMIT ?"
        params.append(limit)

        with self.get_connection() as conn:
            # For debugging, you can print(query) here to see the final string
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]