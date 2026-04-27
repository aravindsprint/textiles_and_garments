import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint, now_datetime, get_datetime
import json


class RollPackingList(Document):
    pass


def round_to_decimals(num, decimals=3):
    """Round a float to the given number of decimal places."""
    factor = 10 ** decimals
    return round(flt(num) * factor) / factor


@frappe.whitelist()
def create_manufacture_entry_from_roll_packing(doc):
    """
    Automatically create Manufacture Stock Entry from Roll Packing List.

    from_bom = 1 is set intentionally so ERPNext can calculate correct valuation
    rates via get_basic_rate_for_manufactured_item(). It does NOT repopulate items
    from BOM during server-side validate() — that only happens via the UI get_items
    whitelist call when items are empty. Since we build all items manually here,
    from_bom = 1 is safe and gives us correct costing.

    Required: bom_no must always be set alongside from_bom = 1.
    """

    try:
        # ==================== Handle different input types ====================
        if isinstance(doc, str):
            try:
                doc_dict = json.loads(doc)
                doc = frappe.get_doc(doc_dict)
            except (json.JSONDecodeError, ValueError):
                doc = frappe.get_doc("Roll Packing List", doc)
        elif isinstance(doc, dict):
            doc = frappe.get_doc(doc)

        # ==================== Validate document ====================
        if doc.docstatus != 1:
            frappe.throw(_("Roll Packing List must be submitted before creating Manufacture Entry"))

        if hasattr(doc, "stock_entry") and doc.stock_entry:
            frappe.throw(
                _("Manufacture Stock Entry {0} already exists for this Roll Packing List").format(
                    frappe.bold(doc.stock_entry)
                )
            )

        if not doc.document_name:
            frappe.throw(_("Job Card reference (document_name) is required"))

        if not doc.roll_packing_list_item:
            frappe.throw(_("Roll Packing List has no items"))

        # ==================== Fetch Roll details (start/end times ONLY) ====================
        #
        # WHY: total_qty is a virtual field on Roll — frappe.get_all() returns None for
        # virtual fields. All qty/weight/batch/item_code data comes from RPL child items.
        # Roll doctype is fetched solely for start_time and end_time.
        #
        roll_numbers = [item.roll_no for item in doc.roll_packing_list_item if item.roll_no]

        if not roll_numbers:
            frappe.throw(_("No roll numbers found in Roll Packing List items"))

        roll_details = frappe.get_all(
            "Roll",
            filters={"name": ["in", roll_numbers]},
            fields=["name", "start_time", "end_time"]
        )
        roll_details_map = {roll.name: roll for roll in roll_details}

        frappe.logger().info(
            f"Roll lookup: requested {len(roll_numbers)}, found {len(roll_details_map)} in map."
        )

        # ==================== Process RPL child items ====================
        #
        # Authoritative data source: RPL child item fields only.
        # Roll doctype used only for start_time / end_time capture.
        #
        batch_summary   = {}
        all_start_times = []
        all_end_times   = []
        total_roll_weight = 0
        total_roll_qty    = 0
        stock_uom         = None

        for item in doc.roll_packing_list_item:
            # ---- All values from RPL child item (authoritative) ----
            batch             = item.batch
            current_stock_uom = item.uom
            roll_weight       = flt(item.roll_weight, 2)
            roll_qty          = cint(item.total_qty or 0)
            item_code         = item.item_code

            # ---- Start/end times from Roll doc only ----
            roll_detail = roll_details_map.get(item.roll_no)
            if roll_detail:
                if roll_detail.start_time:
                    all_start_times.append(get_datetime(roll_detail.start_time))
                if roll_detail.end_time:
                    all_end_times.append(get_datetime(roll_detail.end_time))
            else:
                frappe.logger().warning(
                    f"Roll {item.roll_no} not found in Roll doctype (Draft or permission issue). "
                    "Start/end times excluded for this roll."
                )

            # Capture UOM from first roll processed
            if not stock_uom:
                stock_uom = current_stock_uom

            total_roll_weight += roll_weight
            total_roll_qty    += roll_qty

            frappe.logger().info(
                f"Roll {item.roll_no}: UOM={current_stock_uom}, "
                f"Weight={roll_weight}, Qty={roll_qty}, Batch={batch}"
            )

            # Per-batch accumulation
            if batch not in batch_summary:
                batch_summary[batch] = {
                    "batch":             batch,
                    "item_code":         item_code,
                    "uom":               current_stock_uom or "Kg",
                    "total_roll_weight": 0,
                    "total_roll_qty":    0,
                    "roll_count":        0,
                }

            batch_summary[batch]["total_roll_weight"] += roll_weight
            batch_summary[batch]["total_roll_qty"]    += roll_qty
            batch_summary[batch]["roll_count"]        += 1

        # Round totals
        total_roll_weight = round_to_decimals(total_roll_weight)
        total_roll_qty    = cint(total_roll_qty)

        frappe.logger().info(
            f"Totals — stock_uom={stock_uom}, "
            f"total_roll_weight={total_roll_weight}, total_roll_qty={total_roll_qty}"
        )

        # ==================== Determine fg_completed_qty ====================
        #
        # Pcs UOM  → use piece count (total_roll_qty)
        # Kgs / Kg → use weight     (total_roll_weight)
        #
        if stock_uom and stock_uom.lower() == "pcs":
            qty = total_roll_qty
        else:
            qty = total_roll_weight

        # final_weight is always weight-based — used for raw material proportion calc.
        # Raw materials are always consumed in Kgs regardless of FG UOM.
        final_weight = total_roll_weight

        if qty <= 0:
            frappe.throw(
                _(
                    "Finished goods quantity is zero. "
                    "Check that Roll Packing List items have total_qty filled and UOM is correct."
                )
            )

        if final_weight <= 0:
            frappe.throw(
                _(
                    "Total roll weight is zero. "
                    "Check that Roll Packing List items have roll_weight filled."
                )
            )

        # ==================== Time range ====================
        first_start_time = min(all_start_times) if all_start_times else None
        last_end_time    = max(all_end_times)   if all_end_times   else now_datetime()

        # ==================== Work Order via Job Card ====================
        job_card = frappe.get_doc("Job Card", doc.document_name)
        work_order_name = job_card.work_order

        if not work_order_name:
            frappe.throw(_("Work Order not found in Job Card {0}").format(doc.document_name))

        work_order = frappe.get_doc("Work Order", work_order_name)

        # bom_no is required when from_bom = 1 for valuation rate calculation
        if not work_order.bom_no:
            frappe.throw(
                _("Work Order {0} does not have a BOM. "
                  "BOM is required for manufacture valuation.").format(
                    frappe.bold(work_order_name)
                )
            )

        # ==================== STEP 1: Material Transfer for Manufacture entries ====================
        material_transfer_entries = frappe.get_all(
            "Stock Entry",
            filters={
                "work_order": work_order_name,
                "purpose":    "Material Transfer for Manufacture",
                "docstatus":  1,
            },
            fields=["name", "posting_date", "posting_time"],
            order_by="posting_date DESC, posting_time DESC",
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

        # ==================== STEP 2: Stock Entry Details with batch info ====================
        material_transfer_items = frappe.get_all(
            "Stock Entry Detail",
            filters={
                "parent":           ["in", material_transfer_names],
                "docstatus":        1,
                "is_finished_item": 0,
                "is_scrap_item":    0,
            },
            fields=[
                "item_code", "qty", "t_warehouse", "s_warehouse",
                "stock_uom", "batch_no", "parent",
                "uom", "conversion_factor", "transfer_qty",
            ],
            order_by="parent DESC, idx ASC",
        )

        if not material_transfer_items:
            frappe.throw(
                _("No material transfer items found for Work Order {0}").format(
                    frappe.bold(work_order_name)
                )
            )

        # ==================== STEP 3: Group by item_code + batch_no ====================
        material_batch_summary = {}
        total_transferred_qty  = 0

        for mt_item in material_transfer_items:
            key = f"{mt_item.item_code}||{mt_item.batch_no or 'NO_BATCH'}"

            if key not in material_batch_summary:
                material_batch_summary[key] = {
                    "item_code":         mt_item.item_code,
                    "batch_no":          mt_item.batch_no,
                    "warehouse":         mt_item.t_warehouse,
                    "stock_uom":         mt_item.stock_uom,
                    "total_qty":         0,
                    "uom":               mt_item.uom,
                    "conversion_factor": mt_item.conversion_factor or 1.0,
                    "source_entries":    [],
                }

            material_batch_summary[key]["total_qty"]      += flt(mt_item.qty, 2)
            material_batch_summary[key]["source_entries"].append(mt_item.parent)
            total_transferred_qty += flt(mt_item.qty, 2)

        if total_transferred_qty <= 0:
            frappe.throw(
                _("Total transferred material quantity is zero or negative for Work Order {0}").format(
                    frappe.bold(work_order_name)
                )
            )

        frappe.logger().info(
            f"Total transferred qty: {total_transferred_qty} | "
            f"Unique item-batch combos: {len(material_batch_summary)}"
        )

        batch_summaries_list = list(batch_summary.values())

        # ==================== STEP 4: Create Stock Entry ====================
        #
        # from_bom = 1  — enables correct valuation rate via get_basic_rate_for_manufactured_item().
        #                  Does NOT repopulate items from BOM server-side when items are already
        #                  present. Item auto-fill only happens via the UI get_items() whitelist call.
        #
        # bom_no        — required alongside from_bom = 1 for valuation to work correctly.
        #
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = "Manufacture"
        stock_entry.purpose          = "Manufacture"
        stock_entry.naming_series    = "MF/26/"
        stock_entry.work_order       = work_order_name
        stock_entry.bom_no           = work_order.bom_no   # Required for valuation when from_bom=1
        stock_entry.custom_job_card  = doc.document_name
        stock_entry.project          = work_order.project
        stock_entry.company          = work_order.company
        stock_entry.posting_date     = frappe.utils.nowdate()
        stock_entry.posting_time     = frappe.utils.nowtime()
        stock_entry.fg_completed_qty = qty
        stock_entry.from_bom         = 1   # Correct costing — items are NOT cleared by this server-side

        # ==================== STEP 5: Source items (raw materials consumed) ====================
        #
        # Raw material consumption is ALWAYS weight-based (Kgs), even when FG UOM is Pcs.
        # Proportional qty = (batch's share of total transfer) × actual finished weight
        #
        for idx, (key, mat_data) in enumerate(material_batch_summary.items(), start=1):
            proportional_qty = (
                (mat_data["total_qty"] / total_transferred_qty * final_weight)
                if total_transferred_qty > 0
                else 0
            )
            proportional_qty = round_to_decimals(proportional_qty)

            if proportional_qty <= 0:
                frappe.logger().warning(
                    f"Skipping source item {mat_data['item_code']} "
                    f"batch {mat_data['batch_no']}: zero proportional qty"
                )
                continue

            frappe.logger().info(
                f"Source item {idx}: {mat_data['item_code']} | "
                f"batch={mat_data['batch_no'] or 'None'} | "
                f"qty={proportional_qty} | warehouse={mat_data['warehouse']}"
            )

            stock_entry.append("items", {
                "s_warehouse":       mat_data["warehouse"],
                "item_code":         mat_data["item_code"],
                "qty":               proportional_qty,
                "uom":               mat_data["uom"],
                "stock_uom":         mat_data["stock_uom"],
                "conversion_factor": mat_data["conversion_factor"],
                "transfer_qty":      proportional_qty * mat_data["conversion_factor"],
                "batch_no":          mat_data["batch_no"],
                "is_finished_item":  0,
                "is_scrap_item":     0,
            })

        # ==================== STEP 6: Finished product items ====================
        for batch_data in batch_summaries_list:
            if stock_uom and stock_uom.lower() == "pcs":
                finished_qty = cint(batch_data["total_roll_qty"])
                finished_uom = batch_data["uom"]
            else:
                finished_qty = round_to_decimals(batch_data["total_roll_weight"])
                finished_uom = batch_data["uom"]

            if finished_qty <= 0:
                frappe.logger().warning(
                    f"Skipping finished item batch {batch_data['batch']}: zero qty"
                )
                continue

            frappe.logger().info(
                f"Finished item: {batch_data['item_code']} | "
                f"batch={batch_data['batch']} | qty={finished_qty} {finished_uom}"
            )

            stock_entry.append("items", {
                "t_warehouse":       work_order.fg_warehouse or "NAP_E1/FF/A02 - PSS",
                "item_code":         batch_data["item_code"],
                "qty":               finished_qty,
                "uom":               finished_uom,
                "stock_uom":         finished_uom,
                "conversion_factor": 1.0,
                "transfer_qty":      finished_qty,
                "batch_no":          batch_data["batch"],
                "is_finished_item":  1,
                "is_scrap_item":     0,
            })

        # ==================== STEP 7: Validate items ====================
        if not stock_entry.items:
            frappe.throw(_("No items to transfer. Please check material transfer entries."))

        source_items   = [i for i in stock_entry.items if not i.is_finished_item]
        finished_items = [i for i in stock_entry.items if i.is_finished_item]

        if not source_items:
            frappe.throw(_("No source items (raw materials) found for manufacture."))

        if not finished_items:
            frappe.throw(_("No finished items found for manufacture."))

        # ==================== STEP 8: Safety — remove any zero-qty rows ====================
        before_count = len(stock_entry.items)
        stock_entry.items = [i for i in stock_entry.items if flt(i.qty) > 0]
        after_count = len(stock_entry.items)

        if before_count != after_count:
            frappe.logger().warning(
                f"Zero-qty safety filter removed {before_count - after_count} rows."
            )

        if not stock_entry.items:
            frappe.throw(_("All items have zero quantity after safety filter."))

        # ==================== STEP 9: Pre-insert log ====================
        frappe.logger().info("=" * 80)
        frappe.logger().info("BATCH TRACKING SUMMARY (pre-insert):")
        frappe.logger().info("=" * 80)
        frappe.logger().info(f"stock_uom        : {stock_uom}")
        frappe.logger().info(f"fg_completed_qty : {qty}")
        frappe.logger().info(f"final_weight     : {final_weight}")
        frappe.logger().info(f"from_bom         : 1")
        frappe.logger().info(f"bom_no           : {work_order.bom_no}")
        frappe.logger().info("-" * 80)
        frappe.logger().info("RAW MATERIALS:")
        for item in stock_entry.items:
            if not item.is_finished_item:
                frappe.logger().info(
                    f"  {item.item_code} | qty={item.qty} {item.uom} | "
                    f"batch={item.batch_no or 'None'} | from={item.s_warehouse}"
                )
        frappe.logger().info("FINISHED GOODS:")
        for item in stock_entry.items:
            if item.is_finished_item:
                frappe.logger().info(
                    f"  {item.item_code} | qty={item.qty} {item.uom} | "
                    f"batch={item.batch_no} | to={item.t_warehouse}"
                )
        frappe.logger().info("=" * 80)

        # ==================== STEP 10: Insert ====================
        stock_entry.insert(ignore_permissions=True)
        frappe.db.commit()

        # ==================== STEP 11: Reload from DB before submit ====================
        #
        # WHY THIS IS CRITICAL (applies regardless of from_bom value):
        #
        # Frappe's insert() sequence:
        #   1. validate()     — correct values ✓
        #   2. db_insert()    — DB written with correct values ✓
        #   3. on_update()    — runs AFTER DB write, on the same in-memory object
        #
        # ERPNext v14/v15 on_update triggers Serial/Batch Bundle handlers for items
        # with batch_no. For a newly created FG batch without a Serial-Batch Bundle doc,
        # the handler can reset item.qty = 0 and/or fg_completed_qty = 0 in-memory.
        #
        # These mutations are NOT written back to DB — DB still holds correct values.
        # But submit() calls save() → validate() on the same poisoned in-memory object,
        # sees qty = 0, and raises errors.
        #
        # Fix: discard the in-memory object after insert, reload a clean copy from DB,
        # then re-assert fg_completed_qty and from_bom before submit.
        #
        stock_entry_name = stock_entry.name
        stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)

        # Re-assert fg_completed_qty and from_bom after reload.
        # Defensive layer: if submit()'s internal validate recalculates these from BOM,
        # we ensure our values take precedence.
        stock_entry.fg_completed_qty = qty
        stock_entry.from_bom         = 1
        stock_entry.bom_no           = work_order.bom_no

        frappe.logger().info(
            f"Reloaded {stock_entry_name} from DB. "
            f"Re-asserted fg_completed_qty={qty}, from_bom=1, bom_no={work_order.bom_no}. "
            f"FG qtys after reload: "
            + str([f"{i.item_code}={i.qty}" for i in stock_entry.items if i.is_finished_item])
        )

        # ==================== STEP 12: Post-reload sanity checks ====================
        if flt(stock_entry.fg_completed_qty) <= 0:
            frappe.log_error(
                f"fg_completed_qty is 0 even after DB reload + re-assertion.\n"
                f"Stock Entry : {stock_entry.name}\n"
                f"Expected qty: {qty}\n"
                f"Check for custom before_save hooks or triggers that recalculate "
                f"fg_completed_qty on Stock Entry.",
                "Manufacture Entry FG Completed Qty Zero After Reload"
            )
            frappe.throw(
                _("fg_completed_qty is 0 after reload for Stock Entry {0}. "
                  "Check Error Log for details.").format(frappe.bold(stock_entry.name))
            )

        for fg_row in [i for i in stock_entry.items if i.is_finished_item]:
            if flt(fg_row.qty) <= 0:
                frappe.log_error(
                    f"FG item qty is 0 even after DB reload.\n"
                    f"Stock Entry : {stock_entry.name}\n"
                    f"Item        : {fg_row.item_code}\n"
                    f"Batch       : {fg_row.batch_no}\n"
                    f"DB itself has qty=0. Check for custom before_save hooks "
                    f"or database triggers on Stock Entry / Stock Entry Detail.",
                    "Manufacture Entry FG Qty Zero After Reload"
                )
                frappe.throw(
                    _("Finished goods qty is 0 after DB reload for item {0} (batch: {1}). "
                      "Check Error Log for details.").format(
                        frappe.bold(fg_row.item_code),
                        frappe.bold(fg_row.batch_no or "None")
                    )
                )

        # ==================== STEP 13: Submit ====================
        stock_entry.submit()

        frappe.db.set_value("Roll Packing List", doc.name, "stock_entry", stock_entry.name)
        frappe.db.commit()

        frappe.msgprint(
            _("Manufacture Stock Entry {0} created successfully").format(
                frappe.bold(stock_entry.name)
            ),
            indicator="green",
            alert=True,
        )

        return stock_entry.name

    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Error creating Manufacture Entry for Roll Packing List"
        )
        frappe.throw(_("Failed to create Manufacture Stock Entry: {0}").format(str(e)))


        
