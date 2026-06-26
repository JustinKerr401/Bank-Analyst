import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def drop_tables():

    # Connect to the database
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASS"),
        database=os.getenv("MYSQL_DB")
    )

    cursor = conn.cursor()

    # Accounts (store transactions from RS, CS, and MM)
    cursor.execute("""
    DROP TABLE IF EXISTS accounts
    """)

    conn.commit()

    # Loans (store transactions from credit card)
    cursor.execute("""
    DROP TABLE IF EXISTS loans
    """)

    conn.commit()

    # Note descriptions with commas in them
    cursor.execute("""
    DROP TABLE IF EXISTS faultydescriptions
    """)

    conn.commit()

    # Note files that have been fixed
    cursor.execute("""
    DROP TABLE IF EXISTS fixedfiles
    """)

    conn.commit()

drop_tables()