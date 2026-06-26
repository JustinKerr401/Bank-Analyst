import os
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Connect to the database
conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASS"),
    database=os.getenv("MYSQL_DB")
)
cursor = conn.cursor()

def fixCSV(file_path, faultydescriptions, file):
    
    fixedDescriptions = []
    temp_file = file_path.with_suffix(".tmp")

    with open(file_path, "r", newline="", encoding="utf-8-sig") as infile, \
        open(temp_file, "w", newline="", encoding="utf-8") as outfile:

        for line in infile:
            for description in faultydescriptions:
                toFix = description + ",,"
                if toFix in line:
                    line = line.replace(toFix, description+",")
                    if description not in fixedDescriptions:
                        fixedDescriptions.append(description)

            outfile.write(line)

    # Delete original (problematic) file
    if file_path.exists():
        os.remove(file_path)

    # Rename temp file to take place of original file
    os.rename(temp_file, file_path)

    # Add file to list of fixed files
    cursor.execute("""
    INSERT INTO fixedfiles (filename) VALUES (%s)
    """, 
    (str(file),))

    conn.commit()