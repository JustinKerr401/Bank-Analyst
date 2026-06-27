@echo off
venv\Scripts\python.exe upload_transactions.py
venv\Scripts\python.exe graph.py
venv\Scripts\python.exe expenses.py
pause