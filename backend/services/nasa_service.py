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

            query_ps = (
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
            df_ps = service.search(query_ps).to_table().to_pandas()

            query_spec = (
                "SELECT "
                "pl_name, "
                "spec_type, "
                "num_datapoints, "
                "instrument, "
                "facility AS spec_facility,"
                "minwavelng, "
                "maxwavelng "
                "FROM spectra"
            )
            df_spec = service.search(query_spec).to_table().to_pandas()

            ps_numeric_cols = ['pl_orbper', 'sy_dist', 'st_teff', 'st_rad', 'pl_orbsmax', 'pl_eqt', 'pl_bmasse', 'pl_rade', 'pl_insol']
            spec_numeric_cols = ['num_datapoints', 'minwavelng', 'maxwavelng']

            for col in ps_numeric_cols:
                if col in df_ps.columns:
                    # errors='coerce' turns non-numeric junk into NaN
                    df_ps[col] = pd.to_numeric(df_ps[col], errors='coerce')

            for col in spec_numeric_cols:
                if col in df_spec.columns:
                    # errors='coerce' turns non-numeric junk into NaN
                    df_spec[col] = pd.to_numeric(df_spec[col], errors='coerce')

            ps_aggregation_rules = {
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

            df_ps = df_ps.groupby('pl_name', as_index=False).agg(ps_aggregation_rules)

            spec_aggregation_rules = {
                'spec_type': lambda x: ', '.join(set(x.dropna())),
                'num_datapoints' : 'sum',
                'instrument' : lambda x: ', '.join(set(x.dropna())),
                'spec_facility': lambda x: ', '.join(set(x.dropna())),
                'minwavelng' : 'min',
                'maxwavelng' : 'max'
            }

            df_spec = df_spec.groupby('pl_name', as_index=False).agg(spec_aggregation_rules)

            df = pd.merge(df_ps, df_spec, on='pl_name', how='left')

            df = DataProcessor.clean_and_transform(df)
            
            self.repo.update_planets(df)
            logger.info("NASA sync successful.")
            return True
        except Exception as e:
            logger.error(f"NASA Sync Failed: {e}")
            return False