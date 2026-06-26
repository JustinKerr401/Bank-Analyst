# Bank Analyst

A personal finance analysis tool that imports bank activity from CSV files, stores it in a MySQL database, and visualizes account balances and net worth over time.

The project was built to make personal financial activity easier to understand. Rather than reviewing individual bank statements manually, Bank Analyst consolidates transaction history from multiple accounts and presents meaningful trends in a single visual view.

## Overview

Bank Analyst processes exported CSV files from a bank, stores the transaction data in MySQL, and generates descriptive visualizations for:

* Regular Share account balances
* Checking Share account balances
* Money Market account balances
* Visa Loan / credit card balances
* Total net worth across all tracked accounts

The resulting graphs make it easier to identify how account balances change over time and provide a clearer picture of overall financial progress.

## Features

* Imports transaction history from bank-provided CSV files
* Supports multiple account types through filename prefixes
* Stores processed transactions in a MySQL database
* Avoids inserting duplicate transactions already stored in the database
* Allows CSV files to remain in the project for future reference
* Handles malformed CSV rows caused by company names containing commas
* Corrects future occurrences of known problematic company names during processing
* Visualizes account balances and total net worth over time
* Uses environment variables to keep database credentials out of source code

## Tech Stack

* Python
* MySQL
* Pandas
* Matplotlib
* Plotly
* SQLAlchemy
* PyMySQL
* `mysql-connector-python`
* `python-dotenv`

ChatGPT was used as a development aid to help research concepts, troubleshoot issues, and fill in implementation gaps throughout the project.

## How It Works

1. Export transaction history CSV files from your bank.
2. Place the files in the `assets/` directory in the project root.
3. Ensure each filename begins with the correct account abbreviation.
4. Run the processing script to import new transactions into MySQL.
5. Run the graphing application to view account history and net-worth trends.

The importer checks whether transactions are already stored before inserting them. This means CSV files can remain in the `assets/` folder indefinitely without creating duplicate database entries.

For example, a file named:

```text
CS 1-24 to 6-24.csv
```

indicates that it contains Checking Share account activity from January 2024 through June 2024.

## Supported Account Prefixes

| Prefix | Account Type            |
| ------ | ----------------------- |
| `RS`   | Regular Share           |
| `CS`   | Checking Share          |
| `MM`   | Money Market            |
| `VL`   | Visa Loan / Credit Card |

Example filenames:

```text
RS 1-24 to 6-24.csv
CS 1-24 to 6-24.csv
MM 1-24 to 6-24.csv
VL 1-24 to 6-24.csv
```

## CSV Parsing Notes

Some transaction descriptions include commas in company names. Since commas are also used as CSV separators, these entries can cause parsing errors.

The importer includes logic to identify these problematic descriptions, repair the affected row, and apply the correction to future instances of the same company. This keeps imports consistent while reducing the need for repeated manual cleanup.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/Bank-Analyst.git
cd Bank-Analyst
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
MYSQL_PASS=your_mysql_password
MYSQL_USER=your_mysql_username
MYSQL_HOST=localhost
MYSQL_DB=your_database_name
```

Do not commit your `.env` file to GitHub.

### 5. Add bank CSV files

Create an `assets/` folder in the project directory if it does not already exist.

```text
Bank-Analyst/
├── assets/
│   ├── CS 1-24 to 6-24.csv
│   ├── MM 1-24 to 6-24.csv
│   └── VL 1-24 to 6-24.csv
├── .env
├── requirements.txt
└── ...
```

### 6. Run the project

Run the appropriate scripts to create tables, process CSV files, and display the account graphs.

```bash
python create_table.py
python process_csv.py
python graph.py
```

> Script names may vary depending on the current project structure.

## Requirements

The project currently uses the following Python packages:

```text
contourpy==1.3.3
cycler==0.12.1
fonttools==4.63.0
greenlet==3.5.2
kiwisolver==1.5.0
matplotlib==3.11.0
mysql-connector-python==9.7.0
narwhals==2.22.1
numpy==2.5.0
packaging==26.2
pandas==3.0.3
pillow==12.2.0
plotly==6.8.0
PyMySQL==1.2.0
pyparsing==3.3.2
python-dateutil==2.9.0.post0
python-dotenv==1.2.2
six==1.17.0
SQLAlchemy==2.0.51
typing_extensions==4.15.0
tzdata==2026.2
```

## Planned Improvements

* Display the most common expenses by month, average spending, category, and company
* Allow users to assign categories to transactions marked as `Uncategorized`
* Allow users to select an existing category or create a new category for a company
* Containerize the application with Docker to improve portability and simplify setup
* Continue improving graph controls and financial-statistics displays

## Privacy and Security

This project is intended for personal financial analysis.

Do not commit any of the following to the repository:

* `.env` files
* Database passwords or credentials
* Bank CSV exports
* Database backups or SQL dumps
* Screenshots containing account balances or transaction details
* Logs containing personal financial information

Use a `.gitignore` file to keep local financial data and credentials out of version control.

## License

This project is currently intended for personal and educational use.
