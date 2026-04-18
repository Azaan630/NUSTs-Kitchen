import time
from mysql.connector import pooling, Error
from dotenv import load_dotenv
import os

from mysql.connector.aio import MySQLConnectionPool

load_dotenv()

def create_pool():
    while True:
        try:
            return pooling.MySQLConnectionPool(
                pool_name="db_pool",
                pool_size=10,
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME"),
                port=int(os.getenv("DB_PORT", "3306")),
            )
        except Error as err:
            print(f"Database not ready: {err}. Retrying in 5 seconds...")
            time.sleep(5)

db_pool: MySQLConnectionPool = create_pool()

def get_db():
    if db_pool is not None:
        conn = db_pool.get_connection()
        try:
            yield conn
        finally:
            conn.close()
    else:
        raise RuntimeError("Database pool was not initialized.")

if __name__ == "__main__":
    try:
        print("Testing database connection...")
        connection = db_pool.get_connection()
        print(f"Connected to {os.getenv('DB_NAME')} at {os.getenv('DB_HOST')}")
        connection.close()
    except Exception as e:
        print(f"Error: {e}")