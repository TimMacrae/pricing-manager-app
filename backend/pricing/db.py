import os
from sqlalchemy import create_engine

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

MYSQL_SOURCE_HOST = os.getenv("MYSQL_SOURCE_HOST", "localhost")
MYSQL_ANALYTICS_HOST = os.getenv("MYSQL_ANALYTICS_HOST", "localhost")

MYSQL_SOURCE_DB = os.getenv("MYSQL_SOURCE_DB")
MYSQL_ANALYTICS_DB = os.getenv("MYSQL_ANALYTICS_DB")

# Using PyMySQL driver
SOURCE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_SOURCE_HOST}:3306/{MYSQL_SOURCE_DB}"
)
ANALYTICS_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_ANALYTICS_HOST}:3306/{MYSQL_ANALYTICS_DB}"
)

source_engine = create_engine(SOURCE_URL, pool_pre_ping=True)
analytics_engine = create_engine(ANALYTICS_URL, pool_pre_ping=True)
