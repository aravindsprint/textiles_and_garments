# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from collections import defaultdict
import json
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today
from frappe.utils import nowdate, add_days, getdate





class PlanItems(Document):
    def validate(self):
        planned_item_codes = [d.item_code for d in self.plan_item_planned_wise]
        for row in self.get('plan_items_summary'):
            if row.item_code not in [d.item_code for d in self.plan_items_detail]:
                if row.item_code in planned_item_codes:
                    frappe.throw(f"Cannot remove item {row.item_code} from Plan Items Detail — it is already planned.")
        self.update_plan_items_summary()

    # def update_plan_items_summary(self):
    #     # Check if summary table already has rows — if yes, skip
    #     if self.get("plan_items_summary"):
    #         return  # Do not execute if summary already exists

    #     # Step 1: Aggregate qty by item_code from plan_items_detail
    #     item_totals = defaultdict(float)
    #     for row in self.get("plan_items_detail", []):
    #         if row.item_code:
    #             item_totals[row.item_code] += row.qty or 0

    #     # Step 2: Clear existing summary table (precaution)
    #     self.set("plan_items_summary", [])

    #     # Step 3: Rebuild summary rows with data from Item doctype
    #     for item_code, qty in item_totals.items():
    #         item_details = frappe.db.get_value(
    #             "Item",
    #             item_code,
    #             ["custom_commercial_name", "stock_uom"],
    #             as_dict=True
    #         ) or {}

    #         self.append("plan_items_summary", {
    #             "item_code": item_code,
    #             "commercial_name": item_details.get("custom_commercial_name"),
    #             "uom": item_details.get("stock_uom"),
    #             "qty": qty,
    #             "planned_qty": 0,
    #             "need_to_plan_qty": qty
    #         })
    def update_plan_items_summary(self):
        print("\n\nself\n\n",self.get("plan_items_summary"))
        # REMOVED: The check 'if self.get("plan_items_summary"): return'
        # The function will now always rebuild and reorder the summary.
        if not self.plan_items_summary:
	        print("\nupdate_plan_items_summary\n")
	        # Step 1: Aggregate qty by item_code from plan_items_detail
	        item_totals = defaultdict(float)
	        for row in self.get("plan_items_detail", []):
	            if row.item_code:
	                item_totals[row.item_code] += row.qty or 0

	        # Step 2: Clear existing summary table (precaution before rebuilding)
	        self.set("plan_items_summary", [])

	        # Create a temporary list to hold the newly built summary rows
	        temp_new_summary_rows = []

	        # Step 3: Rebuild summary rows with data from Item doctype into the temporary list
	        for item_code, qty in item_totals.items():
	            item_details = frappe.db.get_value(
	                "Item",
	                item_code,
	                ["custom_commercial_name", "stock_uom"],
	                as_dict=True
	            ) or {}

	            temp_new_summary_rows.append({
	                "item_code": item_code,
	                "commercial_name": item_details.get("custom_commercial_name"),
	                "uom": item_details.get("stock_uom"),
	                "qty": qty,
	                "planned_qty": 0,
	                "need_to_plan_qty": qty
	            })

	        # --- Step 4: Rearrange plan_items_summary based on plan_items_detail order ---
	        # Get the desired order of item_codes from plan_items_detail
	        ordered_item_codes = [detail_row.item_code for detail_row in self.get("plan_items_detail", [])]

	        # Create a dictionary for quick lookup of the newly built summary rows by item_code
	        new_summary_map = {row["item_code"]: row for row in temp_new_summary_rows}

	        # Construct the final, ordered list for plan_items_summary
	        final_ordered_summary = []
	        for item_code in ordered_item_codes:
	            if item_code in new_summary_map:
	                final_ordered_summary.append(new_summary_map[item_code])
	            # Optional: Handle if an item_code from detail is not found in the new summary
	            # (e.g., if it was filtered out or not processed for some reason).
	            # For this scenario, we assume all detail items will have a summary entry.
	                
	        print("\n\nfinal_ordered_summary\n\n",final_ordered_summary)
	        # Assign the newly ordered list back to the child table
	        self.set("plan_items_summary", final_ordered_summary)

	        # Note: This function is typically called from a hook (e.g., before_save)
	        # where the parent document will be saved automatically.
	        # If this is a standalone function, you might need a self.save() here.


