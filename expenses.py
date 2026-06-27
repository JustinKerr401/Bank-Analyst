import os
import tkinter as tk
from tkinter import ttk, messagebox

import mysql.connector
import pandas as pd
from dotenv import load_dotenv

import plotly.graph_objects as go
from plotly.subplots import make_subplots

load_dotenv()

# -------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASS"),
        database=os.getenv("MYSQL_DB")
    )


# -------------------------------------------------
# DATE RANGE WINDOW
# -------------------------------------------------

def get_date_range():

    result = {}

    root = tk.Tk()
    root.title("Bank Analyst - Expense Analysis")
    root.geometry("350x240")
    root.resizable(False, False)

    frame = ttk.Frame(root, padding=15)
    frame.pack(fill="both", expand=True)

    ttk.Label(
        frame,
        text="Expense Analysis",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=(0, 10))

    ttk.Label(frame, text="Start Date (YYYY-MM-DD)").pack(anchor="w")

    start_entry = ttk.Entry(frame, width=25)
    start_entry.pack(fill="x")
    start_entry.insert(0, "2026-01-01")

    ttk.Label(frame, text="").pack()

    ttk.Label(frame, text="End Date (YYYY-MM-DD)").pack(anchor="w")

    end_entry = ttk.Entry(frame, width=25)
    end_entry.pack(fill="x")
    end_entry.insert(0, pd.Timestamp.today().strftime("%Y-%m-%d"))

    def analyze():

        start = start_entry.get().strip()
        end = end_entry.get().strip()

        if start == "" or end == "":
            messagebox.showerror(
                "Invalid Dates",
                "Please enter both dates."
            )
            return

        result["start"] = start
        result["end"] = end

        root.destroy()

    ttk.Button(
        frame,
        text="Analyze",
        command=analyze
    ).pack(pady=15)

    root.mainloop()

    return result["start"], result["end"]


# -------------------------------------------------
# SQL QUERIES
# -------------------------------------------------

FILTER = """
amount < 0
AND date BETWEEN %s AND %s

AND description NOT LIKE 'Transfer to%%'
AND description NOT LIKE 'Transfer from%%'
AND description NOT LIKE 'Member-to-Member%%'
"""

CATEGORY_QUERY = f"""
SELECT
    COALESCE(NULLIF(category,''),'Uncategorized') AS category,
    SUM(ABS(amount)) AS total
FROM accounts
WHERE {FILTER}
GROUP BY category
ORDER BY total DESC;
"""

MERCHANT_QUERY = f"""
SELECT
    description,
    SUM(ABS(amount)) AS total
FROM accounts
WHERE {FILTER}
GROUP BY description
ORDER BY total DESC
LIMIT 15;
"""

EXPENSE_QUERY = f"""
SELECT
    date,
    description,
    category,
    amount
FROM accounts
WHERE {FILTER}
ORDER BY amount ASC
LIMIT 20;
"""


# -------------------------------------------------
# LOAD SQL INTO DATAFRAME
# -------------------------------------------------

def load_dataframe(connection, query, start_date, end_date):

    df = pd.read_sql(
        query,
        connection,
        params=(start_date, end_date)
    )

    if "total" in df.columns:
        df["total"] = pd.to_numeric(df["total"])

    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"])

    return df

# -------------------------------------------------
# LOAD ANALYSIS DATA
# -------------------------------------------------

def load_analysis(start_date, end_date):

    conn = get_connection()

    try:

        categories = load_dataframe(
            conn,
            CATEGORY_QUERY,
            start_date,
            end_date
        )

        merchants = load_dataframe(
            conn,
            MERCHANT_QUERY,
            start_date,
            end_date
        )

        expenses = load_dataframe(
            conn,
            EXPENSE_QUERY,
            start_date,
            end_date
        )

    finally:
        conn.close()

    # -------------------------
    # Clean merchant names
    # -------------------------

    merchants["description"] = merchants["description"].apply(clean_merchant)
    expenses["description"] = expenses["description"].apply(clean_merchant)

    # -------------------------
    # Format dates
    # -------------------------

    expenses["date"] = pd.to_datetime(
        expenses["date"]
    ).dt.strftime("%Y-%m-%d")

    # -------------------------
    # Round money
    # -------------------------

    categories["total"] = categories["total"].round(2)
    merchants["total"] = merchants["total"].round(2)
    expenses["amount"] = expenses["amount"].round(2)

    return categories, merchants, expenses