# import frappe
# from frappe import _
# from frappe.model.document import Document
# from frappe.utils import flt, cint, now_datetime, get_datetime
# import json


# class RollPackingList(Document):
# 	pass


# def round_to_decimals(num, decimals=3):
#     """Round a float to the given number of decimal places."""
#     factor = 10 ** decimals
#     return round(flt(num) * factor) / factor


# @frappe.whitelist()
# def create_manufacture_entry_from_roll_packing(doc):
#     """
#     Automatically create Manufacture Stock Entry from Roll Packing List

#     Args:
#         doc: Roll Packing List document (can be document name, dict, or JSON string)
#     """

#     try:
#         # ==================== Handle different input types ====================
#         if isinstance(doc, str):
#             try:
#                 doc_dict = json.loads(doc)
#                 doc = frappe.get_doc(doc_dict)
#             except (json.JSONDecodeError, ValueError):
#                 doc = frappe.get_doc("Roll Packing List", doc)
#         elif isinstance(doc, dict):
#             doc = frappe.get_doc(doc)

#         # ==================== Validate document ====================
#         if doc.docstatus != 1:
#             frappe.throw(_("Roll Packing List must be submitted before creating Manufacture Entry"))

#         if hasattr(doc, 'stock_entry') and doc.stock_entry:
#             frappe.throw(
#                 _("Manufacture Stock Entry {0} already exists for this Roll Packing List").format(
#                     frappe.bold(doc.stock_entry)
#                 )
#             )

