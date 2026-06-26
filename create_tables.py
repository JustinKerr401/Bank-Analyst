import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def create_tables():

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
    CREATE TABLE IF NOT EXISTS accounts (
        id BIGINT unsigned not null auto_increment PRIMARY KEY,
        account CHAR(2),
        date DATE,
        daysequence INT,
        description VARCHAR(80),
        amount DECIMAL(10,2),
        balance DECIMAL(10,2),
        checkmisc VARCHAR(50),
        note VARCHAR(50),
        category VARCHAR(50)
    )
    """)

    conn.commit()

    # Loans (store transactions from credit card)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loans (
        id BIGINT unsigned not null auto_increment PRIMARY KEY,
        date DATE,
        daysequence INT,
        description VARCHAR(80),
        amount DECIMAL(10,2),
        interest DECIMAL(10,2),
        fees DECIMAL(10,2),
        balance DECIMAL(10,2),
        checkmisc VARCHAR(50),
        note VARCHAR(50),
        category VARCHAR(50)
    )
    """)

    conn.commit()

    # Note descriptions with commas in them
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faultydescriptions (
        name VARCHAR(80) PRIMARY KEY
    )
    """)

    conn.commit()

    # Note files that have been fixed
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fixedfiles (
        filename VARCHAR(31) PRIMARY KEY
    )
    """)

    conn.commit()

create_tables()