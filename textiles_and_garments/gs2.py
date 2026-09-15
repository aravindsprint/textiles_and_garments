import time

while True:
    # Your script logic here
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
    

    # https://docs.google.com/spreadsheets/d/1vCVeL2DgtaWXEoEbMmeThj9K13BvZPwRw2mRA09fSMU/edit?gid=1487265706#gid=1487265706
    # Open the Google Sheet
    # yasin sheet
    # 1vCVeL2DgtaWXEoEbMmeThj9K13BvZPwRw2mRA09fSMU
    # aravind sheet
    # 11L3JiqwHs4R-V5d8vH_Q9Da4MOrLCEpfF3-LipSDhD8

    spreadsheet = client.open_by_key("1vCVeL2DgtaWXEoEbMmeThj9K13BvZPwRw2mRA09fSMU")

    # spreadsheet = client.open_by_key("11L3JiqwHs4R-V5d8vH_Q9Da4MOrLCEpfF3-LipSDhD8")

    # Select the first worksheet
    worksheet = spreadsheet.get_worksheet(0)  # Index 0 refers to the first sheet

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

    # Get the last modified value in column P
    last_value_modified = get_last_modified_value_in_column_p(worksheet)
    print("Last modified value in column P:", last_value_modified)
    cursor = connection.cursor()
    query = f'SELECT date, item_code, for_project, parent, commercial_name, color, requested_by, qty, uom, docstatus, finished_item_code, width, idx, id, creation, modified FROM material_request_item WHERE modified > ? ORDER BY modified ASC'
    cursor.execute(query, (last_value_modified,))
    new_rows_modified = cursor.fetchall()

    if new_rows_modified:
        print("new_rows_modified:", new_rows_modified)

        # Iterate through the rows returned from the database
        for db_row in new_rows_modified:
            # Get the first column value (assuming it's the unique identifier like 'idx')
            print("\n\ndb_row[13]\n\n",db_row[13])
            db_value = db_row[13]  # Assuming the first column in the DB row is the unique identifier (idx)
           
            # Find the row in the Google Sheet that matches the value in the first column
            cell = worksheet.find(str(db_value))  # This will search for the value in the sheet
            
            if cell:  # If the value is found in the sheet
                print("\n\ncell.row\n\n",cell.row)
                row_index = cell.row  # Get the row number where the value was found

                # Update the values in the corresponding row (excluding the first column)
                # You can modify this based on the columns you want to update
                # Update the values in the corresponding row, skipping the 14th column
                for col_index, value in enumerate(db_row):
                    if col_index == 14:  # Skip the 14th column (0-based index)
                        continue
                    worksheet.update_cell(row_index, col_index + 1, value)  # Use col_index + 1 for 1-based indexing
                print(f"Updated row {row_index} in Google Sheets.")

    # def get_last_value_in_column_sorted(worksheet, col_index):
    #     col_values = worksheet.col_values(col_index)  # Get all values in the column
    #     print("Original column values:", col_values)

    #     # Filter out empty values and convert to numbers if possible
    #     numeric_values = []
    #     for value in col_values:
    #         try:
    #             numeric_values.append(float(value))  # Convert to float for sorting
    #         except ValueError:
    #             continue  # Skip non-numeric values

    #     # Sort the numeric values in ascending order
    #     numeric_values.sort()

    #     # Return the last (largest) value, or None if no numeric values exist
    #     return int(numeric_values[-1]) if numeric_values else None



    # last_value = get_last_value_in_column_sorted(worksheet, 13)  # Get the last value in column 1 (A)    
    # print("\n\nlast_value\n\n",last_value)

    # # Query the database for rows with IDs greater than the last value
    # cursor = connection.cursor()
    # query = f'SELECT date, item_code, for_project, parent, commercial_name, color, requested_by, qty, uom, docstatus, finished_item_code, width, idx, id, creation, modified FROM material_request_item WHERE modified > ? ORDER BY modified ASC'
    # cursor.execute(query, (last_value,))
    # new_rows = cursor.fetchall()

    # # Get all existing values in the first column of the Google Sheet
    # existing_values = worksheet.col_values(14)  # Column 1 is the first column (A)
    # print("\n\nexisting_values\n\n",existing_values)
    # # Close the database connection
    # connection.close()

    # # Prepare data for batch update
    # rows_to_insert = []

    # # Check if the idx value in new_rows already exists in the Google Sheet
    # for row in new_rows:
    #     idx_value = str(row[13])  # Assuming the first column in the row is the 'idx' value
    #     print("\n\nidx_value\n\n",idx_value)
    #     if idx_value not in existing_values:
    #         rows_to_insert.append(row)  # Add the row to insert if idx is not found in the existing values

    # # Insert new rows only if there are rows to insert
    # if rows_to_insert:
    #     worksheet.append_rows(rows_to_insert, value_input_option='RAW')  # Append all rows in one request
    #     print(f"Inserted {len(rows_to_insert)} new rows.")
    # else:
    #     print("No new rows to insert.")


    # print(f"Appended {len(new_rows)} rows successfully to Google Sheets.")

    # Wait for 5 minutes (300 seconds)
    time.sleep(30)
