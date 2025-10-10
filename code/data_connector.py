# data_connector.py
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

class SQLConnector:
    """
    Handles connection and query execution for SQL-based data sources.
    """
    def __init__(self, host, user, password, database, port=3306):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": port
        }

    def connect(self):
        try:
            connection = mysql.connector.connect(**self.config)
            if connection.is_connected():
                print(f"[Connected] {self.config['database']} at {self.config['host']}")
                return connection
        except Error as e:
            print(f"[Error] Cannot connect to database: {e}")
        return None

    def execute_query(self, query):
        connection = self.connect()
        if not connection:
            return None

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        except Error as e:
            print(f"[Error] Query failed: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
