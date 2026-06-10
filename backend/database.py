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


async def run_db_seeder():
    seed_file_path = os.path.join(os.path.dirname(__file__), "seed.sql")

    if not os.path.exists(seed_file_path):
        print("Seeder skipped: seed.sql file not found.")
        return

    print("Executing raw SQL seed scripts on Aiven cluster via Async connection pool...")

    conn = await db_pool.get_connection()
    cursor = await conn.cursor()

    try:
        with open(seed_file_path, "r") as f:
            sql_content = f.read().strip()

        if not sql_content:
            return

        results = await cursor.execute(sql_content, multi=True)

        async for result in results:
            pass

        await conn.commit()
        print("Aiven Database initialized and seeded successfully!")
    except Exception as e:
        await conn.rollback()
        print(f"Database seeding failed: {e}")
    finally:
        await cursor.close()
        await conn.close()

if __name__ == "__main__":
    try:
        print("Testing database connection...")
        connection = db_pool.get_connection()
        print(f"Connected to {os.getenv('DB_NAME')} at {os.getenv('DB_HOST')}")
        connection.close()
    except Exception as e:
        print(f"Error: {e}")