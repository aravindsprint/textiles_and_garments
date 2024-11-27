import frappe

def execute():
    # Step 1: Define the date range for filtering
    start_date = "2024-06-01"  # Replace with your desired start date
    end_date = "2024-12-31"    # Replace with your desired end date

    # Step 2: Fetch all affected Stock Entries within the specified posting_date range
    stock_entries = frappe.get_all(
        "Stock Entry",
        fields=["*"],
        filters={
            "posting_date": ["between", [start_date, end_date]]
        },
    )

    for stock_entry in stock_entries:
        try:
            # Skip cancelled stock entries
            if stock_entry.docstatus == 2:
                print(f"Skipping cancelled stock entry: {stock_entry.name}")
                continue  # Skip the cancelled entry

            # Step 3: Delete all associated "Stock Entry Custom Fields" records
            custom_fields = frappe.get_all(
                "Stock Entry Custom Fields",
                filters={"parent": stock_entry.name},
                fields=["name"]
            )

            for custom_field in custom_fields:
                frappe.delete_doc("Stock Entry Custom Fields", custom_field.name, ignore_permissions=True)
                print(f"Deleted custom field: {custom_field.name}")

            # Step 4: Remove all entries in the "custom_stock_entry_custom_fields" child table
            stock_entry_doc = frappe.get_doc("Stock Entry", stock_entry.name)
            stock_entry_doc.custom_stock_entry_custom_fields = []

            # Save the Stock Entry document with the updated child table
            stock_entry_doc.save()
            print(f"Cleared custom fields for stock entry: {stock_entry.name}")

        except Exception as e:
            print(f"Error processing stock entry {stock_entry.name}: {e}")

    # Step 5: Commit changes to the database
    frappe.db.commit()
    print("Reversion process completed.")
