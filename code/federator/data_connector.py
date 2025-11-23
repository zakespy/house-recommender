# data_connector.py
import pymysql
from pymysql.err import MySQLError
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
            "port": port,
            "cursorclass": pymysql.cursors.DictCursor   # returns row as dict
        }

    def connect(self):
        try:
            print("trying to connect")
            connection = pymysql.connect(**self.config)
            print(f"[Connected] {self.config['database']} at {self.config['host']}")
            return connection
        
        except MySQLError as e:
            print(f"[Error] Cannot connect to database: {e}")
            return None

    def execute_query(self, query):
        connection = self.connect()
        if not connection:
            return None

        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return results
        
        except MySQLError as e:
            print(f"[Error] Query failed: {e}")
            return None
        
        finally:
            connection.close()
