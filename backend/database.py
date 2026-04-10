import mysql.connector
import time
import os


def get_db_connection():
    """
    Establishes a connection to the MySQL container.
    Includes a retry loop because MySQL takes time to start inside Docker.
    """
    # These match your docker-compose environment variables
    db_config = {
        'host': 'db',  # Name of the service in docker-compose
        'user': 'root',
        'password': 'meow@123',
        'database': 'mess_db',
        'port': 3306  # Internal Docker port
    }

    # Try connecting 10 times with a 2-second gap
    for attempt in range(10):
        try:
            connection = mysql.connector.connect(**db_config)
            if connection.is_connected():
                print("Successfully connected to the database!")
                return connection
        except mysql.connector.Error as err:
            print(f"Attempt {attempt + 1}: Database not ready yet... ({err})")
            time.sleep(2)

    raise Exception("Could not connect to the database after multiple attempts.")


# Test function to run a simple raw SQL query
def test_query():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # returns data as a Python Dict

    # Simple Raw SQL to verify our init.sql data
    cursor.execute("SELECT * FROM Food_Items")
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return results


if __name__ == "__main__":
    # If you run this file directly, it will test the connection
    print(test_query())