import os

# Centralized configuration for the ExoFinder application, including database file location, NASA TAP URL, cache timeout, and server port.
class Config:
    NASA_TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP"
    DB_FILE = "exoplanets.db"
    CACHE_TIMEOUT = 86400  # 24 hours
    STATIC_FOLDER = '../frontend/build'
    PORT = int(os.environ.get("PORT", 5000))