#         if not doc.document_name:
#             frappe.throw(_("Job Card reference (document_name) is required"))

#         if not doc.roll_packing_list_item:
#             frappe.throw(_("Roll Packing List has no items"))

#         # ==================== Fetch Roll details (for start/end times only) ====================
#         # NOTE: We do NOT use Roll.total_qty or Roll.roll_weight here.
#         # total_qty is a virtual field — frappe.get_all returns None for virtual fields.
#         # RPL child item values are the authoritative source for all qty/weight calculations.
#         # Roll records are fetched solely to capture start_time and end_time.
#         roll_numbers = [item.roll_no for item in doc.roll_packing_list_item if item.roll_no]

#         if not roll_numbers:
#             frappe.throw(_("No roll numbers found in Roll Packing List items"))

#         roll_details = frappe.get_all(
#             "Roll",
#             filters={"name": ["in", roll_numbers]},
#             fields=["name", "start_time", "end_time"]
#         )

#         roll_details_map = {roll.name: roll for roll in roll_details}

#         frappe.logger().info(
#             f"Roll lookup: requested {len(roll_numbers)}, found {len(roll_details_map)} in map."
#         )

#         # ==================== Process rolls & calculate totals ====================
#         # Always use RPL child item data for qty/weight — never rely on Roll virtual fields.
#         batch_summary = {}
#         all_start_times = []
#         all_end_times = []
#         total_roll_weight = 0
#         total_roll_qty = 0
#         stock_uom = None

