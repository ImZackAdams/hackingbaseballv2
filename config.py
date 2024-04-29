# config.py

class Config(object):
    CURRENT_YEAR = 2024
    SQLALCHEMY_DATABASE_URI = 'sqlite:///path_to_your_database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = 'simple'  # Consider "redis" for production use
    # Add other global settings and configurations here
