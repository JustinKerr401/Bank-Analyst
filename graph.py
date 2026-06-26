import os
import mysql.connector
import pandas as pd
from dotenv import load_dotenv
import plotly.graph_objects as go

load_dotenv()

# ----------------------------
# 1. CONNECT VIA ENV VARS
# ----------------------------
conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASS"),
    database=os.getenv("MYSQL_DB")
)

# ----------------------------
# 2. LOAD DATA
# ----------------------------
accounts_query = """
SELECT id, date, account, balance
FROM accounts
"""

loans_query = """
SELECT date, balance
FROM loans
"""

accounts = pd.read_sql(accounts_query, conn)
loans = pd.read_sql(loans_query, conn)

conn.close()

# ----------------------------
# 3. CLEAN DATA (DATE ONLY)
# ----------------------------
accounts["date"] = pd.to_datetime(accounts["date"]).dt.date
loans["date"] = pd.to_datetime(loans["date"]).dt.date

# ----------------------------
# 4. DEDUPE SAFELY
# ----------------------------
accounts = accounts.sort_values(["date", "account", "id"])
accounts = accounts.drop_duplicates(subset=["date", "account"], keep="first")

# ----------------------------
# 5. PIVOT ACCOUNTS
# ----------------------------
accounts_pivot = (
    accounts.pivot_table(
        index="date",
        columns="account",
        values="balance",
        aggfunc="last"
    )
    .sort_index()
    .ffill()
)

# safety: remove duplicate index if any
accounts_pivot = accounts_pivot[~accounts_pivot.index.duplicated(keep="first")]

# ----------------------------
# 6. LOANS (NEGATIVE)
# ----------------------------
loans_series = (
    loans.sort_values("date")
    .set_index("date")["balance"]
)

loans_series.index = pd.to_datetime(loans_series.index).date
loans_series = -loans_series

loans_series = loans_series[~loans_series.index.duplicated(keep="first")]

# ----------------------------
# 7. ALIGN DATA
# ----------------------------
combined_index = accounts_pivot.index.union(loans_series.index)

accounts_pivot = accounts_pivot.reindex(combined_index).ffill()
loans_series = loans_series.reindex(combined_index).ffill()

loans_series.name = "Visa Loan"

# ----------------------------
# 8. TOTAL CALCULATION
# ----------------------------
combined = accounts_pivot.copy()
combined["Visa Loan"] = loans_series

combined["Total"] = (
    combined.get("rs", 0) +
    combined.get("cs", 0) +
    combined.get("mm", 0) +
    combined["Visa Loan"]
)

# ----------------------------
# 9. FIND TUESDAYS (PAYDAYS)
# ----------------------------
combined = combined.copy()
combined.index = pd.to_datetime(combined.index)

tuesdays = combined[combined.index.weekday == 1]

tuesday_totals = tuesdays["Total"]
tuesday_diff = tuesday_totals.diff()
tuesday_days = tuesday_totals.index.to_series().diff().dt.days

# ----------------------------
# 10. PLOT (INTERACTIVE)
# ----------------------------
fig = go.Figure()

# Account lines (hover enabled automatically)
fig.add_trace(go.Scatter(
    x=combined.index,
    y=combined.get("rs"),
    mode="lines",
    name="Regular Share",
    line=dict(width=2, color="blue")
))

fig.add_trace(go.Scatter(
    x=combined.index,
    y=combined.get("cs"),
    mode="lines",
    name="Checking Share",
    line=dict(width=2, color="gold")
))

fig.add_trace(go.Scatter(
    x=combined.index,
    y=combined.get("mm"),
    mode="lines",
    name="Money Market",
    line=dict(width=2, color="green")
))

fig.add_trace(go.Scatter(
    x=combined.index,
    y=combined["Visa Loan"],
    mode="lines",
    name="Visa Loan",
    line=dict(width=2, color="red")
))

fig.add_trace(go.Scatter(
    x=combined.index,
    y=combined["Total"],
    mode="lines",
    name="Total",
    line=dict(width=4, color="black")
))

# ----------------------------
# 11. TUESDAY VERTICAL LINES
# ----------------------------
for t in tuesdays.index:
    fig.add_vline(
        x=t,
        line_width=1,
        line_dash="dot",
        line_color="gray"
    )

# ----------------------------
# 12. ANNOTATE PAYCHECK DIFFERENCES
# ----------------------------
y_top = combined["Total"].max()
y_offset = (combined["Total"].max() - combined["Total"].min()) * 0.04

for i in range(1, len(tuesday_totals)):
    date = tuesday_totals.index[i]
    diff = tuesday_diff.iloc[i]
    days = int(tuesday_days.iloc[i])

    # Days since previous Tuesday
    fig.add_annotation(
        x=date,
        y=y_top + y_offset,
        text=f"{days} days",
        showarrow=False,
        font=dict(
            size=11,
            color="gray"
        )
    )

    # Money gained/lost
    fig.add_annotation(
        x=date,
        y=y_top,
        text=f"{diff:+.2f}",
        showarrow=False,
        font=dict(
            size=12,
            color="green" if diff >= 0 else "red"
        )
    )

# ----------------------------
# 13. LAYOUT + HOVER SETTINGS
# ----------------------------
fig.update_layout(
    title="Net Worth Over Time",
    xaxis_title="Date",
    yaxis_title="Balance ($)",
    hovermode="x unified",
    xaxis=dict(
        rangeslider=dict(visible=True),
        rangeselector=dict(
            buttons=[
                dict(count=1, label="1 Month", step="month", stepmode="backward"),
                dict(count=3, label="3 Months", step="month", stepmode="backward"),
                dict(count=6, label="6 Months", step="month", stepmode="backward"),
                dict(count=1, label="1 Year", step="year", stepmode="backward"),
                dict(step="all", label="All"),
            ]
        )
    )
)

fig.show()