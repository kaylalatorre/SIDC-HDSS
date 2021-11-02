"""
When our works need to read the table on the database regularly, 
we can create a function with the filename db_conn.py as follows. 
It will load the table that fits with our input (config_db and query).
"""
# Note: tbh dk what this for (?)

# Import libraries
import pandas as pd
import psycopg2
from config.config import config
# Take in a PostgreSQL table and outputs a pandas dataframe
def load_db_table(config_db, query):
    params = config(config_db)
    engine = psycopg2.connect(**params)
    data = pd.read_sql(query, con = engine)
    return data