#         for item in doc.roll_packing_list_item:
#             # ---- Authoritative values come from RPL child item ----
#             batch             = item.batch
#             current_stock_uom = item.uom
#             roll_weight       = flt(item.roll_weight, 2)
#             roll_qty          = cint(item.total_qty or 0)
#             item_code         = item.item_code

#             # ---- Pull start/end times from Roll doc only (no qty logic) ----
#             roll_detail = roll_details_map.get(item.roll_no)
#             if roll_detail:
#                 if roll_detail.start_time:
#                     all_start_times.append(get_datetime(roll_detail.start_time))
#                 if roll_detail.end_time:
#                     all_end_times.append(get_datetime(roll_detail.end_time))
#             else:
#                 frappe.logger().warning(
#                     f"Roll {item.roll_no} not found in Roll doctype (Draft or permission issue). "
#                     f"Start/end times will be excluded for this roll."
#                 )

#             # Capture UOM from first roll processed
#             if not stock_uom:
#                 stock_uom = current_stock_uom

#             total_roll_weight += roll_weight
#             total_roll_qty    += roll_qty

#             frappe.logger().info(
#                 f"Roll {item.roll_no}: UOM={current_stock_uom}, "
#                 f"Weight={roll_weight}, Qty={roll_qty}, Batch={batch}"
#             )

