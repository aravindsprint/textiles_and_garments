# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from collections import defaultdict
import json





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




