import os
import pandas as pd
import gspread

google_sheet_id = os.getenv("GOOGLE_SHEET_ID")
google_credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
gc = gspread.service_account(google_credentials_path)
sh = gc.open_by_url(f"https://docs.google.com/spreadsheets/d/{google_sheet_id}")
worksheet = sh.worksheet("All")

def get_data_from_google_sheet():
    url = f"https://docs.google.com/spreadsheets/d/{google_sheet_id}/gviz/tq?tqx=out:csv&sheet=All"
    return pd.read_csv(url)

def insert_data_to_google_sheet(name, producer, type, grape, year, origin, quantity=1, description=""):
    worksheet.append_row([name, producer, type, grape, year, origin, quantity, description])

def update_quantity(row, delta):
    sheet_row = row + 2  # Skip header, and 0 indexing
    current_quantity = int(worksheet.cell(sheet_row, 7).value)
    new_quantity = max(current_quantity + delta, 0)
    worksheet.update_cell(sheet_row, 7, new_quantity)
