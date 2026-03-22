import pyvo
import logging
import time
import pandas as pd
from config import Config
from data.planet_repo import PlanetRepository
from services.processor import DataProcessor

logger = logging.getLogger(__name__)

# This service handles all interactions with the NASA TAP service, including fetching exoplanet data and determining when to refresh the local cache.
class NasaService:
    def __init__(self):
        self.repo = PlanetRepository()

    # Checks if the local cache is expired based on the last synchronization time and the defined cache timeout.
    # If expired, it fetches new data from NASA TAP and updates the local database.
    def sync_if_expired(self):
        last_sync = self.repo.get_last_sync_time()
        if (time.time() - last_sync) > Config.CACHE_TIMEOUT:
            self.fetch_and_store()

    # Fetches exoplanet data from NASA TAP and stores it in the local database. Returns True on success, False on failure.
    def fetch_and_store(self):
        try:
            logger.info("Connecting to NASA TAP...")
            service = pyvo.dal.TAPService(Config.NASA_TAP_URL)
            query = (
                "SELECT "
                "pl_name, "
                "hostname, "
                "disc_year, "
                "discoverymethod, "
                "pl_orbper, "
                "sy_dist, "
                "st_teff, "
                "st_rad, "
                "pl_orbsmax, "
                "pl_eqt," 
                "pl_bmasse, "
                "pl_rade, "
                "pl_insol "
                "FROM ps"
            )
            results = service.search(query)
            df = results.to_table().to_pandas()

            aggregation_rules = {
                'hostname': 'first',
                'disc_year': 'min',
                'discoverymethod': 'first',
                'pl_orbper': 'median',
                'sy_dist': 'mean',
                'st_teff': 'mean',
                'st_rad': 'mean',
                'pl_orbsmax': 'mean',
                'pl_eqt': 'mean',
                'pl_bmasse': 'mean',
                'pl_rade': 'mean',
                'pl_insol': 'mean'
            }

            numeric_cols = ['pl_orbper', 'sy_dist', 'st_teff', 'st_rad', 'pl_orbsmax', 'pl_eqt', 'pl_bmasse', 'pl_rade', 'pl_insol']

            for col in numeric_cols:
                if col in df.columns:
                    # errors='coerce' turns non-numeric junk into NaN
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            df = df.groupby('pl_name', as_index=False).agg(aggregation_rules)

            df = DataProcessor.clean_and_transform(df)
            
            self.repo.update_planets(df)
            logger.info("NASA sync successful.")
            return True
        except Exception as e:
            logger.error(f"NASA Sync Failed: {e}")
            return False