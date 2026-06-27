# Bank Analyst

A personal finance analysis tool that imports bank activity from CSV files, stores it in a MySQL database, and visualizes account balances and net worth over time.

The project was built to make personal financial activity easier to understand. Rather than reviewing individual bank statements manually, Bank Analyst consolidates transaction history from multiple accounts and presents meaningful trends in a single visual view.

## Overview

Bank Analyst is a personal finance analytics tool that imports bank transaction history from CSV files, stores the data in a MySQL database, and provides interactive dashboards for analyzing both account balances and spending habits.

Instead of manually reviewing bank statements, Bank Analyst consolidates financial data from multiple accounts into a single database and generates visual reports that make it easier to understand long-term financial trends, monitor net worth, and identify where money is being spent.

Current dashboards include:

- Net worth and account balance visualization
- Expense analysis over customizable date ranges
- Spending by category
- Top merchants
- Largest individual purchases

## Features

* Imports transaction history from bank-provided CSV files
* Supports multiple account types through filename prefixes
* Stores processed transactions in a MySQL database
* Prevents duplicate transaction imports
* Handles malformed CSV rows caused by company names containing commas
* Automatically corrects known malformed merchant names during future imports
* Interactive Plotly dashboard for tracking net worth over time
* Interactive expense analysis dashboard with customizable date ranges
* Displays spending by category
* Displays highest-spending merchants
* Displays largest individual purchases
* Excludes internal account transfers from spending analytics
* Uses environment variables to keep database credentials out of source code

## Tech Stack

* Python
* MySQL
* Pandas
* Plotly
* SQLAlchemy
* PyMySQL
* mysql-connector-python
* python-dotenv
* Tkinter

ChatGPT was used as a development aid to help research concepts, troubleshoot issues, and fill in implementation gaps throughout the project.

## How It Works

1. Export transaction history CSV files from your bank.
2. Place the files in the `assets/` directory in the project root.
3. Ensure each filename begins with the correct account abbreviation.
4. Run the processing script to import new transactions into MySQL.
5. Launches:
   - **Net Worth Dashboard** to visualize account balances and overall net worth over time.
   - **Expense Dashboard** to analyze spending within a selected date range.

The Expense Dashboard allows users to choose any start and end dates before generating an interactive spending report that includes:

- Spending by category
- Top merchants
- Largest purchases
- Interactive charts with hover information, zooming, and export support

## Dashboards

### Net Worth Dashboard

Displays historical balances for:

- Regular Share
- Checking Share
- Money Market
- Visa Loan
- Total Net Worth

Features include:

- Interactive Plotly graphs
- Hover tooltips
- Zooming and panning
- Range slider
- Quick date selection buttons

---

### Expense Dashboard

Allows the user to select a custom date range before generating an interactive expense report.

The dashboard includes:

- Spending by category (pie chart)
- Top merchants (horizontal bar chart)
- Largest individual purchases (interactive table)

Internal transfers such as loan payments and transfers between personal accounts are automatically excluded so that spending reports reflect actual purchases.

### Duplication safety

The importer checks whether transactions are already stored before inserting them. This means CSV files can remain in the `assets/` folder indefinitely without creating duplicate database entries.

## Supported Account Prefixes

| Prefix | Account Type            |
| ------ | ----------------------- |
| `RS`   | Regular Share           |
| `CS`   | Checking Share          |
| `MM`   | Money Market            |
| `VL`   | Visa Loan / Credit Card |

Example filenames:

```text
RS.csv
CS 1-1 to 6-1.csv
MM January through June.csv
VL 2026 H1.csv
```

### File name restrictions

The file name must not exceed 31 characters. 
This would mean that the filename "VL 8-23-25 through 1-23-26.csv" works. Because it contains 31 characters, this format depicts the maximum length.

## CSV Format Requirements

The importer expects each CSV file to contain a specific set of column headers based on the account type. Files that do not match these formats may fail to import correctly.

### Regular Share (`RS`), Checking Share (`CS`), and Money Market (`MM`)

CSV files whose filenames begin with `RS`, `CS`, or `MM` **must** contain the following columns:

```text
Date,Transaction Description,Amount,Balance,Check/Misc.,Note,Category
```

### Visa Loan / Credit Card (`VL`)

CSV files whose filenames begin with `VL` **must** contain the following columns:

```text
Date,Transaction Description,Principal,Interest,Fees,Balance,Check/Misc.,Note,Category
```

These column names are required by the importer and should not be renamed or removed.

## CSV Parsing Notes

Some transaction descriptions include commas in company names. Since commas are also used as CSV separators, these entries can cause parsing errors.

The importer includes logic to identify these problematic descriptions, repair the affected row, and apply the correction to future instances of the same company. This keeps imports consistent while reducing the need for repeated manual cleanup.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/JustinKerr401/Bank-Analyst.git
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
│   ├── CS 1-1 to 6-1.csv
│   ├── MM 1-1 to 6-1.csv
│   └── VL 1-1 to 6-1.csv
├── .env
├── requirements.txt
└── ...
```

### 6. Run the project

Either run the bat file in File explorer or the terminal.

```bash
.\run.bat
```

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

* Allow users to assign categories to transactions marked as `Uncategorized`
* Docker Containerization

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
