import frappe
from frappe import _


def execute():
    """
    Update fg_warehouse in Work Orders where:
    - production_item starts with 'GKF'
    - source_warehouse starts with 'NAP'
    
    Mapping:
    - Kgs → NAP_E1/FF/A01 - PSS
    - Pcs → NAP_E1/FF/A02 - PSS
    """
    
    frappe.log_error("Starting Work Order FG Warehouse Update Patch", "Patch Execution")
    
    # Define warehouse mapping
    warehouse_mapping = {
        "Kgs": "NAP_E1/FF/A01 - PSS",
        "Pcs": "NAP_E1/FF/A02 - PSS"
    }
    
    # Validate warehouses exist
    for uom, warehouse in warehouse_mapping.items():
        if not frappe.db.exists("Warehouse", warehouse):
            frappe.log_error(
                f"Warehouse {warehouse} does not exist. Patch aborted.",
                "Patch Error"
            )
            print(f"ERROR: Warehouse {warehouse} does not exist!")
            return
    
    # Get Work Orders matching criteria
    work_orders = frappe.get_all(
        "Work Order",
        filters={
            "docstatus": 1,  # Submitted only
            "production_item": ["like", "GKF%"],
            "source_warehouse": ["like", "NAP%"]
        },
        fields=["name", "production_item", "source_warehouse", "fg_warehouse", "stock_uom"]
    )
    
    if not work_orders:
        print("No Work Orders found matching the criteria")
        frappe.log_error("No Work Orders found matching criteria", "Patch Info")
        return
    
    print(f"\nFound {len(work_orders)} Work Orders to process")
    print("=" * 80)
    
    updated_count = 0
    skipped_count = 0
    errors = []
    
    for wo in work_orders:
        try:
            stock_uom = wo.stock_uom
            
            # Check if stock_uom is in mapping
            if stock_uom not in warehouse_mapping:
                skipped_count += 1
                print(f"SKIPPED: {wo.name} - UOM '{stock_uom}' not in mapping")
                continue
            
            new_fg_warehouse = warehouse_mapping[stock_uom]
            old_fg_warehouse = wo.fg_warehouse
            
            # Skip if already correct
            if old_fg_warehouse == new_fg_warehouse:
                print(f"UNCHANGED: {wo.name} - Already has correct warehouse")
                continue
            
            # Update the Work Order
            frappe.db.set_value(
                "Work Order",
                wo.name,
                "fg_warehouse",
                new_fg_warehouse,
                update_modified=True
            )
            
            updated_count += 1
            print(f"UPDATED: {wo.name} | {stock_uom} | {old_fg_warehouse} → {new_fg_warehouse}")
            
        except Exception as e:
            error_msg = f"Failed to update {wo.name}: {str(e)}"
            errors.append(error_msg)
            print(f"ERROR: {error_msg}")
            frappe.log_error(error_msg, "Patch Update Error")
    
    # Commit all changes
    frappe.db.commit()
    
    # Summary
    print("\n" + "=" * 80)
    print("PATCH EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Total Work Orders Found: {len(work_orders)}")
    print(f"Successfully Updated: {updated_count}")
    print(f"Skipped (wrong UOM): {skipped_count}")
    print(f"Errors: {len(errors)}")
    print("\nWarehouse Mapping Applied:")
    for uom, warehouse in warehouse_mapping.items():
        print(f"  {uom} → {warehouse}")
    
    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(f"  - {error}")
    
    # Log summary
    summary = {
        "total_found": len(work_orders),
        "updated": updated_count,
        "skipped": skipped_count,
        "errors": len(errors)
    }
    frappe.log_error(str(summary), "Patch Execution Summary")
    
    print("\nPatch execution completed!")