#             # Accumulate per-batch summary
#             if batch not in batch_summary:
#                 batch_summary[batch] = {
#                     "batch":             batch,
#                     "item_code":         item_code,
#                     "uom":               current_stock_uom or "Kg",
#                     "total_roll_weight": 0,
#                     "total_roll_qty":    0,
#                     "roll_count":        0
#                 }

#             batch_summary[batch]["total_roll_weight"] += roll_weight
#             batch_summary[batch]["total_roll_qty"]    += roll_qty
#             batch_summary[batch]["roll_count"]        += 1

#         # Round totals
#         total_roll_weight = round_to_decimals(total_roll_weight)
#         total_roll_qty    = cint(total_roll_qty)

#         frappe.logger().info(
#             f"Totals — stock_uom={stock_uom}, "
#             f"total_roll_weight={total_roll_weight}, total_roll_qty={total_roll_qty}"
#         )

#         # ==================== Determine fg_completed_qty ====================
#         # Pcs UOM → piece count | Kgs/Kg → weight
#         if stock_uom and stock_uom.lower() == "pcs":
#             qty = total_roll_qty
#         else:
#             qty = total_roll_weight

#         # final_weight is always weight-based (used for raw material proportion)
#         final_weight = total_roll_weight

#         if qty <= 0:
#             frappe.throw(
#                 _("Finished goods quantity is zero. "
#                   "Check that Roll Packing List items have total_qty filled and UOM is correct.")
#             )

