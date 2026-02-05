import frappe
from frappe import _

def on_submit(doc, method=None):
    """Auto-create Material Transfer Stock Entry when Work Order is submitted"""
    
    try:
        # Find existing Stock Entry with this Work Order
        stock_entries = frappe.get_all(
            "Stock Entry",
            filters={
                # "work_order": doc.name,
                "custom_work_order": doc.name,
                "docstatus": ["in", [0, 1]],  # Draft or Submitted
                "stock_entry_type": ["in", ["Material Transfer"]]
            },
            fields=["name", "stock_entry_type", "purpose", "docstatus"],
            order_by="creation desc",
            limit=1
        )
        
        if not stock_entries:
            frappe.msgprint(
                _("No Stock Entry found for Work Order {0}. Skipping auto-creation.").format(doc.name),
                indicator="orange"
            )
            return
        
        source_se = stock_entries[0]
        
        # Check if already submitted
        if source_se.docstatus == 1:
            frappe.msgprint(
                _("Stock Entry {0} is already submitted for Work Order {1}").format(
                    source_se.name, doc.name
                ),
                indicator="blue"
            )
            return
        
        # Get full Stock Entry document
        source_doc = frappe.get_doc("Stock Entry", source_se.name)
        
        # Submit the draft Stock Entry
        if source_doc.docstatus == 0:
            source_doc.submit()
            
            frappe.msgprint(
                _("Stock Entry {0} submitted successfully for Work Order {1}").format(
                    source_doc.name,
                    doc.name
                ),
                title=_("Stock Entry Submitted"),
                indicator="green"
            )
            
            # Log success
            frappe.logger().info(
                f"Auto-submitted Stock Entry {source_doc.name} for Work Order {doc.name}"
            )
        
    except Exception as e:
        error_msg = str(e)
        frappe.log_error(
            title=f"Stock Entry Auto-Submit Failed for Work Order {doc.name}",
            message=f"Work Order: {doc.name}\nError: {error_msg}\n\n{frappe.get_traceback()}"
        )
        
        frappe.msgprint(
            _("Failed to submit Stock Entry for Work Order {0}: {1}").format(
                doc.name, 
                error_msg
            ),
            indicator="red",
            alert=True
        )


def create_material_transfer_copy(doc, method=None):
    """Create a new Material Transfer copy with swapped warehouses"""
    
    try:
        # Find source Stock Entry
        stock_entries = frappe.get_all(
            "Stock Entry",
            filters={
                # "work_order": doc.name,
                "custom_work_order": doc.name,
                "docstatus": 1,  # Only submitted ones
                "purpose": ["in", ["Material Transfer"]]
            },
            fields=["name"],
            order_by="creation desc",
            limit=1
        )
        
        if not stock_entries:
            return
        
        source_doc = frappe.get_doc("Stock Entry", stock_entries[0].name)
        
        # Check if duplicate already exists
        existing_copy = frappe.db.exists("Stock Entry", {
            # "work_order": doc.name,
            "custom_work_order": doc.name,
            "custom_roll_wise_pick_list": source_doc.get("custom_roll_wise_pick_list"),
            "purpose": "Material Transfer",
            "docstatus": ["!=", 2],
            "creation": [">", source_doc.creation]  # Created after source
        })
        
        if existing_copy:
            frappe.msgprint(
                _("Material Transfer copy already exists for Work Order {0}").format(doc.name),
                indicator="blue"
            )
            return
        
        # ✅ Define the static In Transit warehouse
        in_transit_warehouse = "IN TRANSIT - PRANERA DYEING - PSS"
        
        # Validate that In Transit warehouse exists
        if not frappe.db.exists("Warehouse", in_transit_warehouse):
            frappe.throw(
                _("Warehouse '{0}' does not exist. Please create it first.").format(in_transit_warehouse)
            )
        
        # Create new Stock Entry
        new_se = frappe.get_doc({
            "doctype": "Stock Entry",
            "naming_series": source_doc.naming_series,
            "stock_entry_type": "Material Transfer",
            "purpose": "Material Transfer",
            "company": source_doc.company,
            "posting_date": frappe.utils.today(),
            "posting_time": frappe.utils.nowtime(),
            "set_posting_time": 0,
            "custom_work_order": doc.name,
            # "work_order": doc.name,
            "project": source_doc.project,
            "custom_roll_wise_pick_list": source_doc.get("custom_roll_wise_pick_list"),
            "from_bom": 0,
            "use_multi_level_bom": 0,
            "fg_completed_qty": 0
        })
        
        # ✅ Copy items with swapped warehouses
        for item in source_doc.items:
            new_se.append("items", {
                "s_warehouse": item.t_warehouse,  # ✅ Source = Previous Target
                "t_warehouse": in_transit_warehouse,  # ✅ Target = In transit
                "item_code": item.item_code,
                "qty": item.qty,
                "transfer_qty": item.transfer_qty,
                "uom": item.uom,
                "stock_uom": item.stock_uom,
                "conversion_factor": item.conversion_factor,
                "batch_no": item.batch_no,
                "use_serial_batch_fields": item.get("use_serial_batch_fields", 1),
                "allow_zero_valuation_rate": item.get("allow_zero_valuation_rate", 0)
            })
        
        # Copy batch-wise packing summary if exists
        if source_doc.get("custom_batch_wise_packing_summary"):
            for batch_item in source_doc.custom_batch_wise_packing_summary:
                new_se.append("custom_batch_wise_packing_summary", {
                    "batch": batch_item.batch,
                    "qty": batch_item.qty,
                    "no_of_rolls": batch_item.get("no_of_rolls", 0)
                })
        
        # Insert the new Stock Entry
        new_se.insert()
        
        frappe.msgprint(
            _("Created Material Transfer {0} for Work Order {1}<br>Materials moved from <b>{2}</b> to <b>{3}</b>").format(
                new_se.name,
                doc.name,
                source_doc.items[0].t_warehouse if source_doc.items else "N/A",
                in_transit_warehouse
            ),
            title=_("Stock Entry Created"),
            indicator="green"
        )
        
        frappe.logger().info(
            f"Auto-created Stock Entry {new_se.name} from {source_doc.name} for Work Order {doc.name}"
        )
        
        return new_se.name
        
    except Exception as e:
        error_msg = str(e)
        frappe.log_error(
            title=f"Stock Entry Copy Failed for Work Order {doc.name}",
            message=f"Work Order: {doc.name}\nError: {error_msg}\n\n{frappe.get_traceback()}"
        )
        
        frappe.msgprint(
            _("Failed to create Material Transfer for Work Order {0}: {1}").format(
                doc.name,
                error_msg
            ),
            indicator="red"
        )