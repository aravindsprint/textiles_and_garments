import time
import sqlite3
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# SQLite database configuration
DB_FILE = '/Users/aravind/Projects/node/wms/wms.db'
# DB_FILE = '/home/node/wms/wms.db'

# Google Sheets API configuration
SERVICE_ACCOUNT_FILE = './praneraoms-daab053a10d2.json'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Initialize Google Sheets client
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(credentials)
spreadsheet = client.open_by_key("1vCVeL2DgtaWXEoEbMmeThj9K13BvZPwRw2mRA09fSMU")
worksheet = spreadsheet.get_worksheet(0)  # First worksheet

def sort_by_datetime_column(worksheet, col_index=16, range_start="A2", range_end="P"):
    # Fetch all data within the range
    all_data = worksheet.get_all_values()
    header = all_data[0]  # Keep the header row
    rows = all_data[1:]   # Exclude the header row

    # Parse the datetime column and sort rows
    try:
        rows.sort(key=lambda row: datetime.strptime(row[col_index - 1], "%Y-%m-%d %H:%M:%S.%f"))
    except ValueError:
        rows.sort(key=lambda row: datetime.strptime(row[col_index - 1], "%Y-%m-%d %H:%M:%S"))

    # Update the sorted data back to the sheet
    worksheet.update(range_start, [header] + rows)
    print("Sheet sorted successfully by column", col_index)

def get_last_modified_value_in_column_p(worksheet):
    col_values = worksheet.col_values(16)  # Column P is the 16th column (1-based index)
    latest_value = None
    latest_time = None

    for value in reversed(col_values):
        if value:
            try:
                # Try parsing with microseconds
                timestamp = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                try:
                    # If that fails, try parsing without microseconds
                    timestamp = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue  # Skip if it's not a valid datetime format

            # Update the latest value if the timestamp is more recent
            if latest_time is None or timestamp > latest_time:
                latest_time = timestamp
                latest_value = value

    return latest_value

def get_last_value_in_column_sorted(worksheet, col_index):
    col_values = worksheet.col_values(col_index)
    numeric_values = [float(value) for value in col_values if value.isdigit()]
    return int(max(numeric_values)) if numeric_values else None

while True:
    # Open database connection
    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()

        # Get the last modified value in column P
        last_value_modified = get_last_modified_value_in_column_p(worksheet)
        print("Last modified value in column P:", last_value_modified)

        query = """
        SELECT date, item_code, for_project, parent, commercial_name, color, requested_by, qty, uom, docstatus,
               finished_item_code, width, idx, id, creation, modified
        FROM material_request_item
        WHERE modified > ?
        ORDER BY modified ASC
        """

        query1 = """
        SELECT date, item_code, for_project, parent, commercial_name, color, requested_by, qty, uom, docstatus,
               finished_item_code, width, idx, id, creation, modified
        FROM material_request_item
        WHERE modified > ? and docstatus = 1
        ORDER BY modified ASC
        """
        cursor.execute(query, (last_value_modified,))
        new_rows_modified = cursor.fetchall()

        if new_rows_modified:
            print("new_rows_modified:", new_rows_modified)

            for db_row in new_rows_modified:
                db_value = db_row[13]  # 'id' field as unique identifier
                cell = worksheet.find(str(db_value))

                if cell:
                    row_index = cell.row
                    for col_index, value in enumerate(db_row):
                        if col_index == 14:  # Skip the 14th column
                            continue
                        worksheet.update_cell(row_index, col_index + 1, value)
                    print(f"Updated row {row_index} in Google Sheets.")
                    # Call the function
                    sort_by_datetime_column(worksheet)      
        else:
            last_value = get_last_value_in_column_sorted(worksheet, 13)
            print("Last value in column 13:", last_value)

            cursor.execute(query1, (last_value,))
            new_rows = cursor.fetchall()

            existing_values = worksheet.col_values(14)
            rows_to_insert = [row for row in new_rows if str(row[13]) not in existing_values]

            if rows_to_insert:
                worksheet.append_rows(rows_to_insert, value_input_option='RAW')
                print(f"Inserted {len(rows_to_insert)} new rows.")
                # Call the function
                sort_by_datetime_column(worksheet)
            else:
                print("No new rows to insert.")

    # Wait for 30 seconds before the next iteration
    time.sleep(30)