# -------------------------------------------------
# BUILD TABLE
# -------------------------------------------------

def build_table(expenses):

    return go.Table(

        header=dict(

            values=[
                "<b>Date</b>",
                "<b>Merchant</b>",
                "<b>Category</b>",
                "<b>Amount</b>"
            ],

            align="left",
            font=dict(size=13),
            height=30

        ),

        cells=dict(

            values=[

                expenses["date"],
                expenses["description"],
                expenses["category"],
                expenses["amount"].map("${:,.2f}".format)

            ],

            align="left",
            height=25

        )

    )

# -------------------------------------------------
# BUILD DASHBOARD
# -------------------------------------------------

def build_dashboard(start_date, end_date,
                    categories,
                    merchants,
                    expenses):

    fig = make_subplots(

        rows=2,
        cols=2,

        specs=[
            [{"type": "domain"}, {"type": "xy"}],
            [{"type": "table", "colspan": 2}, None]
        ],

        subplot_titles=(

            "Spending by Category",
            "Top Merchants",
            "Largest Individual Expenses"

        ),

        vertical_spacing=0.12,
        horizontal_spacing=0.10
    )

    # ---------------------------------------
    # PIE CHART
    # ---------------------------------------

    top_categories = categories.head(8)

    fig.add_trace(

        go.Pie(

            labels=top_categories["category"],
            values=top_categories["total"],

            textinfo="label+percent",

            hovertemplate=

                "<b>%{label}</b><br>" +
                "$%{value:,.2f}<extra></extra>"

        ),

        row=1,
        col=1

    )

    # ---------------------------------------
    # TOP MERCHANTS
    # ---------------------------------------

    top_merchants = merchants.head(10)

    fig.add_trace(

        go.Bar(

            x=top_merchants["total"],
            y=top_merchants["description"],

            orientation="h",

            text=[
                f"${x:,.2f}"
                for x in top_merchants["total"]
            ],

            textposition="outside",

            hovertemplate=

                "<b>%{y}</b><br>" +
                "$%{x:,.2f}<extra></extra>"

        ),

        row=1,
        col=2

    )

    # Largest first

    fig.update_yaxes(

        autorange="reversed",

        row=1,
        col=2

    )

    # ---------------------------------------
    # TABLE
    # ---------------------------------------

    fig.add_trace(

        build_table(expenses),

        row=2,
        col=1

    )

    # ---------------------------------------
    # LAYOUT
    # ---------------------------------------

    fig.update_layout(

        title=dict(

            text=(
                f"<b>Expense Analysis</b>"
                f"<br><sup>{start_date} → {end_date}</sup>"
            ),

            x=0.5

        ),

        height=900,
        width=1400,

        showlegend=False,

        template="plotly_white"

    )

    # Better x-axis formatting

    fig.update_xaxes(

        title_text="Amount Spent ($)",

        tickprefix="$",

        row=1,
        col=2

    )

    return fig

# -------------------------------------------------
# IMPROVED MERCHANT CLEANING
# -------------------------------------------------

def clean_merchant(name):
    """
    Cleans merchant names for grouping.
    """

    if pd.isna(name):
        return ""

    name = str(name).strip().upper()

    replacements = {
        "TST*": "",
        "SQ *": "",
        "POS PURCHASE ": "",
        "DEBIT CARD PURCHASE ": "",
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    # Remove anything after (
    if "(" in name:
        name = name.split("(")[0]

    # Remove trailing store numbers
    # Example:
    # WAWA 8062 -> WAWA
    # ROYAL FARMS #234 -> ROYAL FARMS
    words = name.split()

    cleaned = []

    for word in words:

        if word.startswith("#"):
            break

        if word.isdigit():
            break

        cleaned.append(word)

    name = " ".join(cleaned)

    return name.title().strip()


# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():

    try:

        start_date, end_date = get_date_range()

        categories, merchants, expenses = load_analysis(
            start_date,
            end_date
        )

        fig = build_dashboard(
            start_date,
            end_date,
            categories,
            merchants,
            expenses
        )

        fig.show()

    except KeyboardInterrupt:
        pass

    except Exception as e:

        messagebox.showerror(
            "Expense Analysis",
            str(e)
        )


# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------

if __name__ == "__main__":
    main()