#         if final_weight <= 0:
#             frappe.throw(
#                 _("Total roll weight is zero. "
#                   "Check that Roll Packing List items have roll_weight filled.")
#             )

#         # ==================== Get time range ====================
#         first_start_time = min(all_start_times) if all_start_times else None
#         last_end_time    = max(all_end_times)   if all_end_times   else now_datetime()

#         # ==================== Get Work Order via Job Card ====================
#         job_card = frappe.get_doc("Job Card", doc.document_name)
#         work_order_name = job_card.work_order

#         if not work_order_name:
#             frappe.throw(_("Work Order not found in Job Card {0}").format(doc.document_name))

#         work_order = frappe.get_doc("Work Order", work_order_name)

#         # ==================== STEP 1: Material Transfer for Manufacture entries ====================
#         material_transfer_entries = frappe.get_all(
#             "Stock Entry",
#             filters={
#                 "work_order": work_order_name,
#                 "purpose":    "Material Transfer for Manufacture",
#                 "docstatus":  1
#             },
#             fields=["name", "posting_date", "posting_time"],
#             order_by="posting_date DESC, posting_time DESC"
#         )

#         if not material_transfer_entries:
#             frappe.throw(
#                 _("No Material Transfer for Manufacture entries found for Work Order {0}").format(
#                     frappe.bold(work_order_name)
#                 )
#             )

#         material_transfer_names = [entry.name for entry in material_transfer_entries]

#         frappe.logger().info(
#             f"Found {len(material_transfer_names)} Material Transfer entries for {work_order_name}"
#         )

#         # ==================== STEP 2: Stock Entry Details with batch info ====================
#         material_transfer_items = frappe.get_all(
#             "Stock Entry Detail",
#             filters={
#                 "parent":           ["in", material_transfer_names],
#                 "docstatus":        1,
#                 "is_finished_item": 0,
#                 "is_scrap_item":    0
#             },
#             fields=[
#                 "item_code", "qty", "t_warehouse", "s_warehouse",
#                 "stock_uom", "batch_no", "parent",
#                 "uom", "conversion_factor", "transfer_qty"
#             ],
#             order_by="parent DESC, idx ASC"
#         )

#         if not material_transfer_items:
#             frappe.throw(
#                 _("No material transfer items found for Work Order {0}").format(
#                     frappe.bold(work_order_name)
#                 )
#             )

#         # ==================== STEP 3: Group by item_code + batch_no ====================
#         material_batch_summary = {}
#         total_transferred_qty  = 0

#         for mt_item in material_transfer_items:
#             key = f"{mt_item.item_code}||{mt_item.batch_no or 'NO_BATCH'}"

#             if key not in material_batch_summary:
#                 material_batch_summary[key] = {
#                     "item_code":         mt_item.item_code,
#                     "batch_no":          mt_item.batch_no,
#                     "warehouse":         mt_item.t_warehouse,
#                     "stock_uom":         mt_item.stock_uom,
#                     "total_qty":         0,
#                     "uom":               mt_item.uom,
#                     "conversion_factor": mt_item.conversion_factor or 1.0,
#                     "source_entries":    []
#                 }

