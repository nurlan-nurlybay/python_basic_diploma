# database-connection.py

import os
import sys
from log_config import logger
from playhouse.pool import PooledSqliteDatabase


# Load database path from an environment variable
database_path = os.getenv('DATABASE_PATH', 'default.db')
db = PooledSqliteDatabase(database_path, max_connections=5)


def connect_to_database():
    try:
        db.connect()
    except Exception as e:
        logger.error("Database connection failed: %s", e)
        sys.exit(1)


def check_database_health() -> bool:
    try:
        db.connect()
        db.execute_sql('SELECT 1;')  # Simple query to check connectivity
        return True
    except Exception as e:
        logger.error("Database health check failed: %s", e)
        return False
