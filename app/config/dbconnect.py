import mysql.connector
from .config import settings


def get_connection():
    dbconfig = {
    "host": settings.db_host,
    "port": settings.db_port,
    "user": settings.db_user,
    "password": settings.db_password,
    "database": settings.db_name,
}

    return mysql.connector.connect(**dbconfig) 
