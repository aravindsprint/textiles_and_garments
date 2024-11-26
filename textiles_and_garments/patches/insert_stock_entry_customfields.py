import frappe

def execute():
    # Step 1: Fetch all stock entries with a value in the work_order field
    stock_entries = frappe.get_all(
        "Stock Entry",
        fields=["*"],
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
            # "work_order": stock_entry.work_order,  # Set the work_order field
            "stock_entry": stock_entry.name,
            "gg":stock_entry.gg,
            "gsm":stock_entry.gsm,
            "city":stock_entry.city,
            "team":stock_entry.team,
            "gstin":stock_entry.gstin,
            "state":stock_entry.state,
            "colour":stock_entry.colour,
            "lot_no":stock_entry.lot_no,
            "remark":stock_entry.remark,
            "address":stock_entry.address,
            "quantity":stock_entry.quantity,
            "attention":stock_entry.attention,
            "eway_bill":stock_entry.eway_bill,
            "lr_number":stock_entry.lr_number,
            "reference":stock_entry.reference,
            "dyeing_lot":stock_entry.dyeing_lot,
            "wo_texture":stock_entry.wo_texture,
            "dyeing_unit":stock_entry.dyeing_unit,
            "fabric_name":stock_entry.fabric_name,
            "loop_length":stock_entry.loop_length,
            "no_of_rolls":stock_entry.no_of_rolls,
            "approved_lab":stock_entry.approved_lab,
            "custom_po_no":stock_entry.custom_po_no,
            "customer_name":stock_entry.customer_name,
            "finishingdia":stock_entry.finishingdia,
            "from_address":stock_entry.from_address,
            "knitting_dia":stock_entry.knitting_dia,
            "address_line1":stock_entry.address_line1,
            "address_line2":stock_entry.address_line2,
            "countable_uom":stock_entry.countable_uom,
            "finishing_dia":stock_entry.finishing_dia,
            "finishing_gsm":stock_entry.finishing_gsm,
            "knitting_unit":stock_entry.knitting_unit,
            "finishing_unit":stock_entry.finishing_unit,
            "party_dc_number":stock_entry.party_dc_number,
            "submitted_date":stock_entry.submitted_date,
            "value_of_goods":stock_entry.value_of_goods,
            "vehicle_number":stock_entry.vehicle_number,
            "wo_required_gg":stock_entry.wo_required_gg,
            "wo_required_ll":stock_entry.wo_required_ll,
            "customer_mobile":stock_entry.customer_mobile,
            "wo_no_of_course":stock_entry.wo_no_of_course,
            "wo_required_dia":stock_entry.wo_required_dia,
            "wo_required_gsm":stock_entry.wo_required_gsm,
            "fabric_reference":stock_entry.fabric_reference,
            "wo_no_of_needles":stock_entry.wo_no_of_needles,
            "lot_received_date":stock_entry.lot_received_date,
            "lab_dip_approval_no":stock_entry.lab_dip_approval_no,
            "no_of_countable_unit":stock_entry.no_of_countable_unit,
            "total_quantity_weight_in_kgs":stock_entry.total_quantity_weight_in_kgs,
            "custom_default_no_of_rolls":stock_entry.custom_default_no_of_rolls
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
               "gg":stock_entry.gg,
            "gsm":stock_entry.gsm,
            "city":stock_entry.city,
            "team":stock_entry.team,
            "gstin":stock_entry.gstin,
            "state":stock_entry.state,
            "colour":stock_entry.colour,
            "lot_no":stock_entry.lot_no,
            "remark":stock_entry.remark,
            "address":stock_entry.address,
            "quantity":stock_entry.quantity,
            "attention":stock_entry.attention,
            "eway_bill":stock_entry.eway_bill,
            "lr_number":stock_entry.lr_number,
            "reference":stock_entry.reference,
            "dyeing_lot":stock_entry.dyeing_lot,
            "wo_texture":stock_entry.wo_texture,
            "dyeing_unit":stock_entry.dyeing_unit,
            "fabric_name":stock_entry.fabric_name,
            "loop_length":stock_entry.loop_length,
            "no_of_rolls":stock_entry.no_of_rolls,
            "approved_lab":stock_entry.approved_lab,
            "custom_po_no":stock_entry.custom_po_no,
            "customer_name":stock_entry.customer_name,
            "finishingdia":stock_entry.finishingdia,
            "from_address":stock_entry.from_address,
            "knitting_dia":stock_entry.knitting_dia,
            "address_line1":stock_entry.address_line1,
            "address_line2":stock_entry.address_line2,
            "countable_uom":stock_entry.countable_uom,
            "finishing_dia":stock_entry.finishing_dia,
            "finishing_gsm":stock_entry.finishing_gsm,
            "knitting_unit":stock_entry.knitting_unit,
            "finishing_unit":stock_entry.finishing_unit,
            "party_dc_number":stock_entry.party_dc_number,
            "submitted_date":stock_entry.submitted_date,
            "value_of_goods":stock_entry.value_of_goods,
            "vehicle_number":stock_entry.vehicle_number,
            "wo_required_gg":stock_entry.wo_required_gg,
            "wo_required_ll":stock_entry.wo_required_ll,
            "customer_mobile":stock_entry.customer_mobile,
            "wo_no_of_course":stock_entry.wo_no_of_course,
            "wo_required_dia":stock_entry.wo_required_dia,
            "wo_required_gsm":stock_entry.wo_required_gsm,
            "fabric_reference":stock_entry.fabric_reference,
            "wo_no_of_needles":stock_entry.wo_no_of_needles,
            "lot_received_date":stock_entry.lot_received_date,
            "lab_dip_approval_no":stock_entry.lab_dip_approval_no,
            "no_of_countable_unit":stock_entry.no_of_countable_unit,
            "total_quantity_weight_in_kgs":stock_entry.total_quantity_weight_in_kgs,
            "custom_default_no_of_rolls":stock_entry.custom_default_no_of_rolls
        })

        # Save the Stock Entry document with the updated child table
        stock_entry_doc.save()

    # Step 5: Commit changes to the database
    frappe.db.commit()

   