#             material_batch_summary[key]["total_qty"]      += flt(mt_item.qty, 2)
#             material_batch_summary[key]["source_entries"].append(mt_item.parent)
#             total_transferred_qty += flt(mt_item.qty, 2)

#         if total_transferred_qty <= 0:
#             frappe.throw(
#                 _("Total transferred material quantity is zero or negative for Work Order {0}").format(
#                     frappe.bold(work_order_name)
#                 )
#             )

#         frappe.logger().info(
#             f"Total transferred qty: {total_transferred_qty} | "
#             f"Unique item-batch combos: {len(material_batch_summary)}"
#         )

#         batch_summaries_list = list(batch_summary.values())

#         # ==================== STEP 4: Create Stock Entry ====================
#         stock_entry = frappe.new_doc("Stock Entry")
#         stock_entry.stock_entry_type = "Manufacture"
#         stock_entry.purpose          = "Manufacture"
#         stock_entry.naming_series    = "MF/26/"
#         stock_entry.work_order       = work_order_name
#         stock_entry.custom_job_card  = doc.document_name
#         stock_entry.project          = work_order.project
#         stock_entry.company          = work_order.company
#         stock_entry.posting_date     = frappe.utils.nowdate()
#         stock_entry.posting_time     = frappe.utils.nowtime()
#         stock_entry.fg_completed_qty = qty
#         stock_entry.from_bom         = 0  # Must be 0 — we build all items manually.
#         stock_entry.bom_no           = work_order.bom_no  # Still set for valuation rates.

#         # ==================== STEP 5: Source items (raw materials consumed) ====================
#         # Raw material consumption is always weight-based (Kgs), even when FG UOM is Pcs.
#         for idx, (key, mat_data) in enumerate(material_batch_summary.items(), start=1):
#             proportional_qty = (
#                 (mat_data["total_qty"] / total_transferred_qty * final_weight)
#                 if total_transferred_qty > 0 else 0
#             )
#             proportional_qty = round_to_decimals(proportional_qty)

#             if proportional_qty <= 0:
#                 frappe.logger().warning(
#                     f"Skipping source item {mat_data['item_code']} "
#                     f"batch {mat_data['batch_no']}: zero proportional qty"
#                 )
#                 continue

#             frappe.logger().info(
#                 f"Source item {idx}: {mat_data['item_code']} | "
#                 f"batch={mat_data['batch_no'] or 'None'} | "
#                 f"qty={proportional_qty} | warehouse={mat_data['warehouse']}"
#             )

#             stock_entry.append("items", {
#                 "s_warehouse":       mat_data["warehouse"],
#                 "item_code":         mat_data["item_code"],
#                 "qty":               proportional_qty,
#                 "uom":               mat_data["uom"],
#                 "stock_uom":         mat_data["stock_uom"],
#                 "conversion_factor": mat_data["conversion_factor"],
#                 "transfer_qty":      proportional_qty * mat_data["conversion_factor"],
#                 "batch_no":          mat_data["batch_no"],
#                 "is_finished_item":  0,
#                 "is_scrap_item":     0,
#             })

#         # ==================== STEP 6: Finished product items ====================
#         for batch_data in batch_summaries_list:
#             if stock_uom and stock_uom.lower() == "pcs":
#                 finished_qty = cint(batch_data["total_roll_qty"])
#                 finished_uom = batch_data["uom"]
#             else:
#                 finished_qty = round_to_decimals(batch_data["total_roll_weight"])
#                 finished_uom = batch_data["uom"]

#             if finished_qty <= 0:
#                 frappe.logger().warning(
#                     f"Skipping finished item batch {batch_data['batch']}: zero qty"
#                 )
#                 continue

#             frappe.logger().info(
#                 f"Finished item: {batch_data['item_code']} | "
#                 f"batch={batch_data['batch']} | qty={finished_qty} {finished_uom}"
#             )

#             stock_entry.append("items", {
#                 "t_warehouse":       work_order.fg_warehouse or "NAP_E1/FF/A02 - PSS",
#                 "item_code":         batch_data["item_code"],
#                 "qty":               finished_qty,
#                 "uom":               finished_uom,
#                 "stock_uom":         finished_uom,
#                 "conversion_factor": 1.0,
#                 "transfer_qty":      finished_qty,
#                 "batch_no":          batch_data["batch"],
#                 "is_finished_item":  1,
#                 "is_scrap_item":     0,
#             })

#         # ==================== STEP 7: Validate items ====================
#         if not stock_entry.items:
#             frappe.throw(_("No items to transfer. Please check material transfer entries."))

#         source_items   = [i for i in stock_entry.items if not i.is_finished_item]
#         finished_items = [i for i in stock_entry.items if i.is_finished_item]

#         if not source_items:
#             frappe.throw(_("No source items (raw materials) found for manufacture."))