@frappe.whitelist()
def get_selected_sales_order():
    # Fetch Sales Order where sales order field contains any of the given Sales Order Items
    sales_orders = frappe.get_all(
        "Sales Order",
        filters={
            "docstatus": 1
        },
        fields=["*"]
    )
    return sales_orders


@frappe.whitelist()
def get_sales_order_items(sales_orders):
    """
    Fetch Sales Order Items for the given Sales Orders
    """
    if isinstance(sales_orders, str):
        try:
            sales_orders = json.loads(sales_orders)
        except:
            frappe.throw("Invalid format for sales_orders parameter")
    
    if not sales_orders:
        return []
    
    # Fetch Sales Order Items
    items = frappe.get_all(
        "Sales Order Item",
        filters={
            "parent": ["in", sales_orders],
            "docstatus": 1
        },
        fields=["parent", "item_code", "qty", "uom"]
    )
    
    return items




@frappe.whitelist()
def get_bom_items(bom_names):
    """
    Fetch items from BOM's child table
    """
    if isinstance(bom_names, str):
        try:
            bom_names = json.loads(bom_names)
        except:
            frappe.throw("Invalid format for bom_names parameter")
    
    if not bom_names:
        return []
    
    # Fetch BOM items
    bom_items = frappe.get_all(
        "BOM Item",
        filters={
            "parent": ["in", bom_names],
            "docstatus": 1
        },
        fields=["parent", "item_code", "qty", "uom", "idx"]
    )
    
    return bom_items





@frappe.whitelist()
def get_all_bom_items_recursive(bom_names):
    """
    Fetch all BOM items recursively for multi-level BOMs
    """
    if isinstance(bom_names, str):
        try:
            bom_names = json.loads(bom_names)
        except:
            frappe.throw("Invalid format for bom_names parameter")
    
    if not bom_names:
        return {}
    
    result = {}
    
    for bom_name in bom_names:
        result[bom_name] = get_bom_items_recursive(bom_name)
    
    return result

def get_bom_items_recursive(bom_name, level=1, max_level=10):
    """
    Recursively fetch BOM items for a given BOM
    """
    if level > max_level:
        return []
    
    bom_items = frappe.get_all(
        "BOM Item",
        filters={
            "parent": bom_name,
            "docstatus": 1
        },
        fields=["item_code", "qty", "uom", "idx"]
    )
    
    # Check if each item has its own BOM
    for item in bom_items:
        # Check if this item has a BOM
        has_bom = frappe.db.exists("BOM", {
            "item": item["item_code"],
            "docstatus": 1,
            "is_active": 1
        })
        
        item["has_bom"] = bool(has_bom)
        item["bom_name"] = bom_name
        
        if has_bom:
            # Get the latest BOM for this item
            latest_bom = frappe.get_all(
                "BOM",
                filters={
                    "item": item["item_code"],
                    "docstatus": 1,
                    "is_active": 1
                },
                fields=["name", "quantity"],
                order_by="creation desc",
                limit=1
            )
            
            if latest_bom:
                item["bom_quantity"] = latest_bom[0]["quantity"]
                # Recursively get child BOM items
                item["child_bom_items"] = get_bom_items_recursive(
                    latest_bom[0]["name"], 
                    level + 1, 
                    max_level
                )
    
    return bom_items

@frappe.whitelist()
def get_latest_boms_for_items(item_codes):
    """
    Fetch the latest BOM for each item code with quantity information
    """
    if isinstance(item_codes, str):
        try:
            item_codes = json.loads(item_codes)
        except:
            frappe.throw("Invalid format for item_codes parameter")
    
    if not item_codes:
        return {}
    
    boms_by_item = {}
    
    for item_code in item_codes:
        # Get the latest BOM for this item
        latest_bom = frappe.get_all(
            "BOM",
            filters={
                "item": item_code,
                "docstatus": 1,
                "is_active": 1
            },
            fields=["name", "creation", "item", "quantity"],
            order_by="creation desc",
            limit=1
        )
        
        if latest_bom:
            boms_by_item[item_code] = latest_bom[0]
        else:
            boms_by_item[item_code] = None
    
    return boms_by_item



# @frappe.whitelist()
# def get_bom_details_from_plan_items(docname, bom, plan_items_detail, search_batch=None):
#     if not bom:
#         return []

    
#     print("\n\ndocname,\n\n",docname)
#     print("\n\nbom,\n\n",bom)
#     print("\n\nplan_items_detail,\n\n",plan_items_detail)
#     # print("\n\ndocname,\n\n",docname)
#     bom_doc = frappe.get_doc("BOM", bom)
#     item_codes =  [bom_doc.item]

