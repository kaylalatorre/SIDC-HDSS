"""
Python script to test our PostgreSQL connection via Python
"""

# Import libraries
from src.data.db_conn import load_db_table
from config.config import get_project_root
# Project root
PROJECT_ROOT = get_project_root()
# Read database - PostgreSQL
# df = load_db_table(config_db = 'database.ini', query = 'SELECT * FROM auth_user LIMIT 5')
df = load_db_table(config_db = 'database.ini', query = 'SELECT * FROM farmsapp_internalbiosec LIMIT 5')
print(df)

