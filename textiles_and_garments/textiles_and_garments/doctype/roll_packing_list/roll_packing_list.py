import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime, get_datetime
import json

class RollPackingList(Document):
	pass

def round_to_decimals(value, decimals=2):
    """Helper function for rounding to avoid floating-point precision issues"""
    return round(flt(value), decimals)

@frappe.whitelist()
def create_manufacture_entry_from_roll_packing(doc):
    """
    Automatically create Manufacture Stock Entry from Roll Packing List
    
    Args:
        doc: Roll Packing List document (can be document name, dict, or JSON string)
    """
    
    try:
        # Handle different input types
        if isinstance(doc, str):
            try:
                doc_dict = json.loads(doc)
                doc = frappe.get_doc(doc_dict)
            except (json.JSONDecodeError, ValueError):
                doc = frappe.get_doc("Roll Packing List", doc)
        elif isinstance(doc, dict):
            doc = frappe.get_doc(doc)
        
        # Validate document is submitted
        if doc.docstatus != 1:
            frappe.throw(_("Roll Packing List must be submitted before creating Manufacture Entry"))
        
        # Check if stock entry already exists
        if hasattr(doc, 'custom_stock_entry') and doc.custom_stock_entry:
            frappe.throw(_("Manufacture Stock Entry {0} already exists for this Roll Packing List").format(
                frappe.bold(doc.custom_stock_entry)
            ))
        
        # Validate document
        if not doc.document_name:
            frappe.throw(_("Job Card reference (document_name) is required"))
        
        if not doc.roll_packing_list_item:
            frappe.throw(_("Roll Packing List has no items"))
        
        # Extract roll numbers from Roll Packing List items
        roll_numbers = [item.roll_no for item in doc.roll_packing_list_item if item.roll_no]
        
        if not roll_numbers:
            frappe.throw(_("No roll numbers found in Roll Packing List items"))
        
        # Fetch roll details from Roll doctype
        roll_details = frappe.get_all(
            "Roll",
            filters={"name": ["in", roll_numbers]},
            fields=["name", "start_time", "end_time", "roll_weight", "batch", "item_code", "stock_uom"]
        )
        
        if not roll_details:
            frappe.throw(_("No roll details found for the roll numbers"))
        
        # Create lookup map for roll details
        roll_details_map = {roll.name: roll for roll in roll_details}
        
        # Process batch summaries and calculate totals
        batch_summary = {}
        all_start_times = []
        all_end_times = []
        total_roll_weight = 0
        
        for item in doc.roll_packing_list_item:
            roll_detail = roll_details_map.get(item.roll_no)
            
            if roll_detail:
                batch = roll_detail.batch or item.batch
                roll_weight = flt(roll_detail.roll_weight or item.roll_weight, 2)
                total_roll_weight = total_roll_weight + roll_weight
                
                # Initialize batch summary
                if batch not in batch_summary:
                    batch_summary[batch] = {
                        "batch": batch,
                        "item_code": roll_detail.item_code or item.item_code,
                        "uom": roll_detail.stock_uom or item.stock_uom or "Kg",
                        "total_roll_weight": 0,
                        "roll_count": 0
                    }
                
                batch_summary[batch]["total_roll_weight"] = batch_summary[batch]["total_roll_weight"] + roll_weight
                batch_summary[batch]["roll_count"] = batch_summary[batch]["roll_count"] + 1
                
                # Collect start and end times
                if roll_detail.start_time:
                    all_start_times.append(get_datetime(roll_detail.start_time))
                if roll_detail.end_time:
                    all_end_times.append(get_datetime(roll_detail.end_time))
        
        # Round total roll weight
        total_roll_weight = round_to_decimals(total_roll_weight)
        
        # Get first start time and last end time
        first_start_time = min(all_start_times) if all_start_times else None
        last_end_time = max(all_end_times) if all_end_times else now_datetime()
        
        # Get Work Order from Job Card
        job_card = frappe.get_doc("Job Card", doc.document_name)
        work_order_name = job_card.work_order
        
        if not work_order_name:
            frappe.throw(_("Work Order not found in Job Card {0}").format(doc.document_name))
        
        work_order = frappe.get_doc("Work Order", work_order_name)
        
        # ✅ FIXED: Query Stock Entry (parent) first, then get Stock Entry Detail
        # Step 1: Get all submitted Stock Entries for this work order
        submitted_stock_entries = frappe.get_all(
            "Stock Entry",
            filters={
                "work_order": work_order_name,
                "docstatus": 1
            },
            pluck="name"
        )
        
        # Step 2: Get cancelled MTM Stock Entries to exclude
        cancelled_mtm_entries = frappe.get_all(
            "Stock Entry",
            filters={
                "work_order": work_order_name,
                "docstatus": 2,
                "name": ["like", "MTM%"]
            },
            pluck="name"
        )
        
        # Step 3: Filter out cancelled MTM entries
        valid_stock_entries = [
            entry for entry in submitted_stock_entries 
            if entry not in cancelled_mtm_entries
        ]
        
        if not valid_stock_entries:
            frappe.throw(_("No valid material transfer entries found for Work Order {0}").format(work_order_name))
        
        # Step 4: Get Stock Entry Details from valid stock entries
        material_transfer_items = frappe.get_all(
            "Stock Entry Detail",
            filters={
                "parent": ["in", valid_stock_entries],
                "docstatus": 1
            },
            fields=["item_code", "qty", "t_warehouse", "stock_uom", "batch_no", "parent"],
            order_by="idx DESC"
        )
        
        if not material_transfer_items:
            frappe.throw(_("No material transfer items found for Work Order {0}").format(work_order_name))
        
        # Calculate total ok_qty from material transfers
        total_ok_qty = sum([flt(item.qty, 2) for item in material_transfer_items])
        
        if total_ok_qty <= 0:
            frappe.throw(_("Total material quantity is zero or negative for Work Order {0}").format(work_order_name))
        
        # Get stock UOM from first batch summary
        batch_summaries_list = list(batch_summary.values())
        stock_uom = batch_summaries_list[0]["uom"] if batch_summaries_list else "Kg"
        qty = total_roll_weight
        
        # Create Stock Entry document
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = "Manufacture"
        stock_entry.purpose = "Manufacture"
        stock_entry.work_order = work_order_name
        stock_entry.custom_job_card = doc.document_name
        stock_entry.project = work_order.project
        stock_entry.company = work_order.company
        stock_entry.posting_date = frappe.utils.nowdate()
        stock_entry.posting_time = frappe.utils.nowtime()
        stock_entry.fg_completed_qty = qty
        stock_entry.from_bom = 1
        
        # Add source items (materials consumed) proportionally
        for idx, mt_item in enumerate(material_transfer_items, start=1):
            # Calculate proportional qty based on stock UOM
            if stock_uom == "Kgs" or stock_uom == "Kg":
                proportional_qty = (flt(mt_item.qty) / total_ok_qty * qty) if total_ok_qty > 0 else 0
            else:
                proportional_qty = (flt(mt_item.qty) / total_ok_qty * total_roll_weight) if total_ok_qty > 0 else 0
            
            proportional_qty = round_to_decimals(proportional_qty)
            
            # Skip items with zero quantity
            if proportional_qty <= 0:
                continue
            
            stock_entry.append("items", {
                "s_warehouse": mt_item.t_warehouse,
                "item_code": mt_item.item_code,
                "qty": proportional_qty,
                "uom": mt_item.stock_uom,
                "stock_uom": mt_item.stock_uom,
                "conversion_factor": 1.0,
                "transfer_qty": proportional_qty,
                "batch_no": mt_item.batch_no,
                "is_finished_item": 0,
                "is_scrap_item": 0,
                "use_serial_batch_fields": 1 if mt_item.batch_no else 0
            })
        
        # Add finished product item(s) - one per batch
        for batch_data in batch_summaries_list:
            finished_qty = round_to_decimals(batch_data["total_roll_weight"])
            
            if finished_qty <= 0:
                continue
            
            stock_entry.append("items", {
                "t_warehouse": "NAP_E1/FF/A01 - PSS",
                "item_code": batch_data["item_code"],
                "qty": finished_qty,
                "uom": batch_data["uom"],
                "stock_uom": batch_data["uom"],
                "conversion_factor": 1.0,
                "transfer_qty": finished_qty,
                "batch_no": batch_data["batch"],
                "is_finished_item": 1,
                "is_scrap_item": 0,
                "use_serial_batch_fields": 0
            })
        
        # Validate that we have both source and target items
        if not stock_entry.items:
            frappe.throw(_("No items to transfer. Please check material transfer entries."))
        
        source_items = [item for item in stock_entry.items if not item.is_finished_item]
        finished_items = [item for item in stock_entry.items if item.is_finished_item]
        
        if not source_items:
            frappe.throw(_("No source items (raw materials) found for manufacture."))
        
        if not finished_items:
            frappe.throw(_("No finished items found for manufacture."))
        
        # Save and submit the Stock Entry
        stock_entry.insert()
        stock_entry.submit()
        
        # Add reference to Roll Packing List
        frappe.db.set_value("Roll Packing List", doc.name, "custom_stock_entry", stock_entry.name)
        frappe.db.commit()
        
        frappe.msgprint(
            _("Manufacture Stock Entry {0} created successfully").format(
                frappe.bold(stock_entry.name)
            ),
            indicator="green",
            alert=True
        )
        
        return stock_entry.name
        
    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Error creating Manufacture Entry for Roll Packing List"
        )
        frappe.throw(_("Failed to create Manufacture Stock Entry: {0}").format(str(e)))