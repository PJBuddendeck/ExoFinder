import numpy as np
import pandas as pd

# This service cleans and transforms raw data fetched from NASA TAP.
# Includes calculating the equilibrium temperature (Teq) for each planet based on available stellar and orbital parameters. 
# It also handles any necessary data cleaning to ensure compatibility with our database and frontend display requirements.
class DataProcessor:
    # Main entry point for cleaning and transforming the DataFrame.
    def clean_and_transform(df: pd.DataFrame) -> pd.DataFrame:
        # 1. Calculate Equilibrium Temperature (Teq) for each planet
        df = DataProcessor.calc_eqt(df)

        # 2. Calculate Earth Similarity Index (ESI) for each planet
        df = DataProcessor.calc_esi(df)

        # 3. Calculate Habitability Zone for each planet
        df = DataProcessor.calc_hz(df)

        # 4. Approximate planet type (rocky, gas) for each planet
        df = DataProcessor.calc_planet_type(df)

        # 5. Final Cleanup: Handle NaNs for the DB
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
        # 1. Physics Derivations
        # These will result in NaN if either Bmasse or Rade is missing
        if 'pl_bmasse' in df.columns and 'pl_rade' in df.columns:
            df['pl_dens_earth'] = df['pl_bmasse'] / (df['pl_rade']**3)
            df['pl_vesc_earth'] = np.sqrt(df['pl_bmasse'] / df['pl_rade'])

        # 2. Define the strict requirements
        cols = ['pl_rade', 'pl_dens_earth', 'pl_vesc_earth', 'pl_insol']
        weights = np.array([0.57, 1.07, 0.70, 5.58])
        n = len(weights)

        # 3. Create a Strict Mask
        # Only True if EVERY required column has a non-null value
        # .all(axis=1) checks horizontally across the row
        strict_mask = df[cols].notna().all(axis=1)

        # 4. Initialize the column with NaN (NULL)
        df['pl_esi'] = np.nan

        # 5. Only perform math on the valid subset
        if strict_mask.any():
            # Create a temporary Series for the calculation
            esi_values = pd.Series(1.0, index=df[strict_mask].index)

            for i, col in enumerate(cols):
                # Pull only the valid rows for this parameter
                x = pd.to_numeric(df.loc[strict_mask, col])
                
                # Similarity: 1 - |x - 1| / (x + 1)
                similarity = 1 - (x - 1).abs() / (x + 1)
                
                # Update accumulator (Geometric Mean)
                esi_values *= similarity ** (weights[i] / n)

            # Assign calculated values back to the main DataFrame
            df.loc[strict_mask, 'pl_esi'] = esi_values.round(3)

        return df

    def calc_hz(df: pd.DataFrame) -> pd.DataFrame:
        # Placeholder for future HZ calculation logic
        df['pl_hz'] = None
        return df
    
    def calc_planet_type(df: pd.DataFrame) -> pd.DataFrame:
        # Placeholder for future planet type classification logic
        df['pl_type'] = None
        return df