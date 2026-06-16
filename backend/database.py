import time
from mysql.connector import pooling, Error
from dotenv import load_dotenv
import os

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

db_pool = create_pool()


def run_db_seeder():
    seed_file_path = os.path.join(os.path.dirname(__file__), "seed.sql")

    if not os.path.exists(seed_file_path):
        print("Seeder skipped: seed.sql file not found.")
        return

    print("Executing SQL seed scripts...")

    conn = db_pool.get_connection()
    cursor = conn.cursor()

    try:
        with open(seed_file_path, "r") as f:
            sql_content = f.read().strip()

        if not sql_content:
            return

        for statement in sql_content.replace("\r\n", "\n").split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt + ";")

        conn.commit()
        print("Database seeded successfully!")
    except Exception as e:
        conn.rollback()
        print(f"Database seeding failed: {e}")
    finally:
        cursor.close()
        conn.close()


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
        print(f"Connected successfully")
        connection.close()
    except Exception as e:
        print(f"Error: {e}")