#         if not finished_items:
#             frappe.throw(_("No finished items found for manufacture."))

#         # ==================== STEP 8: Safety — remove any zero-qty rows ====================
#         before_count = len(stock_entry.items)
#         stock_entry.items = [i for i in stock_entry.items if flt(i.qty) > 0]
#         after_count = len(stock_entry.items)

#         if before_count != after_count:
#             frappe.logger().warning(
#                 f"Zero-qty safety filter removed {before_count - after_count} rows."
#             )

#         if not stock_entry.items:
#             frappe.throw(_("All items have zero quantity after safety filter."))

#         # ==================== STEP 9: Pre-insert log ====================
#         frappe.logger().info("=" * 80)
#         frappe.logger().info("BATCH TRACKING SUMMARY:")
#         frappe.logger().info("=" * 80)
#         frappe.logger().info(f"stock_uom         : {stock_uom}")
#         frappe.logger().info(f"fg_completed_qty  : {qty}")
#         frappe.logger().info(f"final_weight (raw): {final_weight}")
#         frappe.logger().info("-" * 80)
#         frappe.logger().info("RAW MATERIALS:")
#         for item in stock_entry.items:
#             if not item.is_finished_item:
#                 frappe.logger().info(
#                     f"  {item.item_code} | qty={item.qty} {item.uom} | "
#                     f"batch={item.batch_no or 'None'} | from={item.s_warehouse}"
#                 )
#         frappe.logger().info("FINISHED GOODS:")
#         for item in stock_entry.items:
#             if item.is_finished_item:
#                 frappe.logger().info(
#                     f"  {item.item_code} | qty={item.qty} {item.uom} | "
#                     f"batch={item.batch_no} | to={item.t_warehouse}"
#                 )
#         frappe.logger().info("=" * 80)

#         # ==================== STEP 10: Insert ====================
#         stock_entry.insert(ignore_permissions=True)

#         # Flush to DB before reload.
#         frappe.db.commit()

#         # ==================== STEP 11: Reload from DB before submit ====================
#         #
#         # WHY THIS IS CRITICAL:
#         #
#         # Frappe's insert() sequence is:
#         #   1. validate()        — items have correct qty ✓
#         #   2. db_insert()       — DB is written with correct qty ✓
#         #   3. on_update() hooks — run AFTER DB write, on the same in-memory object
#         #
#         # In ERPNext v14/v15, on_update triggers Serial/Batch Bundle handlers for
#         # items that have a batch_no. For a freshly created FG batch that does not
#         # yet have a Serial-Batch Bundle document, the handler can reset item.qty = 0
#         # in-memory as a side effect (bundle-qty mismatch resolution). This mutation
#         # is NOT written back to DB — the DB still holds the correct value from step 2.
#         #
#         # When submit() then calls save() → validate() on that same poisoned in-memory
#         # object, it sees qty = 0 on the FG row and raises InvalidQtyError.
#         #
#         # Fix: discard the in-memory object entirely after insert and reload a clean
#         # copy straight from DB. DB state is always authoritative and correct here.
#         #
#         stock_entry_name = stock_entry.name
#         stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)

#         frappe.logger().info(
#             f"Reloaded {stock_entry_name} from DB. FG qtys after reload: "
#             + str([
#                 f"{i.item_code}={i.qty}"
#                 for i in stock_entry.items if i.is_finished_item
#             ])
#         )

#         # ==================== STEP 12: Post-reload sanity check ====================
#         # If qty is still 0 after a DB reload, something wrote 0 into the DB itself —
#         # which would indicate a custom before_save hook or trigger on Stock Entry Detail.
#         for fg_row in [i for i in stock_entry.items if i.is_finished_item]:
#             if flt(fg_row.qty) <= 0:
#                 frappe.log_error(
#                     f"FG item qty is 0 even after DB reload.\n"
#                     f"Stock Entry : {stock_entry.name}\n"
#                     f"Item        : {fg_row.item_code}\n"
#                     f"Batch       : {fg_row.batch_no}\n"
#                     f"The DB itself has qty=0. Check for custom before_save hooks "
#                     f"or database triggers on Stock Entry / Stock Entry Detail.",
#                     "Manufacture Entry FG Qty Zero After Reload"
#                 )
#                 frappe.throw(
#                     _("Finished goods qty is 0 even after DB reload for item {0} "
#                       "(batch: {1}). Check Error Log for details.").format(
#                         frappe.bold(fg_row.item_code),
#                         frappe.bold(fg_row.batch_no or "None")
#                     )
#                 )

#         # ==================== STEP 13: Submit ====================
#         stock_entry.submit()

#         # Save reference back to Roll Packing List
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

        
