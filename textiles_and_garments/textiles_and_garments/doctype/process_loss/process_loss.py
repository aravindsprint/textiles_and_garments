# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe.utils import flt


class ProcessLoss(Document):
	pass



@frappe.whitelist()
def calculate_process_loss(docname, purchase_orders):
    if isinstance(purchase_orders, str):
        purchase_orders = json.loads(purchase_orders)

    print("\n\nOriginal purchase_orders:\n", purchase_orders)
    
    # Extract only purchase_order values from non-empty rows
    purchase_order_list = [
        row.get("purchase_order") for row in purchase_orders
        if row.get("purchase_order") not in [None, ""]
    ]
    
    print("\n\nFiltered purchase orders:\n", purchase_order_list)
    getStockEntryDetails(purchase_order_list)



@frappe.whitelist()
def getStockEntryDetails(purchase_order_list):
    print("\n\ngetStockEntryDetails\n\n",purchase_order_list)



import json
import frappe

@frappe.whitelist()
def calculate_process_loss(docname, purchase_orders):
    if isinstance(purchase_orders, str):
        purchase_orders = json.loads(purchase_orders)

    print("\n\nOriginal purchase_orders:\n", purchase_orders)
    
    # Extract only purchase_order values from non-empty rows
    purchase_order_list = [
        row.get("purchase_order") for row in purchase_orders
        if row.get("purchase_order") not in [None, ""]
    ]
    
    print("\n\nFiltered purchase orders:\n", purchase_order_list)
    return get_subcontracting_order_details(purchase_order_list)

@frappe.whitelist()
def get_subcontracting_order_details(purchase_order_list):
    print("\n\nget_subcontracting_order_details\n\n", purchase_order_list)
    
    if not purchase_order_list:
        return []
    
    # Convert to tuple for SQL query
    po_tuple = tuple(purchase_order_list)
    
    # Get all Subcontracting Orders linked to these Purchase Orders
    sco_list = frappe.db.sql("""
        SELECT name, purchase_order, supplier, total_qty, status
        FROM `tabSubcontracting Order`
        WHERE purchase_order IN %s AND docstatus = 1
    """, (po_tuple,), as_dict=True)
    
    print("\n\nSubcontracting Orders found:\n", sco_list)
    
    result = []
    
    for sco in sco_list:
        # Get all supplied items for this Subcontracting Order
        supplied_items = frappe.get_all(
            "Subcontracting Order Supplied Item",
            filters={"parent": sco.name},
            fields=["*"]  # Get all fields from the supplied items table
        )
        
        # Add the SCO details along with its supplied items
        sco_data = {
            "subcontracting_order": sco.name,
            "purchase_order": sco.purchase_order,
            "supplier": sco.supplier,
            "total_qty": sco.total_qty,
            "status": sco.status,
            "supplied_items": supplied_items
        }
        
        result.append(sco_data)
    
    print("\n\nFinal result with supplied items:\n", result)
    return result        