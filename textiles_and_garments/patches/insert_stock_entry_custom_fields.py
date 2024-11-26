import frappe

def execute():
    # Step 1: Fetch all stock entries with a value in the work_order field
    stock_entries = frappe.get_all(
        "Stock Entry",
        fields=["name", "work_order", "docstatus"],
        filters={"work_order": ["is", "set"]},
    )

    for stock_entry in stock_entries:
        # Skip cancelled stock entries
        if stock_entry.docstatus == 2:
            print(f"Skipping cancelled stock entry: {stock_entry.name}")
            continue  # Skip the cancelled entry

        # Step 2: Create a new "Stock Entry Custom Fields" record for each stock entry
        custom_field = frappe.get_doc({
            "doctype": "Stock Entry Custom Fields",
            "parent": stock_entry.name,  # Link the Stock Entry as the parent
            "parenttype": "Stock Entry",  # Specify the parent type
            "parentfield": "custom_stock_entry_custom_fields",  # Correct parent field name for the child table
            "work_order": stock_entry.work_order,  # Set the work_order field
            "stock_entry": stock_entry.name
        })

        # Step 3: Insert the new record into the database
        custom_field.insert(ignore_permissions=True)

        print("\n\ncustom_field\n\n", custom_field.name)

        # Step 4: Append the new custom field to the child table of Stock Entry
        stock_entry_doc = frappe.get_doc("Stock Entry", stock_entry.name)
        stock_entry_doc.append("custom_stock_entry_custom_fields", {
            "name": custom_field.name,  # Add the reference to the new custom field in the child table
            "work_order": stock_entry.work_order,
            "stock_entry": stock_entry.name
        })

        # Save the Stock Entry document with the updated child table
        stock_entry_doc.save()

    # Step 5: Commit changes to the database
    frappe.db.commit()

   