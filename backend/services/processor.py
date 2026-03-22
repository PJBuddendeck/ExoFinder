import numpy as np
import pandas as pd

# This service cleans and transforms raw data fetched from NASA TAP.
# Includes calculating the equilibrium temperature (Teq) for each planet based on available stellar and orbital parameters. 
# It also handles any necessary data cleaning to ensure compatibility with our database and frontend display requirements.
class DataProcessor:
    def clean_and_transform(df: pd.DataFrame) -> pd.DataFrame:
        # 1. Calculate Equilibrium Temperature (Teq) for each planet
        df = DataProcessor.calc_eqt(df)

        # 2. Calculate Earth Similarity Index (ESI) for each planet
        df = DataProcessor.calc_esi(df)

        # 3. Final Cleanup: Handle NaNs for the DB
        # SQLite doesn't love NaN, so we replace with None (which becomes NULL)
        df = df.where(pd.notnull(df), None)

        return df

    def calc_eqt(df: pd.DataFrame) -> pd.DataFrame:
        # 1. Ensure the column exists so we can check for NaNs
        if 'pl_eqt' not in df.columns:
            df['pl_eqt'] = np.nan
        else:
            df['pl_eqt'] = pd.to_numeric(df['pl_eqt'], errors='coerce')

        required_cols = ['st_teff', 'st_rad', 'pl_orbsmax']
        if all(col in df.columns for col in required_cols):
            # 2. Calculate the theoretical value for EVERY row (temporary variable)
            albedo = 0.3
            a_solar = df['pl_orbsmax'] * 215.032
            
            calculated_teq = (
                df['st_teff'] * np.sqrt(df['st_rad'] / (2 * a_solar)) * (1 - albedo)**0.25
            )

            # 3. Use fillna: It ONLY fills the NaNs and leaves existing numbers alone
            df['pl_eqt'] = df['pl_eqt'].fillna(calculated_teq)

            # 4. Round the final result
            df['pl_eqt'] = df['pl_eqt'].round(2)
        
        return df
    
    def calc_esi(df: pd.DataFrame) -> pd.DataFrame:
        # Calculate ESI, check if columns exist to avoid crashes
        return df