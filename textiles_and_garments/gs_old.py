

# import sqlite3
# import gspread
# from google.oauth2.service_account import Credentials

# # SQLite database configuration
# db_file = '/Users/aravind/Projects/node/wms/wms.db'
# connection = sqlite3.connect(db_file)

# # Create a cursor object to interact with the database
# cursor = connection.cursor()

# # Query data from the table
# cursor.execute('SELECT * FROM material_request_item WHERE id = "19b52uvqed"')
# rows = cursor.fetchall()

# # Close the database connection
# connection.close()

# # Google Sheets API configuration
# SERVICE_ACCOUNT_FILE = './praneraoms-daab053a10d2.json'
# SCOPES = [
#     'https://www.googleapis.com/auth/spreadsheets',
#     'https://www.googleapis.com/auth/drive'
# ]

# credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# client = gspread.authorize(credentials)

# # Open the Google Sheet
# spreadsheet = client.open_by_key("11L3JiqwHs4R-V5d8vH_Q9Da4MOrLCEpfF3-LipSDhD8")

# # Select the first worksheet
# worksheet = spreadsheet.get_worksheet(0)  # Index 0 refers to the first sheet

# # Update the row values into Google Sheets
# for index, row in enumerate(rows, start=2):  # Start from row 1 in Google Sheets
#     # Update each column in the row
#     for col_index, value in enumerate(row, start=1):  # Start from column 1
#         cell = worksheet.cell(index, col_index)
#         worksheet.update_cell(index, col_index, value)

# print("Data updated successfully in Google Sheets.")


import time
import sqlite3
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# SQLite database configuration
db_file = '/Users/aravind/Projects/node/wms/wms.db'
# db_file = '/home/node/wms/wms.db'
connection = sqlite3.connect(db_file)

# Google Sheets API configuration
SERVICE_ACCOUNT_FILE = './praneraoms-daab053a10d2.json'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(credentials)

# Open the Google Sheet
spreadsheet = client.open_by_key("1vCVeL2DgtaWXEoEbMmeThj9K13BvZPwRw2mRA09fSMU")
worksheet = spreadsheet.get_worksheet(0)  # Select the first worksheet

def get_last_modified_value_in_column_p(worksheet):
    col_values = worksheet.col_values(16)  # Column P is the 16th column (1-based index)
    
    # Initialize a variable to store the latest timestamp
    latest_value = None
    latest_time = None

    # Iterate through the column from the last value to the first
    for value in reversed(col_values):
        if value:  # Check if the value is non-empty
            try:
                # Parse the timestamp string into a datetime object
                timestamp = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
                
                # Update the latest timestamp if this one is more recent
                if latest_time is None or timestamp > latest_time:
                    latest_time = timestamp
                    latest_value = value
            except ValueError:
                # Handle the case where the value is not a valid timestamp
                continue

    return latest_value  # Return the last modified timestamp or None if no valid value is found

