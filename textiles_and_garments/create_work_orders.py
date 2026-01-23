import frappe
from frappe import _

def on_submit(doc, method=None):
    """Auto-create Work Orders with Operations for Manufacture Material Requests"""
    
    if doc.material_request_type != "Manufacture":
        return
    
    work_orders = []
    
    for item in doc.items:
        if not item.bom_no:
            continue
        
        # Check if Work Order already exists
        existing_wo = frappe.db.exists("Work Order", {
            "material_request": doc.name,
            "material_request_item": item.name
        })
        
        if existing_wo:
            continue
        
        try:
            # Create Work Order
            wo = frappe.get_doc({
                "doctype": "Work Order",
                "production_item": item.item_code,
                "bom_no": item.bom_no,
                "qty": item.qty,
                "stock_uom": item.stock_uom,
                "company": doc.company,
                "fg_warehouse": item.warehouse,
                "project": item.project,
                "date": frappe.utils.today(),
                "use_multi_level_bom": 1,
                "material_request": doc.name,
                "custom_location": item.custom_location,
                "material_request_item": item.name,
                "planned_start_date": doc.schedule_date or doc.transaction_date,
                "expected_delivery_date": item.schedule_date,
            })
            
            # Get workstation from Material Request Item custom field
            workstation = item.get("custom_workstation")
            
            if not workstation:
                frappe.msgprint(
                    _("No workstation specified for item {0}. Skipping operation creation.").format(item.item_code),
                    indicator="orange"
                )
            else:
                # Get workstation details
                workstation_doc = frappe.get_doc("Workstation", workstation)
                workstation_type = workstation_doc.get("workstation_type") or ""
                hour_rate = workstation_doc.get("hour_rate") or 0
                
                # Add operation to Work Order
                wo.append("operations", {
                    "operation": "Knitting",
                    "workstation_type": workstation_type,
                    "workstation": workstation,
                    "status": "Pending",
                    "time_in_mins": 0.01,
                    "planned_operating_cost": 0,
                    "sequence_id": 1,
                    "hour_rate": hour_rate,
                    "batch_size": 0,
                    "completed_qty": 0,
                    "process_loss_qty": 0,
                    "actual_operation_time": 0,
                    "actual_operating_cost": 0
                })
            
            # Insert Work Order
            wo.insert()
            work_orders.append(wo.name)
            
            frappe.msgprint(
                _("Created Work Order {0} for {1}").format(wo.name, item.item_code),
                indicator="green"
            )
            
        except Exception as e:
            error_msg = str(e)
            frappe.log_error(
                title=f"Work Order Creation Failed for {item.item_code}",
                message=f"Material Request: {doc.name}\nItem: {item.item_code}\nError: {error_msg}\n\n{frappe.get_traceback()}"
            )
            frappe.msgprint(
                _("Failed to create Work Order for {0}: {1}").format(item.item_code, error_msg),
                indicator="red"
            )
    
    if work_orders:
        frappe.msgprint(
            _("Successfully created {0} Work Order(s): {1}").format(
                len(work_orders),
                ", ".join(work_orders)
            ),
            title=_("Work Orders Created"),
            indicator="green"
        )

        