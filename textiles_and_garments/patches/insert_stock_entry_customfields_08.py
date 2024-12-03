import frappe

def execute():
    import frappe

    # Define the date range for filtering
    start_date = "2018-01-01"  # Replace with your desired start date
    end_date = "2018-12-31"    # Replace with your desired end date

    # Fetch all stock entries with the specified posting_date range
    stock_entries = frappe.get_all(
        "Stock Entry",
        fields=["*"],
        filters={
            "posting_date": ["between", [start_date, end_date]],
        },
    )

    for stock_entry in stock_entries:
        try:
            # Skip cancelled stock entries
            if stock_entry.docstatus == 2:
                print(f"Skipping cancelled stock entry: {stock_entry.name}")
                continue

            # Fetch the full Stock Entry document
            stock_entry_doc = frappe.get_doc("Stock Entry", stock_entry.name)

            # Check if a row already exists in the child table
            existing_row = next(
                (
                    row for row in stock_entry_doc.custom_stock_entry_custom_fields
                    if row.parent == stock_entry.name
                ),
                None
            )

            if existing_row:
                print(f"Skipping Stock Entry {stock_entry.name}, as it already has a row in custom_stock_entry_custom_fields.")
                continue

            # Prepare data for the new row
            child_row_data = {
                "parent": stock_entry.name,
                "parenttype": "Stock Entry",
                "parentfield": "custom_stock_entry_custom_fields",
            }

            # List of fields to copy
            fields_to_copy = [
                "work_order", "stock_entry", "gg", "gsm", "city", "team", "gstin", "state",
                "colour", "lot_no", "remark", "address", "quantity", "attention", "eway_bill",
                "lr_number", "reference", "dyeing_lot", "wo_texture", "dyeing_unit",
                "fabric_name", "loop_length", "no_of_rolls", "approved_lab", "custom_po_no",
                "customer_name", "finishingdia", "from_address", "knitting_dia", "address_line1",
                "address_line2", "countable_uom", "finishing_dia", "finishing_gsm", "knitting_unit",
                "finishing_unit", "party_dc_number", "submitted_date", "value_of_goods",
                "vehicle_number", "wo_required_gg", "wo_required_ll", "customer_mobile",
                "wo_no_of_course", "wo_required_dia", "wo_required_gsm", "fabric_reference",
                "wo_no_of_needles", "lot_received_date", "lab_dip_approval_no", 
                "no_of_countable_unit", "total_quantity_weight_in_kgs", "custom_default_no_of_rolls"
            ]

            # Copy fields if they exist and are not None
            for field in fields_to_copy:
                child_row_data[field] = stock_entry.get(field) or None

            # Append the new row to the child table
            stock_entry_doc.append("custom_stock_entry_custom_fields", child_row_data)

            # Add required fields for saving Stock Entry
            if not stock_entry_doc.party_dc_numer:
                stock_entry_doc.party_dc_numer = "-"
            if not stock_entry_doc.value_of_goods:
                stock_entry_doc.value_of_goods = "0"
            if not stock_entry_doc.vehicle_number:
                stock_entry_doc.vehicle_number = "-"

            # Save the Stock Entry document with the updated child table
            stock_entry_doc.save()
            frappe.db.commit()  # Commit changes after each save
            print(f"Row added to Stock Entry {stock_entry.name}")

        except Exception as e:
            # Log the error and continue processing
            print(f"Error processing stock entry {stock_entry.name}: {e}")
            frappe.db.rollback()  # Rollback changes for the current stock entry


   