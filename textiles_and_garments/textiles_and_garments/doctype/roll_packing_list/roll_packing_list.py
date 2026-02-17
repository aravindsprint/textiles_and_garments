import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint, now_datetime, get_datetime
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
        if hasattr(doc, 'stock_entry') and doc.stock_entry:
            frappe.throw(
                _("Manufacture Stock Entry {0} already exists for this Roll Packing List").format(
                    frappe.bold(doc.stock_entry)
                )
            )

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
        # ✅ Added total_qty and mistake_qty fields for Pcs UOM support
        roll_details = frappe.get_all(
            "Roll",
            filters={"name": ["in", roll_numbers]},
            fields=[
                "name", "start_time", "end_time", "roll_weight",
                "batch", "item_code", "stock_uom", "total_qty", "mistake_qty"
            ]
        )

        if not roll_details:
            frappe.throw(_("No roll details found for the roll numbers"))

        # Create lookup map for roll details
        roll_details_map = {roll.name: roll for roll in roll_details}

        # ==================== STEP 4: Process data & calculate totals ====================
        batch_summary = {}
        all_start_times = []
        all_end_times = []
        total_roll_weight = 0
        total_roll_qty = 0      # ✅ NEW: for Pcs UOM
        stock_uom = None        # ✅ NEW: detected from roll details

        for item in doc.roll_packing_list_item:
            roll_detail = roll_details_map.get(item.roll_no)

            if roll_detail:
                batch = roll_detail.batch or item.batch
                current_stock_uom = roll_detail.stock_uom or item.stock_uom

                # ✅ Capture UOM from the first roll encountered
                if not stock_uom:
                    stock_uom = current_stock_uom

                roll_weight = flt(roll_detail.roll_weight or item.roll_weight, 2)
                roll_qty = cint(roll_detail.total_qty or item.total_qty)   # ✅ Pcs qty

                total_roll_weight += roll_weight
                total_roll_qty += roll_qty   # ✅ Accumulate pcs qty

                if current_stock_uom and current_stock_uom.lower() == "pcs":
                    frappe.logger().info(
                        f"✓ Roll {item.roll_no}: Pcs UOM - Total Qty: {roll_qty}, Weight: {roll_weight}"
                    )
                else:
                    frappe.logger().info(
                        f"✓ Roll {item.roll_no}: Kgs UOM - Weight: {roll_weight}, Qty: {roll_qty}"
                    )

                # Initialize batch summary
                if batch not in batch_summary:
                    batch_summary[batch] = {
                        "batch": batch,
                        "item_code": roll_detail.item_code or item.item_code,
                        "uom": current_stock_uom or "Kg",
                        "total_roll_weight": 0,
                        "total_roll_qty": 0,   # ✅ NEW: per-batch pcs qty
                        "roll_count": 0
                    }

                batch_summary[batch]["total_roll_weight"] += roll_weight
                batch_summary[batch]["total_roll_qty"] += roll_qty   # ✅ NEW
                batch_summary[batch]["roll_count"] += 1

                # Collect start and end times
                if roll_detail.start_time:
                    all_start_times.append(get_datetime(roll_detail.start_time))
                if roll_detail.end_time:
                    all_end_times.append(get_datetime(roll_detail.end_time))

        # Round totals
        total_roll_weight = round_to_decimals(total_roll_weight)
        total_roll_qty = cint(total_roll_qty)   # ✅ Pcs must be whole numbers

        frappe.logger().info(f"✓ Total Roll Weight (rounded): {total_roll_weight}")
        frappe.logger().info(f"✓ Total Roll Qty (Pcs): {total_roll_qty}")
        frappe.logger().info(f"✓ Stock UOM: {stock_uom}")

        # ✅ Determine final quantity - mirrors JS finalQuantity logic exactly
        # Pcs UOM  → use total_roll_qty (count)
        # Kgs/Kg   → use total_roll_weight
        if stock_uom and stock_uom.lower() == "pcs":
            qty = total_roll_qty
        else:
            qty = total_roll_weight

        final_weight = total_roll_weight   # ✅ Always keep weight separately for raw material calc

        # Get first start time and last end time
        first_start_time = min(all_start_times) if all_start_times else None
        last_end_time = max(all_end_times) if all_end_times else now_datetime()

        # Get Work Order from Job Card
        job_card = frappe.get_doc("Job Card", doc.document_name)
        work_order_name = job_card.work_order

        if not work_order_name:
            frappe.throw(_("Work Order not found in Job Card {0}").format(doc.document_name))

        work_order = frappe.get_doc("Work Order", work_order_name)

        # ==================== STEP 1: Get Material Transfer for Manufacture Stock Entries ====================
        material_transfer_entries = frappe.get_all(
            "Stock Entry",
            filters={
                "work_order": work_order_name,
                "purpose": "Material Transfer for Manufacture",
                "docstatus": 1  # Only submitted entries
            },
            fields=["name", "posting_date", "posting_time"],
            order_by="posting_date DESC, posting_time DESC"
        )

        if not material_transfer_entries:
            frappe.throw(
                _("No Material Transfer for Manufacture entries found for Work Order {0}").format(
                    frappe.bold(work_order_name)
                )
            )

        material_transfer_names = [entry.name for entry in material_transfer_entries]

        frappe.logger().info(
            f"Found {len(material_transfer_names)} Material Transfer entries for {work_order_name}"
        )

        # ==================== STEP 2: Get Stock Entry Details with BATCH info ====================
        material_transfer_items = frappe.get_all(
            "Stock Entry Detail",
            filters={
                "parent": ["in", material_transfer_names],
                "docstatus": 1,
                "is_finished_item": 0,   # Only raw materials, not finished goods
                "is_scrap_item": 0       # Exclude scrap items
            },
            fields=[
                "item_code",
                "qty",
                "t_warehouse",           # Target warehouse (WIP warehouse)
                "s_warehouse",           # Source warehouse
                "stock_uom",
                "batch_no",              # ✅ CRITICAL: Batch used in material transfer
                "parent",
                "uom",
                "conversion_factor",
                "transfer_qty"
            ],
            order_by="parent DESC, idx ASC"
        )

        if not material_transfer_items:
            frappe.throw(
                _("No material transfer items found for Work Order {0}").format(
                    frappe.bold(work_order_name)
                )
            )

        # ==================== STEP 3: Group materials by item_code and batch_no ====================
        material_batch_summary = {}
        total_transferred_qty = 0

        for mt_item in material_transfer_items:
            key = f"{mt_item.item_code}||{mt_item.batch_no or 'NO_BATCH'}"

            if key not in material_batch_summary:
                material_batch_summary[key] = {
                    "item_code": mt_item.item_code,
                    "batch_no": mt_item.batch_no,
                    "warehouse": mt_item.t_warehouse,   # WIP warehouse
                    "stock_uom": mt_item.stock_uom,
                    "total_qty": 0,
                    "uom": mt_item.uom,
                    "conversion_factor": mt_item.conversion_factor or 1.0,
                    "source_entries": []
                }

            material_batch_summary[key]["total_qty"] += flt(mt_item.qty, 2)
            material_batch_summary[key]["source_entries"].append(mt_item.parent)
            total_transferred_qty += flt(mt_item.qty, 2)

        if total_transferred_qty <= 0:
            frappe.throw(
                _("Total transferred material quantity is zero or negative for Work Order {0}").format(
                    frappe.bold(work_order_name)
                )
            )

        frappe.logger().info(f"Total transferred quantity: {total_transferred_qty}")
        frappe.logger().info(
            f"Material batch summary: {len(material_batch_summary)} unique item-batch combinations"
        )

        batch_summaries_list = list(batch_summary.values())

        # ==================== STEP 4: Create Stock Entry document ====================
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = "Manufacture"
        stock_entry.purpose = "Manufacture"
        stock_entry.naming_series = "MF/25/"
        stock_entry.work_order = work_order_name
        stock_entry.custom_job_card = doc.document_name
        stock_entry.project = work_order.project
        stock_entry.company = work_order.company
        stock_entry.posting_date = frappe.utils.nowdate()
        stock_entry.posting_time = frappe.utils.nowtime()
        stock_entry.fg_completed_qty = qty   # ✅ Correct qty: Pcs count or weight
        stock_entry.from_bom = 1

        # ==================== STEP 5: Add source items (raw materials consumed) ====================
        # ✅ Raw material consumption is ALWAYS weight-based regardless of FG UOM.
        #    For Pcs items, we still consume raw material in Kgs (the fabric weight).
        for idx, (key, mat_data) in enumerate(material_batch_summary.items(), start=1):
            proportional_qty = (
                (mat_data["total_qty"] / total_transferred_qty * final_weight)
                if total_transferred_qty > 0 else 0
            )
            proportional_qty = round_to_decimals(proportional_qty)

            # Skip items with zero quantity
            if proportional_qty <= 0:
                frappe.logger().warning(
                    f"Skipping {mat_data['item_code']} batch {mat_data['batch_no']}: zero quantity"
                )
                continue

            frappe.logger().info(
                f"Adding source item {idx}: {mat_data['item_code']} "
                f"Batch: {mat_data['batch_no'] or 'None'} "
                f"Qty: {proportional_qty} "
                f"From: {mat_data['warehouse']}"
            )

            stock_entry.append("items", {
                "s_warehouse": mat_data["warehouse"],          # WIP warehouse
                "item_code": mat_data["item_code"],
                "qty": proportional_qty,
                "uom": mat_data["uom"],
                "stock_uom": mat_data["stock_uom"],
                "conversion_factor": mat_data["conversion_factor"],
                "transfer_qty": proportional_qty * mat_data["conversion_factor"],
                "batch_no": mat_data["batch_no"],              # ✅ PRESERVE batch from Material Transfer
                "is_finished_item": 0,
                "is_scrap_item": 0,
                "use_serial_batch_fields": 1 if mat_data["batch_no"] else 0
            })

        # ==================== STEP 6: Add finished product items ====================
        for batch_data in batch_summaries_list:
            # ✅ Use Pcs qty for Pcs UOM, weight for Kgs/Kg
            if stock_uom and stock_uom.lower() == "pcs":
                finished_qty = cint(batch_data["total_roll_qty"])
                finished_uom = batch_data["uom"]  # "Pcs"
            else:
                finished_qty = round_to_decimals(batch_data["total_roll_weight"])
                finished_uom = batch_data["uom"]  # "Kg" / "Kgs"

            if finished_qty <= 0:
                frappe.logger().warning(
                    f"Skipping finished item batch {batch_data['batch']}: zero quantity"
                )
                continue

            frappe.logger().info(
                f"Adding finished item: {batch_data['item_code']} "
                f"Batch: {batch_data['batch']} "
                f"Qty: {finished_qty} {finished_uom}"
            )

            stock_entry.append("items", {
                "t_warehouse": work_order.fg_warehouse or "NAP_E1/FF/A01 - PSS",
                "item_code": batch_data["item_code"],
                "qty": finished_qty,
                "uom": finished_uom,
                "stock_uom": finished_uom,
                "conversion_factor": 1.0,
                "transfer_qty": finished_qty,
                "batch_no": batch_data["batch"],   # New batch for finished goods
                "is_finished_item": 1,
                "is_scrap_item": 0,
                "use_serial_batch_fields": 1        # Always use batch for finished item
            })

        # ==================== STEP 7: Validate items ====================
        if not stock_entry.items:
            frappe.throw(_("No items to transfer. Please check material transfer entries."))

        source_items = [item for item in stock_entry.items if not item.is_finished_item]
        finished_items = [item for item in stock_entry.items if item.is_finished_item]

        if not source_items:
            frappe.throw(_("No source items (raw materials) found for manufacture."))

        if not finished_items:
            frappe.throw(_("No finished items found for manufacture."))

        frappe.logger().info(
            f"Stock Entry has {len(source_items)} source items and {len(finished_items)} finished items"
        )

        # ==================== STEP 8: Log batch tracking summary ====================
        frappe.logger().info("=" * 80)
        frappe.logger().info("BATCH TRACKING SUMMARY:")
        frappe.logger().info("=" * 80)
        frappe.logger().info(f"Stock UOM: {stock_uom}")
        frappe.logger().info(f"FG Completed Qty (fg_completed_qty): {qty}")
        frappe.logger().info(f"Total Roll Weight (for raw material calc): {final_weight}")
        frappe.logger().info("-" * 80)
        frappe.logger().info("RAW MATERIALS (from Material Transfer):")
        for item in source_items:
            frappe.logger().info(
                f"  - {item.item_code}: {item.qty} {item.uom} "
                f"(Batch: {item.batch_no or 'None'}) from {item.s_warehouse}"
            )
        frappe.logger().info("-" * 80)
        frappe.logger().info("FINISHED GOODS (from Roll Packing List):")
        for item in finished_items:
            frappe.logger().info(
                f"  - {item.item_code}: {item.qty} {item.uom} "
                f"(Batch: {item.batch_no}) to {item.t_warehouse}"
            )
        frappe.logger().info("=" * 80)

        # ==================== STEP 9: Save and submit ====================
        stock_entry.insert()
        stock_entry.submit()

        # Add reference to Roll Packing List
        frappe.db.set_value("Roll Packing List", doc.name, "stock_entry", stock_entry.name)
        frappe.db.commit()

        frappe.msgprint(
            _("Manufacture Stock Entry {0} created successfully with batch tracking").format(
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


# ==================== HELPER ====================

def round_to_decimals(num, decimals=3):
    """Round a float to the given number of decimal places."""
    factor = 10 ** decimals
    return round(flt(num) * factor) / factor

    
# @frappe.whitelist()
# def create_manufacture_entry_from_roll_packing(doc):
#     """
#     Automatically create Manufacture Stock Entry from Roll Packing List
    
#     Args:
#         doc: Roll Packing List document (can be document name, dict, or JSON string)
#     """
    
#     try:
#         # Handle different input types
#         if isinstance(doc, str):
#             try:
#                 doc_dict = json.loads(doc)
#                 doc = frappe.get_doc(doc_dict)
#             except (json.JSONDecodeError, ValueError):
#                 doc = frappe.get_doc("Roll Packing List", doc)
#         elif isinstance(doc, dict):
#             doc = frappe.get_doc(doc)
        
#         # Validate document is submitted
#         if doc.docstatus != 1:
#             frappe.throw(_("Roll Packing List must be submitted before creating Manufacture Entry"))
        
#         # Check if stock entry already exists
#         if hasattr(doc, 'stock_entry') and doc.stock_entry:
#             frappe.throw(_("Manufacture Stock Entry {0} already exists for this Roll Packing List").format(
#                 frappe.bold(doc.stock_entry)
#             ))
        
#         # Validate document
#         if not doc.document_name:
#             frappe.throw(_("Job Card reference (document_name) is required"))
        
#         if not doc.roll_packing_list_item:
#             frappe.throw(_("Roll Packing List has no items"))
        
#         # Extract roll numbers from Roll Packing List items
#         roll_numbers = [item.roll_no for item in doc.roll_packing_list_item if item.roll_no]
        
#         if not roll_numbers:
#             frappe.throw(_("No roll numbers found in Roll Packing List items"))
        
#         # Fetch roll details from Roll doctype
#         roll_details = frappe.get_all(
#             "Roll",
#             filters={"name": ["in", roll_numbers]},
#             fields=["name", "start_time", "end_time", "roll_weight", "batch", "item_code", "stock_uom"]
#         )
        
#         if not roll_details:
#             frappe.throw(_("No roll details found for the roll numbers"))
        
#         # Create lookup map for roll details
#         roll_details_map = {roll.name: roll for roll in roll_details}
        
#         # Process batch summaries and calculate totals
#         batch_summary = {}
#         all_start_times = []
#         all_end_times = []
#         total_roll_weight = 0
        
#         for item in doc.roll_packing_list_item:
#             roll_detail = roll_details_map.get(item.roll_no)
            
#             if roll_detail:
#                 batch = roll_detail.batch or item.batch
#                 roll_weight = flt(roll_detail.roll_weight or item.roll_weight, 2)
#                 total_roll_weight = total_roll_weight + roll_weight
                
#                 # Initialize batch summary
#                 if batch not in batch_summary:
#                     batch_summary[batch] = {
#                         "batch": batch,
#                         "item_code": roll_detail.item_code or item.item_code,
#                         "uom": roll_detail.stock_uom or item.stock_uom or "Kg",
#                         "total_roll_weight": 0,
#                         "roll_count": 0
#                     }
                
#                 batch_summary[batch]["total_roll_weight"] = batch_summary[batch]["total_roll_weight"] + roll_weight
#                 batch_summary[batch]["roll_count"] = batch_summary[batch]["roll_count"] + 1
                
#                 # Collect start and end times
#                 if roll_detail.start_time:
#                     all_start_times.append(get_datetime(roll_detail.start_time))
#                 if roll_detail.end_time:
#                     all_end_times.append(get_datetime(roll_detail.end_time))
        
#         # Round total roll weight
#         total_roll_weight = round_to_decimals(total_roll_weight)
        
#         # Get first start time and last end time
#         first_start_time = min(all_start_times) if all_start_times else None
#         last_end_time = max(all_end_times) if all_end_times else now_datetime()
        
#         # Get Work Order from Job Card
#         job_card = frappe.get_doc("Job Card", doc.document_name)
#         work_order_name = job_card.work_order
        
#         if not work_order_name:
#             frappe.throw(_("Work Order not found in Job Card {0}").format(doc.document_name))
        
#         work_order = frappe.get_doc("Work Order", work_order_name)
        
#         # ✅ STEP 1: Get Material Transfer for Manufacture Stock Entries
#         material_transfer_entries = frappe.get_all(
#             "Stock Entry",
#             filters={
#                 "work_order": work_order_name,
#                 "purpose": "Material Transfer for Manufacture",
#                 "docstatus": 1  # Only submitted entries
#             },
#             fields=["name", "posting_date", "posting_time"],
#             order_by="posting_date DESC, posting_time DESC"
#         )
        
#         if not material_transfer_entries:
#             frappe.throw(_("No Material Transfer for Manufacture entries found for Work Order {0}").format(
#                 frappe.bold(work_order_name)
#             ))
        
#         material_transfer_names = [entry.name for entry in material_transfer_entries]
        
#         frappe.logger().info(f"Found {len(material_transfer_names)} Material Transfer entries for {work_order_name}")
        
#         # ✅ STEP 2: Get Stock Entry Details with BATCH information from Material Transfer entries
#         material_transfer_items = frappe.get_all(
#             "Stock Entry Detail",
#             filters={
#                 "parent": ["in", material_transfer_names],
#                 "docstatus": 1,
#                 "is_finished_item": 0,  # Only raw materials, not finished goods
#                 "is_scrap_item": 0      # Exclude scrap items
#             },
#             fields=[
#                 "item_code", 
#                 "qty", 
#                 "t_warehouse",  # Target warehouse (WIP warehouse)
#                 "s_warehouse",  # Source warehouse
#                 "stock_uom", 
#                 "batch_no",     # ✅ CRITICAL: Batch used in material transfer
#                 "parent",
#                 "uom",
#                 "conversion_factor",
#                 "transfer_qty"
#             ],
#             order_by="parent DESC, idx ASC"
#         )
        
#         if not material_transfer_items:
#             frappe.throw(_("No material transfer items found for Work Order {0}").format(
#                 frappe.bold(work_order_name)
#             ))
        
#         # ✅ STEP 3: Group materials by item_code and batch_no for proper tracking
#         material_batch_summary = {}
#         total_transferred_qty = 0
        
#         for mt_item in material_transfer_items:
#             key = f"{mt_item.item_code}||{mt_item.batch_no or 'NO_BATCH'}"
            
#             if key not in material_batch_summary:
#                 material_batch_summary[key] = {
#                     "item_code": mt_item.item_code,
#                     "batch_no": mt_item.batch_no,
#                     "warehouse": mt_item.t_warehouse,  # WIP warehouse where material was transferred
#                     "stock_uom": mt_item.stock_uom,
#                     "total_qty": 0,
#                     "uom": mt_item.uom,
#                     "conversion_factor": mt_item.conversion_factor or 1.0,
#                     "source_entries": []
#                 }
            
#             material_batch_summary[key]["total_qty"] += flt(mt_item.qty, 2)
#             material_batch_summary[key]["source_entries"].append(mt_item.parent)
#             total_transferred_qty += flt(mt_item.qty, 2)
        
#         if total_transferred_qty <= 0:
#             frappe.throw(_("Total transferred material quantity is zero or negative for Work Order {0}").format(
#                 frappe.bold(work_order_name)
#             ))
        
#         frappe.logger().info(f"Total transferred quantity: {total_transferred_qty}")
#         frappe.logger().info(f"Material batch summary: {len(material_batch_summary)} unique item-batch combinations")
        
#         # Get stock UOM from first batch summary
#         batch_summaries_list = list(batch_summary.values())
#         stock_uom = batch_summaries_list[0]["uom"] if batch_summaries_list else "Kg"
#         qty = total_roll_weight
        
#         # ✅ STEP 4: Create Stock Entry document
#         stock_entry = frappe.new_doc("Stock Entry")
#         stock_entry.stock_entry_type = "Manufacture"
#         stock_entry.purpose = "Manufacture"
#         stock_entry.naming_series = "MF/25/"
#         stock_entry.work_order = work_order_name
#         stock_entry.custom_job_card = doc.document_name
#         stock_entry.project = work_order.project
#         stock_entry.company = work_order.company
#         stock_entry.posting_date = frappe.utils.nowdate()
#         stock_entry.posting_time = frappe.utils.nowtime()
#         stock_entry.fg_completed_qty = qty
#         stock_entry.from_bom = 1
        
#         # ✅ STEP 5: Add source items (materials consumed) - PRESERVE BATCH from Material Transfer
#         for idx, (key, mat_data) in enumerate(material_batch_summary.items(), start=1):
#             # Calculate proportional qty based on finished goods quantity
#             if stock_uom in ["Kgs", "Kg"]:
#                 proportional_qty = (mat_data["total_qty"] / total_transferred_qty * qty) if total_transferred_qty > 0 else 0
#             else:
#                 proportional_qty = (mat_data["total_qty"] / total_transferred_qty * total_roll_weight) if total_transferred_qty > 0 else 0
            
#             proportional_qty = round_to_decimals(proportional_qty)
            
#             # Skip items with zero quantity
#             if proportional_qty <= 0:
#                 frappe.logger().warning(f"Skipping {mat_data['item_code']} batch {mat_data['batch_no']}: zero quantity")
#                 continue
            
#             frappe.logger().info(
#                 f"Adding source item {idx}: {mat_data['item_code']} "
#                 f"Batch: {mat_data['batch_no'] or 'None'} "
#                 f"Qty: {proportional_qty} "
#                 f"From: {mat_data['warehouse']}"
#             )
            
#             # ✅ CRITICAL: Use the SAME batch that was used in Material Transfer
#             stock_entry.append("items", {
#                 "s_warehouse": mat_data["warehouse"],  # WIP warehouse
#                 "item_code": mat_data["item_code"],
#                 "qty": proportional_qty,
#                 "uom": mat_data["uom"],
#                 "stock_uom": mat_data["stock_uom"],
#                 "conversion_factor": mat_data["conversion_factor"],
#                 "transfer_qty": proportional_qty * mat_data["conversion_factor"],
#                 "batch_no": mat_data["batch_no"],  # ✅ PRESERVE batch from Material Transfer
#                 "is_finished_item": 0,
#                 "is_scrap_item": 0,
#                 "use_serial_batch_fields": 1 if mat_data["batch_no"] else 0
#             })
        
#         # ✅ STEP 6: Add finished product item(s) - one per batch from Roll Packing List
#         for batch_data in batch_summaries_list:
#             finished_qty = round_to_decimals(batch_data["total_roll_weight"])
            
#             if finished_qty <= 0:
#                 frappe.logger().warning(f"Skipping finished item batch {batch_data['batch']}: zero quantity")
#                 continue
            
#             frappe.logger().info(
#                 f"Adding finished item: {batch_data['item_code']} "
#                 f"Batch: {batch_data['batch']} "
#                 f"Qty: {finished_qty}"
#             )
            
#             stock_entry.append("items", {
#                 "t_warehouse": work_order.fg_warehouse or "NAP_E1/FF/A01 - PSS",
#                 "item_code": batch_data["item_code"],
#                 "qty": finished_qty,
#                 "uom": batch_data["uom"],
#                 "stock_uom": batch_data["uom"],
#                 "conversion_factor": 1.0,
#                 "transfer_qty": finished_qty,
#                 "batch_no": batch_data["batch"],  # New batch for finished goods
#                 "is_finished_item": 1,
#                 "is_scrap_item": 0,
#                 "use_serial_batch_fields": 1  # Use batch for finished item
#             })
        
#         # ✅ STEP 7: Validate that we have both source and target items
#         if not stock_entry.items:
#             frappe.throw(_("No items to transfer. Please check material transfer entries."))
        
#         source_items = [item for item in stock_entry.items if not item.is_finished_item]
#         finished_items = [item for item in stock_entry.items if item.is_finished_item]
        
#         if not source_items:
#             frappe.throw(_("No source items (raw materials) found for manufacture."))
        
#         if not finished_items:
#             frappe.throw(_("No finished items found for manufacture."))
        
#         frappe.logger().info(f"Stock Entry has {len(source_items)} source items and {len(finished_items)} finished items")
        
#         # ✅ STEP 8: Log batch information for debugging
#         frappe.logger().info("=" * 80)
#         frappe.logger().info("BATCH TRACKING SUMMARY:")
#         frappe.logger().info("=" * 80)
#         frappe.logger().info("RAW MATERIALS (from Material Transfer):")
#         for item in source_items:
#             frappe.logger().info(
#                 f"  - {item.item_code}: {item.qty} {item.uom} "
#                 f"(Batch: {item.batch_no or 'None'}) from {item.s_warehouse}"
#             )
#         frappe.logger().info("-" * 80)
#         frappe.logger().info("FINISHED GOODS (from Roll Packing List):")
#         for item in finished_items:
#             frappe.logger().info(
#                 f"  - {item.item_code}: {item.qty} {item.uom} "
#                 f"(Batch: {item.batch_no}) to {item.t_warehouse}"
#             )
#         frappe.logger().info("=" * 80)
        
#         # Save and submit the Stock Entry
#         stock_entry.insert()
#         stock_entry.submit()
        
#         # Add reference to Roll Packing List
#         frappe.db.set_value("Roll Packing List", doc.name, "stock_entry", stock_entry.name)
#         frappe.db.commit()
        
#         frappe.msgprint(
#             _("Manufacture Stock Entry {0} created successfully with batch tracking").format(
#                 frappe.bold(stock_entry.name)
#             ),
#             indicator="green",
#             alert=True
#         )
        
#         return stock_entry.name
        
#     except Exception as e:
#         frappe.log_error(
#             message=frappe.get_traceback(),
#             title="Error creating Manufacture Entry for Roll Packing List"
#         )
#         frappe.throw(_("Failed to create Manufacture Stock Entry: {0}").format(str(e)))


# import frappe
# from frappe import _
# from frappe.model.document import Document
# from frappe.utils import flt, now_datetime, get_datetime
# import json

# class RollPackingList(Document):
# 	pass

# def round_to_decimals(value, decimals=2):
#     """Helper function for rounding to avoid floating-point precision issues"""
#     return round(flt(value), decimals)

# @frappe.whitelist()
# def create_manufacture_entry_from_roll_packing(doc):
#     """
#     Automatically create Manufacture Stock Entry from Roll Packing List
    
#     Args:
#         doc: Roll Packing List document (can be document name, dict, or JSON string)
#     """
    
#     try:
#         # Handle different input types
#         if isinstance(doc, str):
#             try:
#                 doc_dict = json.loads(doc)
#                 doc = frappe.get_doc(doc_dict)
#             except (json.JSONDecodeError, ValueError):
#                 doc = frappe.get_doc("Roll Packing List", doc)
#         elif isinstance(doc, dict):
#             doc = frappe.get_doc(doc)
        
#         # Validate document is submitted
#         if doc.docstatus != 1:
#             frappe.throw(_("Roll Packing List must be submitted before creating Manufacture Entry"))
        
#         # Check if stock entry already exists
#         if hasattr(doc, 'stock_entry') and doc.stock_entry:
#             frappe.throw(_("Manufacture Stock Entry {0} already exists for this Roll Packing List").format(
#                 frappe.bold(doc.stock_entry)
#             ))
        
#         # Validate document
#         if not doc.document_name:
#             frappe.throw(_("Job Card reference (document_name) is required"))
        
#         if not doc.roll_packing_list_item:
#             frappe.throw(_("Roll Packing List has no items"))
        
#         # Extract roll numbers from Roll Packing List items
#         roll_numbers = [item.roll_no for item in doc.roll_packing_list_item if item.roll_no]
        
#         if not roll_numbers:
#             frappe.throw(_("No roll numbers found in Roll Packing List items"))
        
#         # Fetch roll details from Roll doctype
#         roll_details = frappe.get_all(
#             "Roll",
#             filters={"name": ["in", roll_numbers]},
#             fields=["name", "start_time", "end_time", "roll_weight", "batch", "item_code", "stock_uom"]
#         )
        
#         if not roll_details:
#             frappe.throw(_("No roll details found for the roll numbers"))
        
#         # Create lookup map for roll details
#         roll_details_map = {roll.name: roll for roll in roll_details}
        
#         # Process batch summaries and calculate totals
#         batch_summary = {}
#         all_start_times = []
#         all_end_times = []
#         total_roll_weight = 0
        
#         for item in doc.roll_packing_list_item:
#             roll_detail = roll_details_map.get(item.roll_no)
            
#             if roll_detail:
#                 batch = roll_detail.batch or item.batch
#                 roll_weight = flt(roll_detail.roll_weight or item.roll_weight, 2)
#                 total_roll_weight = total_roll_weight + roll_weight
                
#                 # Initialize batch summary
#                 if batch not in batch_summary:
#                     batch_summary[batch] = {
#                         "batch": batch,
#                         "item_code": roll_detail.item_code or item.item_code,
#                         "uom": roll_detail.stock_uom or item.stock_uom or "Kg",
#                         "total_roll_weight": 0,
#                         "roll_count": 0
#                     }
                
#                 batch_summary[batch]["total_roll_weight"] = batch_summary[batch]["total_roll_weight"] + roll_weight
#                 batch_summary[batch]["roll_count"] = batch_summary[batch]["roll_count"] + 1
                
#                 # Collect start and end times
#                 if roll_detail.start_time:
#                     all_start_times.append(get_datetime(roll_detail.start_time))
#                 if roll_detail.end_time:
#                     all_end_times.append(get_datetime(roll_detail.end_time))
        
#         # Round total roll weight
#         total_roll_weight = round_to_decimals(total_roll_weight)
        
#         # Get first start time and last end time
#         first_start_time = min(all_start_times) if all_start_times else None
#         last_end_time = max(all_end_times) if all_end_times else now_datetime()
        
#         # Get Work Order from Job Card
#         job_card = frappe.get_doc("Job Card", doc.document_name)
#         work_order_name = job_card.work_order
        
#         if not work_order_name:
#             frappe.throw(_("Work Order not found in Job Card {0}").format(doc.document_name))
        
#         work_order = frappe.get_doc("Work Order", work_order_name)
        
#         # ✅ FIXED: Query Stock Entry (parent) first, then get Stock Entry Detail
#         # Step 1: Get all submitted Stock Entries for this work order
#         submitted_stock_entries = frappe.get_all(
#             "Stock Entry",
#             filters={
#                 "work_order": work_order_name,
#                 "docstatus": 1
#             },
#             pluck="name"
#         )
        
#         # Step 2: Get cancelled MTM Stock Entries to exclude
#         cancelled_mtm_entries = frappe.get_all(
#             "Stock Entry",
#             filters={
#                 "work_order": work_order_name,
#                 "docstatus": 2,
#                 "name": ["like", "MTM%"]
#             },
#             pluck="name"
#         )
        
#         # Step 3: Filter out cancelled MTM entries
#         valid_stock_entries = [
#             entry for entry in submitted_stock_entries 
#             if entry not in cancelled_mtm_entries
#         ]
        
#         if not valid_stock_entries:
#             frappe.throw(_("No valid material transfer entries found for Work Order {0}").format(work_order_name))
        
#         # Step 4: Get Stock Entry Details from valid stock entries
#         material_transfer_items = frappe.get_all(
#             "Stock Entry Detail",
#             filters={
#                 "parent": ["in", valid_stock_entries],
#                 "docstatus": 1
#             },
#             fields=["item_code", "qty", "t_warehouse", "stock_uom", "batch_no", "parent"],
#             order_by="idx DESC"
#         )
        
#         if not material_transfer_items:
#             frappe.throw(_("No material transfer items found for Work Order {0}").format(work_order_name))
        
#         # Calculate total ok_qty from material transfers
#         total_ok_qty = sum([flt(item.qty, 2) for item in material_transfer_items])
        
#         if total_ok_qty <= 0:
#             frappe.throw(_("Total material quantity is zero or negative for Work Order {0}").format(work_order_name))
        
#         # Get stock UOM from first batch summary
#         batch_summaries_list = list(batch_summary.values())
#         stock_uom = batch_summaries_list[0]["uom"] if batch_summaries_list else "Kg"
#         qty = total_roll_weight
        
#         # Create Stock Entry document
#         stock_entry = frappe.new_doc("Stock Entry")
#         stock_entry.stock_entry_type = "Manufacture"
#         stock_entry.purpose = "Manufacture"
#         stock_entry.work_order = work_order_name
#         stock_entry.custom_job_card = doc.document_name
#         stock_entry.project = work_order.project
#         stock_entry.company = work_order.company
#         stock_entry.posting_date = frappe.utils.nowdate()
#         stock_entry.posting_time = frappe.utils.nowtime()
#         stock_entry.fg_completed_qty = qty
#         stock_entry.from_bom = 1
        
#         # Add source items (materials consumed) proportionally
#         for idx, mt_item in enumerate(material_transfer_items, start=1):
#             # Calculate proportional qty based on stock UOM
#             if stock_uom == "Kgs" or stock_uom == "Kg":
#                 proportional_qty = (flt(mt_item.qty) / total_ok_qty * qty) if total_ok_qty > 0 else 0
#             else:
#                 proportional_qty = (flt(mt_item.qty) / total_ok_qty * total_roll_weight) if total_ok_qty > 0 else 0
            
#             proportional_qty = round_to_decimals(proportional_qty)
            
#             # Skip items with zero quantity
#             if proportional_qty <= 0:
#                 continue
            
#             stock_entry.append("items", {
#                 "s_warehouse": mt_item.t_warehouse,
#                 "item_code": mt_item.item_code,
#                 "qty": proportional_qty,
#                 "uom": mt_item.stock_uom,
#                 "stock_uom": mt_item.stock_uom,
#                 "conversion_factor": 1.0,
#                 "transfer_qty": proportional_qty,
#                 "batch_no": mt_item.batch_no,
#                 "is_finished_item": 0,
#                 "is_scrap_item": 0,
#                 "use_serial_batch_fields": 1 if mt_item.batch_no else 0
#             })
        
#         # Add finished product item(s) - one per batch
#         for batch_data in batch_summaries_list:
#             finished_qty = round_to_decimals(batch_data["total_roll_weight"])
            
#             if finished_qty <= 0:
#                 continue
            
#             stock_entry.append("items", {
#                 "t_warehouse": "NAP_E1/FF/A01 - PSS",
#                 "item_code": batch_data["item_code"],
#                 "qty": finished_qty,
#                 "uom": batch_data["uom"],
#                 "stock_uom": batch_data["uom"],
#                 "conversion_factor": 1.0,
#                 "transfer_qty": finished_qty,
#                 "batch_no": batch_data["batch"],
#                 "is_finished_item": 1,
#                 "is_scrap_item": 0,
#                 "use_serial_batch_fields": 0
#             })
        
#         # Validate that we have both source and target items
#         if not stock_entry.items:
#             frappe.throw(_("No items to transfer. Please check material transfer entries."))
        
#         source_items = [item for item in stock_entry.items if not item.is_finished_item]
#         finished_items = [item for item in stock_entry.items if item.is_finished_item]
        
#         if not source_items:
#             frappe.throw(_("No source items (raw materials) found for manufacture."))
        
#         if not finished_items:
#             frappe.throw(_("No finished items found for manufacture."))
        
#         # Save and submit the Stock Entry
#         stock_entry.insert()
#         stock_entry.submit()
        
#         # Add reference to Roll Packing List
#         frappe.db.set_value("Roll Packing List", doc.name, "stock_entry", stock_entry.name)
#         frappe.db.commit()
        
#         frappe.msgprint(
#             _("Manufacture Stock Entry {0} created successfully").format(
#                 frappe.bold(stock_entry.name)
#             ),
#             indicator="green",
#             alert=True
#         )
        
#         return stock_entry.name
        
#     except Exception as e:
#         frappe.log_error(
#             message=frappe.get_traceback(),
#             title="Error creating Manufacture Entry for Roll Packing List"
#         )
#         frappe.throw(_("Failed to create Manufacture Stock Entry: {0}").format(str(e)))