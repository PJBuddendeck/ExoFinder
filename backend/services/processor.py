import numpy as np
import pandas as pd

# This service cleans and transforms raw data fetched from NASA TAP.
# Includes calculating the equilibrium temperature (Teq) for each planet based on available stellar and orbital parameters. 
# It also handles any necessary data cleaning to ensure compatibility with our database and frontend display requirements.
class DataProcessor:
    @staticmethod
    def clean_and_transform(df: pd.DataFrame) -> pd.DataFrame:
        # 1. Standardize column names (NASA names can be cryptic)
        # Ensure we have the columns needed for the math
        
        # 2. Calculate Teq, check if columns exist to avoid crashes
        if all(col in df.columns for col in ['st_teff', 'st_rad', 'pl_orbsmax']):
            # Bond Albedo (Default to 0.3 if not provided in dataset)
            albedo = 0.3
            
            # Constants/Math
            # Teq = Teff * sqrt(R_star / (2 * semi_major_axis)) * (1 - albedo)^0.25
            # Note: We must ensure units match. Usually R_star is in Solar Radii 
            # and orbsmax is in AU. 1 AU ≈ 215 Solar Radii.
            
            # Convert AU to Solar Radii for the ratio
            a_in_solar_radii = df['pl_orbsmax'] * 215.032
            
            df['pl_eqt'] = (
                df['st_teff'] * np.sqrt(df['st_rad'] / (2 * a_in_solar_radii)) * (1 - albedo)**0.25
            )
            
            # Round for the UI
            df['pl_eqt'] = df['pl_eqt'].round(2)

        # 3. Final Cleanup: Handle NaNs for the DB
        # SQLite doesn't love NaN, so we replace with None (which becomes NULL)
        df = df.where(pd.notnull(df), None)

        return df