def retry_with_backoff(func, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            return func()
        except gspread.exceptions.APIError as e:
            if e.response.status_code == 429:  # Rate limit exceeded
                retries += 1
                wait_time = 2 ** retries  # Exponential backoff
                print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("Max retries reached. Could not complete the operation.")

# Function to update multiple cells at once
def update_cells_in_batch(worksheet, rows_to_insert):
    cell_updates = []
    for row_index, db_row in enumerate(rows_to_insert, start=2):
        for col_index, value in enumerate(db_row[1:], start=2):  # Skip the first column
            cell_updates.append(gspread.models.Cell(row_index, col_index, value))

    # Update all cells in one go
    retry_with_backoff(lambda: worksheet.update_cells(cell_updates))

# Main loop to check for updates and write to Google Sheets
while True:
    # Get the last modified value in column P
    last_value_modified = get_last_modified_value_in_column_p(worksheet)
    print("Last modified value in column P:", last_value_modified)

    cursor = connection.cursor()
    query = f'SELECT date, item_code, for_project, parent, commercial_name, color, requested_by, qty, uom, docstatus, finished_item_code, width, idx, id, creation, modified FROM material_request_item WHERE modified > ? ORDER BY modified ASC'
    cursor.execute(query, (last_value_modified,))
    new_rows_modified = cursor.fetchall()

    if new_rows_modified:
        print("new_rows_modified:", new_rows_modified)

        # Prepare data for batch update
        rows_to_insert = []

        # Iterate through the rows returned from the database
        for db_row in new_rows_modified:
            db_value = db_row[0]  # Assuming the first column in the DB row is the unique identifier (idx)

            # Find the row in the Google Sheet that matches the value in the first column
            cell = worksheet.find(str(db_value))  # This will search for the value in the sheet

            if cell:  # If the value is found in the sheet
                row_index = cell.row  # Get the row number where the value was found

                # Update the values in the corresponding row (excluding the first column)
                for col_index, value in enumerate(db_row[1:], start=2):  # Start from column 2 to skip the first column
                    worksheet.update_cell(row_index, col_index, value)
                print(f"Updated row {row_index} in Google Sheets.")

    def get_last_value_in_column_sorted(worksheet, col_index):
        col_values = worksheet.col_values(col_index)  # Get all values in the column
        print("Original column values:", col_values)

        # Filter out empty values and convert to numbers if possible
        numeric_values = []
        for value in col_values:
            try:
                numeric_values.append(float(value))  # Convert to float for sorting
            except ValueError:
                continue  # Skip non-numeric values

        # Sort the numeric values in ascending order
        numeric_values.sort()

        # Return the last (largest) value, or None if no numeric values exist
        return int(numeric_values[-1]) if numeric_values else None

    last_value = get_last_value_in_column_sorted(worksheet, 13)  # Get the last value in column 13 (M)    
    print("\n\nlast_value\n\n", last_value)

    # Query the database for rows with IDs greater than the last value
    cursor.execute(f'SELECT date, item_code, for_project, parent, commercial_name, color, requested_by, qty, uom, docstatus, finished_item_code, width, idx, id, creation, modified FROM material_request_item WHERE modified > ? ORDER BY modified ASC', (last_value,))
    new_rows = cursor.fetchall()

    # Get all existing values in the first column of the Google Sheet
    existing_values = worksheet.col_values(14)  # Column 14 is the 14th column (N)
    print("\n\nexisting_values\n\n", existing_values)

    # Prepare data for batch insert
    rows_to_insert = []
    for row in new_rows:
        idx_value = str(row[13])  # Assuming the first column in the row is the 'idx' value
        print("\n\nidx_value\n\n", idx_value)
        if idx_value not in existing_values:
            rows_to_insert.append(row)  # Add the row to insert if idx is not found in the existing values

    # Insert new rows only if there are rows to insert
    if rows_to_insert:
        retry_with_backoff(lambda: worksheet.append_rows(rows_to_insert, value_input_option='RAW'))  # Append all rows in one request
        print(f"Inserted {len(rows_to_insert)} new rows.")
    else:
        print("No new rows to insert.")

    print(f"Appended {len(new_rows)} rows successfully to Google Sheets.")

    # Wait for 5 minutes (300 seconds) before the next iteration
    time.sleep(300)


# import time
# import sqlite3
# import gspread
# from google.oauth2.service_account import Credentials
# from datetime import datetime

# # SQLite database configuration
# db_file = '/Users/aravind/Projects/node/wms/wms.db'
# connection = sqlite3.connect(db_file)

# # Google Sheets API configuration
# SERVICE_ACCOUNT_FILE = './praneraoms-daab053a10d2.json'
# SCOPES = [
#     'https://www.googleapis.com/auth/spreadsheets',
#     'https://www.googleapis.com/auth/drive'
# ]

# credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# client = gspread.authorize(credentials)

# # Open the Google Sheet
# spreadsheet = client.open_by_key("1vCVeL2DgtaWXEoEbMmeThj9K13BvZPwRw2mRA09fSMU")
# worksheet = spreadsheet.get_worksheet(0)  # Select the first worksheet

# def retry_with_backoff(func, *args, retries=5):
#     delay = 1  # Start with 1 second
#     for attempt in range(retries):
#         try:
#             return func(*args)
#         except gspread.exceptions.APIError as e:
#             if e.response.status_code == 429:  # Quota exceeded
#                 print(f"Quota exceeded. Retrying in {delay} seconds...")
#                 time.sleep(delay)
#                 delay *= 2  # Exponential backoff
#             else:
#                 raise
#     raise Exception("Max retries exceeded")

# def get_last_modified_value_in_column_p(worksheet):
#     col_values = worksheet.col_values(16)  # Column P is the 16th column (1-based index)
#     latest_value = None
#     latest_time = None

#     for value in reversed(col_values):
#         if value:
#             try:
#                 timestamp = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
#                 if latest_time is None or timestamp > latest_time:
#                     latest_time = timestamp
#                     latest_value = value
#             except ValueError:
#                 continue

#     return latest_value

# last_value_modified = get_last_modified_value_in_column_p(worksheet)
# print("Last modified value in column P:", last_value_modified)

# cursor = connection.cursor()
# query = f'SELECT date, item_code, for_project, parent, commercial_name, color, requested_by, qty, uom, docstatus, finished_item_code, width, idx, id, creation, modified FROM material_request_item WHERE modified > ? ORDER BY modified ASC'
# cursor.execute(query, (last_value_modified,))
# new_rows_modified = cursor.fetchall()

# if new_rows_modified:
#     print("New rows modified:", new_rows_modified)
#     batch_updates = []

#     for db_row in new_rows_modified:
#         db_value = db_row[0]
#         cell = retry_with_backoff(worksheet.find, str(db_value))

#         if cell:
#             row_index = cell.row
#             for col_index, value in enumerate(db_row[1:], start=2):
#                 batch_updates.append({
#                     'range': f'{chr(64 + col_index)}{row_index}',
#                     'values': [[value]]
#                 })

#     if batch_updates:
#         retry_with_backoff(worksheet.batch_update, batch_updates)
#         print(f"Batch updated {len(batch_updates)} cells.")

# # Handle new rows to append
# def get_last_value_in_column(worksheet, col_index):
#     col_values = worksheet.col_values(col_index)
#     if col_values:
#         return col_values[-1]
#     return None

# last_value = get_last_value_in_column(worksheet, 13)
# cursor.execute(query, (last_value,))
# new_rows = cursor.fetchall()
# existing_values = worksheet.col_values(13)
# connection.close()

# rows_to_insert = []
# for row in new_rows:
#     idx_value = str(row[13])
#     if idx_value not in existing_values:
#         rows_to_insert.append(row)

# if rows_to_insert:
#     retry_with_backoff(worksheet.append_rows, rows_to_insert, value_input_option='RAW')
#     print(f"Inserted {len(rows_to_insert)} new rows.")
# else:
#     print("No new rows to insert.")

# print("Script execution completed.")

# # Wait for 5 minutes (300 seconds)
# time.sleep(300)




# # Check the worksheets
# worksheets = spreadsheet.worksheets()
# for ws in worksheets:
#     print(ws.title)