#     if not item_codes:
#         return []

#     filters = frappe._dict({
#         "item_codes": item_codes,
#         "include_expired_batches": False,
#         "to_date": today()
#     })

#     batchwise_data = get_batchwise_data_from_stock_ledger(filters)
#     batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)
#     data = parse_batchwise_data(batchwise_data)
#     print("\n\ndata 1\n\n",data)
#     data = sum_balance_qty(data)
#     print("\n\ndata 2\n\n",data)
#     return data

#     # # Filter data based on search_batch if provided
#     # # if search_batch:
#     # #     search_batches = [b.strip() for b in search_batch.split(',')]
#     # #     print("\n\nsearch_batches\n\n",search_batches)
#     # #     data = [row for row in data if row.get("batch_no") in search_batches]
#     # if search_batch:
#     #     search_patterns = [b.strip().replace('%', '') for b in search_batch.split(',')]
#     #     # print("\n\nsearch_patterns\n\n", search_patterns)
        
#     #     data = [
#     #         row for row in data 
#     #         if any(
#     #             pattern in (row.get("batch_no") or "")
#     #             for pattern in search_patterns
#     #         )
#     #     ]

#     # # Fetch previous reservations from Plans Stock Item
#     # reserved_map = get_reserved_quantities(docname)

#     # for row in data:
#     #     key = (row.get("warehouse"), row.get("batch_no"))
#     #     # print("\n\nkey\n\n",key)
#     #     # print("\n\nreserved_map.get(key, 0)\n\n",reserved_map.get(key, 0))
#     #     previous_reserved_qty = reserved_map.get(key, 0)
#     #     row["previous_reserved_qty"] = previous_reserved_qty
#     #     row["avail_qty"] = flt(row.get("balance_qty")) - flt(previous_reserved_qty)

#     # return data



# def sum_balance_qty(data):
#     total_balance = 0
#     for item in data:
#         total_balance += item['balance_qty']
    
#     return {
#         'item_code': data[0]['item_code'] if data else None,
#         'balance_qty': total_balance
#     }

@frappe.whitelist()
def get_stock_for_item(docname, item_code, search_batch=None):
    """
    Get stock data for a specific item
    """
    if not item_code:
        return []

    filters = frappe._dict({
        "item_codes": [item_code],  # Search for the specific item
        "include_expired_batches": False,
        "to_date": today()
    })

    batchwise_data = get_batchwise_data_from_stock_ledger(filters)
    batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)
    data = parse_batchwise_data(batchwise_data)

    # Filter data based on search_batch if provided
    if search_batch:
        search_patterns = [b.strip().replace('%', '') for b in search_batch.split(',')]
        data = [
            row for row in data 
            if any(pattern in (row.get("batch_no") or "") for pattern in search_patterns)
        ]

    # Fetch previous reservations
    reserved_map = get_reserved_quantities(docname)

    for row in data:
        key = (row.get("warehouse"), row.get("batch_no"))
        previous_reserved_qty = reserved_map.get(key, 0)
        row["previous_reserved_qty"] = previous_reserved_qty
        row["avail_qty"] = flt(row.get("balance_qty")) - flt(previous_reserved_qty)

    return data



