import os
import re
import pymysql
from dotenv import load_dotenv

# 1. Load credentials from your root .env file
load_dotenv('.env')

try:
    # 2. Open connection to your Aiven MySQL Database
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        autocommit=True
    )
    cursor = connection.cursor()

    # 3. Read your original init.sql file
    with open('db/init.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 4. Clean up Windows line endings and isolate blocks
    sql_content = sql_content.replace('\r\n', '\n')

    # 5. Extract queries by parsing out DELIMITER sections cleanly
    statements = []

    # Split the file by the word 'DELIMITER' case-insensitively
    chunks = re.split(r'(?i)\bDELIMITER\b', sql_content)

    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        # Check if this chunk defines a custom delimiter block (e.g., "$$ ... $$")
        match = re.match(r'^([^\n]+)\n(.*)', chunk, re.DOTALL)
        if match and any(d in match.group(1) for d in ['$$', '//']):
            delim = match.group(1).strip()
            body = match.group(2).strip()

            # Extract the stored procedures/triggers using the custom delimiter
            for stmt in body.split(delim):
                if stmt.strip() and not stmt.strip().upper().startswith('DELIMITER'):
                    statements.append(stmt.strip())
        else:
            # Standard chunk separated by regular semicolons
            # If a delimiter line was left at the end of a previous block, clean it
            lines = chunk.split('\n')
            if lines and any(d in lines[0] for d in ['$$', '//', ';']):
                chunk = '\n'.join(lines[1:])

            for stmt in chunk.split(';'):
                if stmt.strip():
                    statements.append(stmt.strip())

    print("⏳ Executing your native database schema on Aiven...")
    for statement in statements:
        clean_statement = statement.strip()

        # Completely skip any comment lines or administrative system sets blocked by Aiven
        if not clean_statement or clean_statement.startswith('#') or clean_statement.startswith('--'):
            continue
        if clean_statement.upper().startswith('SET GLOBAL'):
            print("⚠️ Skipping restricted administrative command: SET GLOBAL")
            continue

        try:
            cursor.execute(clean_statement)
        except Exception as query_error:
            print(f"\n❌ Failed query query text:\n{clean_statement}\n")
            raise query_error

    print("\n🚀 Success! All Tables, Views, Procedures, Triggers, and Dummy Data are live on Aiven!")

    cursor.close()
    connection.close()

except Exception as e:
    print(f"\n💥 Migration failed: {e}")