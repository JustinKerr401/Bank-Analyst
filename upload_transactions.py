# Proper loading
import os
import mysql.connector
import csv
import sys
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from descriptionFixer import fixCSV
from create_table import create_tables

load_dotenv()
create_tables()

# Connect to the database
conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASS"),
    database=os.getenv("MYSQL_DB")
)
cursor = conn.cursor()

# Note CSV files present
folder = Path(__file__).parent / "assets"
files = [file.name for file in folder.iterdir() if file.is_file()]

# Iterate through each CSV file and upload transactions
for file in files:
    # Identify account based
    account = file.lower().split(" ")[0]
    table = ""
    if account == "rs" or account == "cs" or account == "mm":
        table = "accounts"
    elif account == "vl":
        table = "loans"
    else:
        print(f"Unknown account type for file: {file}")
        continue

    # Fix CSV file if it contains a known problematic description
    cursor.execute("SELECT * FROM faultydescriptions")
    faultydescriptions = {row[0] for row in cursor.fetchall()}
    cursor.execute("SELECT * FROM fixedfiles")
    fixedfiles = {row[0] for row in cursor.fetchall()}
    if file not in fixedfiles:
        fixCSV(folder / file, faultydescriptions, file)

    # Read the file
    with open(folder / file, newline="", encoding="utf-8-sig") as transaction:
        reader = csv.DictReader(transaction)
        rows = list(reader)
        daysequence = 1  # Initialize day sequence for each file
        lastDate = ""  # Initialize last date for each file

        # Iterate over each row
        for row in rows:
            # Add to database if it doesn't exist
                # Try to identify specific rows with problems
            try:
                # RS, CS, or MM
                if table == "accounts":
                    date = datetime.strptime(
                        row["Date"],
                        "%m/%d/%Y %I:%M:%S %p"
                    ).date()
                    if lastDate == date:
                        daysequence += 1
                    else:
                        daysequence = 1
                    amount = float(row["Amount"])
                    balance = float(row["Balance"])

                    # Check if row is already in database
                    cursor.execute("""
                        SELECT 1
                        FROM accounts
                        WHERE account = %s
                        AND date = %s
                        AND description = %s
                        AND amount = %s
                        LIMIT 1
                    """, (
                        account,
                        date,
                        row["Transaction Description"],
                        amount
                    ))

                    if cursor.fetchone():
                        continue

                    # Throw in database
                    cursor.execute("""
                    INSERT INTO accounts
                    (account, date, daysequence, description, amount, balance, checkmisc, note, category)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        account,
                        date,
                        daysequence,
                        row["Transaction Description"],
                        amount,
                        balance,
                        row["Check/Misc."],
                        row["Note"],
                        row["Category"]
                    ))

                    lastDate = date
                    conn.commit()
                elif table == "loans":
                    date = datetime.strptime(
                        row["Date"],
                        "%m/%d/%Y %I:%M:%S %p"
                    ).date()
                    if lastDate == date:
                        daysequence += 1
                    else:
                        daysequence = 1
                    amount = float(row["Principal"])
                    interest = float(row["Interest"])
                    fees = float(row["Fees"])
                    balance = float(row["Balance"])

                    # Check if row is already in database
                    cursor.execute("""
                        SELECT 1
                        FROM loans
                        WHERE date = %s
                        AND description = %s
                        AND amount = %s
                        LIMIT 1
                    """, (
                        date,
                        row["Transaction Description"],
                        amount
                    ))

                    if cursor.fetchone():
                        continue

                    # Throw in database
                    cursor.execute("""
                    INSERT INTO loans
                    (date, daysequence, description, amount, interest, fees, balance, checkmisc, note, category)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        date,
                        daysequence,
                        row["Transaction Description"],
                        amount,
                        interest,
                        fees,
                        balance,
                        row["Check/Misc."],
                        row["Note"],
                        row["Category"]
                    ))

                    lastDate = date
                    conn.commit()
            # Note descriptions with commas in them
            except Exception as e:
                print(f"FAILED ROW:\nP{row}\nERROR: repr{e}")
                # See if the description already exists in the faultydescriptions table
                cursor.execute("""
                SELECT 1 FROM faultydescriptions
                WHERE name = %s
                LIMIT 1
                """,
                (row["Transaction Description"],))

                exists = cursor.fetchone() is not None
                
                if not exists:
                    cursor.execute("""
                    INSERT INTO faultydescriptions (name) VALUES (%s)
                    """, 
                    (row["Transaction Description"],))

                    conn.commit()

                    print(f"{row['Transaction Description']} has a comma in it. It has been noted and the problem will not occur again. Try rerunning the script")
                
                sys.exit()