def get_reserved_quantities(exclude_docname):
    """
    Returns a dictionary with key (warehouse, batch) and value as 
    (sum of all reserve_qty) - (sum of all actual_delivered_qty)
    from all 'Plans Stock Item' entries excluding the current docname.
    """
    reserved_map = {}

    # First get all reserve quantities grouped by warehouse and batch
    # reserve_results = frappe.db.get_all(
    #     "Plans Stock Item",
    #     fields=["warehouse", "batch", "sum(reserve_qty) as total_reserve"],
    #     filters={"parent": ["!=", exclude_docname], "docstatus": ["=", 1]},
    #     group_by="warehouse, batch"
    # )

    reserve_results = frappe.db.get_all(
        "Serial and Batch Entry Plans",
        fields=["warehouse", "batch_no", "sum(qty) as total_reserve"],
        filters={"parenttype": "Production Stock Reservation", "docstatus": ["=", 1]},
        group_by="warehouse, batch_no"
    )

    # print("\n\nreserve_results\n\n", reserve_results)

    # Create a dictionary of all actual delivered quantities by warehouse and batch
    actual_delivered_map = {}
    actual_delivered_results = frappe.db.get_all(
        "Serial and Batch Entry Plans",
        fields=["warehouse", "batch_no", "sum(actual_delivered_qty) as total_delivered"],
        filters={"parenttype": "Production Stock Reservation"},
        group_by="warehouse, batch_no"
    )

    # print("\n\nactual_delivered_results\n\n", actual_delivered_results)

    for entry in actual_delivered_results:
        key = (entry.warehouse, entry.batch_no)
        actual_delivered_map[key] = flt(entry.total_delivered or 0)

    # Create a dictionary of all short close quantities by warehouse and batch
    short_close_map = {}
    short_close_results = frappe.db.get_all(
        "Serial and Batch Entry Plans",
        fields=["warehouse", "batch_no", "sum(short_close_qty) as total_short_close"],
        filters={"parenttype": "Production Stock Reservation", "docstatus": 1},
        group_by="warehouse, batch_no"
    )
    # print("\n\nshort_close_results\n\n",short_close_results)

    for entry in short_close_results:
        key = (entry.warehouse, entry.batch_no)
        short_close_map[key] = flt(entry.total_short_close or 0)

    # Calculate final reserved quantities
    for row in reserve_results:
        key = (row.warehouse, row.batch_no)
        # print("\n\nkey\n\n",key)
        total_reserve = flt(row.total_reserve or 0)
        # print("\n\ntotal_reserve\n\n",total_reserve)
        total_delivered = actual_delivered_map.get(key, 0)
        # print("\n\ntotal_delivered\n\n",total_delivered)
        total_short_close = short_close_map.get(key, 0)
        # print("\n\ntotal_short_close\n\n",total_short_close)
        
        adjusted_reserve = total_reserve - total_delivered - total_short_close
        
        if adjusted_reserve > 0:
            reserved_map[key] = adjusted_reserve

    return reserved_map


def parse_batchwise_data(batchwise_data):
    data = []
    for key in batchwise_data:
        d = batchwise_data[key]
        if flt(d.balance_qty) == 0:
            continue
        data.append(d)
    return data


def get_batchwise_data_from_stock_ledger(filters):
    batchwise_data = frappe._dict()
    table = frappe.qb.DocType("Stock Ledger Entry")
    batch = frappe.qb.DocType("Batch")
    item = frappe.qb.DocType("Item")

    query = (
        frappe.qb.from_(table)
        .inner_join(batch).on(table.batch_no == batch.name)
        .inner_join(item).on(table.item_code == item.name)
        .select(
            table.item_code,
            table.warehouse,
            table.batch_no,
            item.stock_uom,
            Sum(table.actual_qty).as_("balance_qty"),
        )
        .where(table.is_cancelled == 0)
        .groupby(table.item_code, table.warehouse, table.batch_no, item.stock_uom)
    )

    if filters.get("item_codes"):
        query = query.where(table.item_code.isin(filters.item_codes))

    for d in query.run(as_dict=True):
        key = (d.item_code, d.warehouse, d.batch_no)
        batchwise_data.setdefault(key, d)

    return batchwise_data


def get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters):
    table = frappe.qb.DocType("Stock Ledger Entry")
    ch_table = frappe.qb.DocType("Serial and Batch Entry")
    batch = frappe.qb.DocType("Batch")
    item = frappe.qb.DocType("Item")

    query = (
        frappe.qb.from_(table)
        .inner_join(ch_table).on(table.serial_and_batch_bundle == ch_table.parent)
        .inner_join(batch).on(ch_table.batch_no == batch.name)
        .inner_join(item).on(table.item_code == item.name)
        .select(
            table.item_code,
            ch_table.warehouse,
            ch_table.batch_no,
            item.stock_uom,
            Sum(ch_table.qty).as_("balance_qty"),
        )
        .where((table.is_cancelled == 0) & (table.docstatus == 1))
        .groupby(table.item_code, ch_table.warehouse, ch_table.batch_no, item.stock_uom)
    )

    if filters.get("item_codes"):
        query = query.where(table.item_code.isin(filters.item_codes))

    for d in query.run(as_dict=True):
        key = (d.item_code, d.warehouse, d.batch_no)
        if key in batchwise_data:
            batchwise_data[key].balance_qty += flt(d.balance_qty)
        else:
            batchwise_data.setdefault(key, d)

    return batchwise_data









