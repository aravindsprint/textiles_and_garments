# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe.utils import flt



class ProcessLoss(Document):
	pass



# @frappe.whitelist()
# def calculate_process_loss(docname, purchase_orders):
#     if isinstance(purchase_orders, str):
#         purchase_orders = json.loads(purchase_orders)

#     print("\n\nOriginal purchase_orders:\n", purchase_orders)
    
#     # Extract only purchase_order values from non-empty rows
#     purchase_order_list = [
#         row.get("purchase_order") for row in purchase_orders
#         if row.get("purchase_order") not in [None, ""]
#     ]
    
#     print("\n\nFiltered purchase orders:\n", purchase_order_list)
#     getStockEntryDetails(purchase_order_list)



# @frappe.whitelist()
# def getStockEntryDetails(purchase_order_list):
#     print("\n\ngetStockEntryDetails\n\n",purchase_order_list)

# @frappe.whitelist()
# def calculate_process_loss(docname, purchase_orders):
#     if isinstance(purchase_orders, str):
#         purchase_orders = json.loads(purchase_orders)

#     print("\n\nOriginal purchase_orders:\n", purchase_orders)
    
#     # Extract only purchase_order values from non-empty rows
#     purchase_order_list = [
#         row.get("purchase_order") for row in purchase_orders
#         if row.get("purchase_order") not in [None, ""]
#     ]
    
#     print("\n\nFiltered purchase orders:\n", purchase_order_list)
    
#     # Get the supplied items data
#     all_supplied_items = get_subcontracting_order_details(purchase_order_list)
    
#     # Get the Process Loss document
#     process_loss_doc = frappe.get_doc("Process Loss", docname)
    
#     # Clear existing sent_details
#     process_loss_doc.set("sent_details", [])
    
#     # Insert new data into sent_details table
#     for item in all_supplied_items:
#         process_loss_doc.append("sent_details", {
#             "purchase_order": item.get("purchase_order"),
#             "subcontracting_order": item.get("subcontracting_order"),
#             "item_code": item.get("main_item_code") or item.get("rm_item_code"),  # Adjust field name as needed
#             "po_qty": item.get("required_qty") or item.get("qty"),  # Adjust field name as needed
#             "sent_qty": item.get("consumed_qty") or 0,  # Adjust field name as needed
#             "uom": item.get("stock_uom") or item.get("uom")  # Adjust field name as needed
#             # stock_entry will be filled later when stock entries are created
#         })
    
#     # Save the document
#     process_loss_doc.save()
#     frappe.db.commit()
    
#     return all_supplied_items

# @frappe.whitelist()
# def get_subcontracting_order_details(purchase_order_list):
#     print("\n\nget_subcontracting_order_details\n\n", purchase_order_list)
    
#     if not purchase_order_list:
#         return []
    
#     # Convert to tuple for SQL query
#     po_tuple = tuple(purchase_order_list)
#     print("\npo_tuple\n", po_tuple)
    
#     # Get all Subcontracting Orders linked to these Purchase Orders
#     sco_list = frappe.db.sql("""
#         SELECT name, purchase_order, supplier, total_qty, status
#         FROM `tabSubcontracting Order`
#         WHERE purchase_order IN %s AND docstatus = 1
#     """, (po_tuple,), as_dict=True)
    
#     print("\n\nSubcontracting Orders found:\n", sco_list)
    
#     all_supplied_items = []  # Main array for all supplied items
    
#     for sco in sco_list:
#         # Get all supplied items for this Subcontracting Order
#         supplied_items = frappe.get_all(
#             "Subcontracting Order Supplied Item",
#             filters={"parent": sco.name},
#             fields=["*"]  # Get all fields from the supplied items table
#         )
        
#         # Add SCO reference to each supplied item and add to main array
#         for item in supplied_items:
#             item_with_sco_ref = item.copy()
#             item_with_sco_ref.update({
#                 "subcontracting_order": sco.name,
#                 "purchase_order": sco.purchase_order,
#                 "supplier": sco.supplier,
#                 "sco_total_qty": sco.total_qty,
#                 "sco_status": sco.status
#             })
#             all_supplied_items.append(item_with_sco_ref)
    
#     print("\n\nAll supplied items in separate array:\n", all_supplied_items)
    
#     return all_supplied_items



# @frappe.whitelist()
# def calculate_process_loss(docname, purchase_orders):
#     if isinstance(purchase_orders, str):
#         purchase_orders = json.loads(purchase_orders)

#     print("\n\nOriginal purchase_orders:\n", purchase_orders)
    
#     # Extract only purchase_order values from non-empty rows
#     purchase_order_list = [
#         row.get("purchase_order") for row in purchase_orders
#         if row.get("purchase_order") not in [None, ""]
#     ]
    
#     print("\n\nFiltered purchase orders:\n", purchase_order_list)
    
#     # Get the supplied items data
#     all_supplied_items = get_subcontracting_order_details(purchase_order_list)
#     print("\n\nall_supplied_items\n\n", all_supplied_items)
    
#     return all_supplied_items

# @frappe.whitelist()
# def get_subcontracting_order_details(purchase_order_list):
#     print("\n\nget_subcontracting_order_details\n\n", purchase_order_list)
    
#     if not purchase_order_list:
#         return []
    
#     # Convert to tuple for SQL query
#     po_tuple = tuple(purchase_order_list)
#     print("\npo_tuple\n", po_tuple)
    
#     # Get all Subcontracting Orders linked to these Purchase Orders
#     sco_list = frappe.db.sql("""
#         SELECT name
#         FROM `tabSubcontracting Order`
#         WHERE purchase_order IN %s AND docstatus = 1
#     """, (po_tuple,), as_dict=False)
    
#     print("\n\nSubcontracting Orders found:\n", sco_list)
    
#     # Extract only the name values from the result
#     sco_names = [row[0] for row in sco_list] if sco_list else []
    
#     # Get all Stock Entries linked to these Subcontracting Orders
#     stock_entries = get_stock_entries_for_sco(sco_names)
    
#     return stock_entries

# def get_stock_entries_for_sco(sco_names):
#     if not sco_names:
#         return []
    
#     # Convert to tuple for SQL query
#     sco_tuple = tuple(sco_names)
#     print("\nsco_tuple for stock entries\n", sco_tuple)
    
#     # Get all Stock Entries linked to these Subcontracting Orders
#     stock_entry_list = frappe.db.sql("""
#         SELECT name, subcontracting_order, purpose, posting_date, total_outgoing_value, total_incoming_value
#         FROM `tabStock Entry`
#         WHERE subcontracting_order IN %s AND docstatus = 1 AND purchase_order = 'Send to Subcontractor'
#         ORDER BY posting_date
#     """, (sco_tuple,), as_dict=True)
    
#     print("\n\nStock Entries found:\n", stock_entry_list)
    
#     # Fetch stock entry details for each stock entry
#     for stock_entry in stock_entry_list:
#         stock_entry['items'] = get_stock_entry_details(stock_entry['name'])
    
#     return stock_entry_list

# def get_stock_entry_details(stock_entry_name):
#     """Fetch all items from Stock Entry Detail table for a given Stock Entry"""
#     stock_entry_details = frappe.db.sql("""
#         SELECT 
#             item_code, qty, uom, 
#             s_warehouse, t_warehouse, po_detail
#         FROM `tabStock Entry Detail`
#         WHERE parent = %s
#         ORDER BY idx
#     """, (stock_entry_name,), as_dict=True)
    
#     return stock_entry_details


# @frappe.whitelist()
# def calculate_process_loss(docname, purchase_orders):
#     if isinstance(purchase_orders, str):
#         purchase_orders = json.loads(purchase_orders)

#     print("\n\nOriginal purchase_orders:\n", purchase_orders)
    
#     # Extract only purchase_order values from non-empty rows
#     purchase_order_list = [
#         row.get("purchase_order") for row in purchase_orders
#         if row.get("purchase_order") not in [None, ""]
#     ]
    
#     print("\n\nFiltered purchase orders:\n", purchase_order_list)
    
#     # Get the supplied items data
#     all_supplied_items = get_subcontracting_order_details(purchase_order_list)
#     print("\n\nall_supplied_items\n\n", all_supplied_items)
    
#     # Update the Process Loss document with the sent_details
#     update_sent_details(docname, all_supplied_items)
    
#     return all_supplied_items

# def update_sent_details(docname, sent_details_data):
#     """Update the sent_details table in the Process Loss document"""
#     try:
#         # Get the Process Loss document
#         process_loss_doc = frappe.get_doc("Process Loss", docname)
        
#         # Clear existing sent_details
#         process_loss_doc.set("sent_details", [])
        
#         # Add new sent_details rows
#         for item in sent_details_data:
#             process_loss_doc.append("sent_details", {
#                 "purchase_order": item.get("purchase_order"),
#                 "subcontracting_order": item.get("subcontracting_order"),
#                 "item_code": item.get("item_code"),
#                 "po_qty": item.get("po_qty", 0),
#                 "sent_qty": item.get("sent_qty", 0),
#                 "stock_entry": item.get("stock_entry"),
#                 "uom": item.get("uom", "")
#             })
        
#         # Save the document
#         process_loss_doc.save()
#         frappe.db.commit()
        
#         print(f"\n\nSuccessfully updated sent_details for {docname}")
#         return True
        
#     except Exception as e:
#         frappe.log_error(f"Error updating sent_details for {docname}: {str(e)}")
#         frappe.throw(f"Failed to update sent details: {str(e)}")
#         return False

# @frappe.whitelist()
# def get_subcontracting_order_details(purchase_order_list):
#     print("\n\nget_subcontracting_order_details\n\n", purchase_order_list)
    
#     if not purchase_order_list:
#         return []
    
#     # Convert to tuple for SQL query
#     po_tuple = tuple(purchase_order_list)
#     print("\npo_tuple\n", po_tuple)
    
#     # Get all Subcontracting Orders linked to these Purchase Orders
#     sco_list = frappe.db.sql("""
#         SELECT name, purchase_order
#         FROM `tabSubcontracting Order`
#         WHERE purchase_order IN %s AND docstatus = 1
#     """, (po_tuple,), as_dict=True)
    
#     print("\n\nSubcontracting Orders found:\n", sco_list)
    
#     if not sco_list:
#         return []
    
#     # Get SCO names
#     sco_names = [sco['name'] for sco in sco_list]
#     sco_tuple = tuple(sco_names)
    
#     # Get Subcontracting Order Supplied Items (raw materials)
#     sco_supplied_items = frappe.db.sql("""
#         SELECT 
#             parent as subcontracting_order,
#             rm_item_code as item_code,
#             main_item_code as po_item_code,
#             required_qty as po_qty
#         FROM `tabSubcontracting Order Supplied Item`
#         WHERE parent IN %s
#     """, (sco_tuple,), as_dict=True)
    
#     print("\n\nSubcontracting Order Supplied Items found:\n", sco_supplied_items)
    
#     # Get UOM for each item from Item master
#     item_codes = list(set([item['item_code'] for item in sco_supplied_items if item['item_code']]))
#     item_uom_map = {}
    
#     if item_codes:
#         item_tuple = tuple(item_codes)
#         item_data = frappe.db.sql("""
#             SELECT item_code, stock_uom
#             FROM `tabItem`
#             WHERE item_code IN %s
#         """, (item_tuple,), as_dict=True)
        
#         item_uom_map = {item['item_code']: item['stock_uom'] for item in item_data}
    
#     print("\n\nItem UOM Map:\n", item_uom_map)
    
#     # Get all Stock Entries linked to these Subcontracting Orders
#     stock_entries_data = get_stock_entries_for_sco(sco_names)
    
#     # Combine data for sent_details
#     sent_details = []
    
#     for sco in sco_list:
#         # Find supplied items for this SCO
#         sco_items_filtered = [item for item in sco_supplied_items if item['subcontracting_order'] == sco['name']]
        
#         # Find matching stock entries for this SCO
#         matching_entries = [
#             entry for entry in stock_entries_data 
#             if entry['subcontracting_order'] == sco['name']
#         ]
        
#         for sco_item in sco_items_filtered:
#             uom = item_uom_map.get(sco_item['item_code'], '')
            
#             for entry in matching_entries:
#                 # Find matching items in the stock entry
#                 for stock_item in entry.get('items', []):
#                     if stock_item.get('item_code') == sco_item['item_code']:
#                         sent_details.append({
#                             'purchase_order': sco['purchase_order'],
#                             'subcontracting_order': sco['name'],
#                             'item_code': sco_item['item_code'],
#                             'po_qty': sco_item['po_qty'],
#                             'sent_qty': stock_item.get('qty', 0),
#                             'stock_entry': entry['name'],
#                             'uom': uom
#                         })
    
#     print("\n\nFinal sent_details:\n", sent_details)
#     return sent_details

# def get_stock_entries_for_sco(sco_names):
#     if not sco_names:
#         return []
    
#     # Convert to tuple for SQL query
#     sco_tuple = tuple(sco_names)
#     print("\nsco_tuple for stock entries\n", sco_tuple)
    
#     # Get all Stock Entries linked to these Subcontracting Orders with purpose "Send to Subcontractor"
#     stock_entry_list = frappe.db.sql("""
#         SELECT name, subcontracting_order, purpose, posting_date
#         FROM `tabStock Entry`
#         WHERE subcontracting_order IN %s AND docstatus = 1 AND purpose = 'Send to Subcontractor'
#         ORDER BY posting_date
#     """, (sco_tuple,), as_dict=True)
    
#     print("\n\nStock Entries found:\n", stock_entry_list)
    
#     # Fetch stock entry details for each stock entry
#     for stock_entry in stock_entry_list:
#         stock_entry['items'] = get_stock_entry_details(stock_entry['name'])
    
#     return stock_entry_list

# def get_stock_entry_details(stock_entry_name):
#     """Fetch all items from Stock Entry Detail table for a given Stock Entry"""
#     stock_entry_details = frappe.db.sql("""
#         SELECT 
#             item_code, qty, uom, 
#             s_warehouse, t_warehouse, po_detail
#         FROM `tabStock Entry Detail`
#         WHERE parent = %s
#         ORDER BY idx
#     """, (stock_entry_name,), as_dict=True)
    
#     return stock_entry_details



# @frappe.whitelist()
# def calculate_process_loss(docname, purchase_orders):
#     if isinstance(purchase_orders, str):
#         purchase_orders = json.loads(purchase_orders)

#     print("\n\nOriginal purchase_orders:\n", purchase_orders)
    
#     # Extract only purchase_order values from non-empty rows
#     purchase_order_list = [
#         row.get("purchase_order") for row in purchase_orders
#         if row.get("purchase_order") not in [None, ""]
#     ]
    
#     print("\n\nFiltered purchase orders:\n", purchase_order_list)
    
#     # Get the supplied items data
#     all_supplied_items = get_subcontracting_order_details(purchase_order_list)
#     print("\n\nall_supplied_items\n\n", all_supplied_items)
    
#     # Update the Process Loss document with the sent_details
#     update_sent_details(docname, all_supplied_items)
    
#     return all_supplied_items

# def update_sent_details(docname, sent_details_data):
#     """Update the sent_details table in the Process Loss document"""
#     try:
#         # Get the Process Loss document
#         process_loss_doc = frappe.get_doc("Process Loss", docname)
        
#         # Clear existing sent_details
#         process_loss_doc.set("sent_details", [])
        
#         # Add new sent_details rows
#         for item in sent_details_data:
#             process_loss_doc.append("sent_details", {
#                 "purchase_order": item.get("purchase_order"),
#                 "subcontracting_order": item.get("subcontracting_order"),
#                 "item_code": item.get("item_code"),
#                 "po_item_code": item.get("main_item_code", ""),  # Added main_item_code
#                 "po_qty": item.get("po_qty", 0),
#                 "sent_qty": item.get("sent_qty", 0),
#                 "stock_entry": item.get("stock_entry"),
#                 "uom": item.get("uom", "")
#             })
        
#         # Save the document
#         process_loss_doc.save()
#         frappe.db.commit()
        
#         print(f"\n\nSuccessfully updated sent_details for {docname}")
#         return True
        
#     except Exception as e:
#         frappe.log_error(f"Error updating sent_details for {docname}: {str(e)}")
#         frappe.throw(f"Failed to update sent details: {str(e)}")
#         return False

# @frappe.whitelist()
# def get_subcontracting_order_details(purchase_order_list):
#     print("\n\nget_subcontracting_order_details\n\n", purchase_order_list)
    
#     if not purchase_order_list:
#         return []
    
#     # Convert to tuple for SQL query
#     po_tuple = tuple(purchase_order_list)
#     print("\npo_tuple\n", po_tuple)
    
#     # Get all Subcontracting Orders linked to these Purchase Orders
#     sco_list = frappe.db.sql("""
#         SELECT name, purchase_order, supplier_warehouse
#         FROM `tabSubcontracting Order`
#         WHERE purchase_order IN %s AND docstatus = 1
#     """, (po_tuple,), as_dict=True)
    
#     print("\n\nSubcontracting Orders found:\n", sco_list)
    
#     if not sco_list:
#         return []
    
#     # Get SCO names
#     sco_names = [sco['name'] for sco in sco_list]
#     sco_tuple = tuple(sco_names)
    
#     # Get Subcontracting Order Supplied Items (raw materials)
#     sco_supplied_items = frappe.db.sql("""
#         SELECT 
#             parent as subcontracting_order,
#             rm_item_code as item_code,
#             main_item_code,
#             required_qty as po_qty
#         FROM `tabSubcontracting Order Supplied Item`
#         WHERE parent IN %s
#     """, (sco_tuple,), as_dict=True)
    
#     print("\n\nSubcontracting Order Supplied Items found:\n", sco_supplied_items)
    
#     # Get UOM for each item from Item master
#     item_codes = list(set([item['item_code'] for item in sco_supplied_items if item['item_code']]))
#     item_uom_map = {}
    
#     if item_codes:
#         item_tuple = tuple(item_codes)
#         item_data = frappe.db.sql("""
#             SELECT item_code, stock_uom
#             FROM `tabItem`
#             WHERE item_code IN %s
#         """, (item_tuple,), as_dict=True)
        
#         item_uom_map = {item['item_code']: item['stock_uom'] for item in item_data}
    
#     print("\n\nItem UOM Map:\n", item_uom_map)
    
#     # Get all Stock Entries linked to these Subcontracting Orders
#     stock_entries_data = get_stock_entries_for_sco(sco_names)
    
#     # Combine data for sent_details
#     sent_details = []
    
#     for sco in sco_list:
#         # Find supplied items for this SCO
#         sco_items_filtered = [item for item in sco_supplied_items if item['subcontracting_order'] == sco['name']]
        
#         # Find matching stock entries for this SCO
#         matching_entries = [
#             entry for entry in stock_entries_data 
#             if entry['subcontracting_order'] == sco['name']
#         ]
        
#         for sco_item in sco_items_filtered:
#             uom = item_uom_map.get(sco_item['item_code'], '')
            
#             for entry in matching_entries:
#                 # Find matching items in the stock entry
#                 for stock_item in entry.get('items', []):
#                     if stock_item.get('item_code') == sco_item['item_code']:
#                         sent_details.append({
#                             'purchase_order': sco['purchase_order'],
#                             'subcontracting_order': sco['name'],
#                             'item_code': sco_item['item_code'],
#                             'main_item_code': sco_item.get('main_item_code', ''),  # Added main_item_code
#                             'po_qty': sco_item['po_qty'],
#                             'sent_qty': stock_item.get('qty', 0),
#                             'stock_entry': entry['name'],
#                             'uom': uom
#                         })
    
#     print("\n\nFinal sent_details:\n", sent_details)
#     return sent_details

# def get_stock_entries_for_sco(sco_names):
#     if not sco_names:
#         return []
    
#     # Convert to tuple for SQL query
#     sco_tuple = tuple(sco_names)
#     print("\nsco_tuple for stock entries\n", sco_tuple)
    
#     # Get all Stock Entries linked to these Subcontracting Orders with purpose "Send to Subcontractor"
#     stock_entry_list = frappe.db.sql("""
#         SELECT name, subcontracting_order, purpose, posting_date
#         FROM `tabStock Entry`
#         WHERE subcontracting_order IN %s AND docstatus = 1 AND purpose = 'Send to Subcontractor'
#         ORDER BY posting_date
#     """, (sco_tuple,), as_dict=True)
    
#     print("\n\nStock Entries found:\n", stock_entry_list)
    
#     # Fetch stock entry details for each stock entry
#     for stock_entry in stock_entry_list:
#         stock_entry['items'] = get_stock_entry_details(stock_entry['name'])
    
#     return stock_entry_list

# def get_stock_entry_details(stock_entry_name):
#     """Fetch all items from Stock Entry Detail table for a given Stock Entry"""
#     stock_entry_details = frappe.db.sql("""
#         SELECT 
#             item_code, qty, uom, 
#             s_warehouse, t_warehouse, po_detail
#         FROM `tabStock Entry Detail`
#         WHERE parent = %s
#         ORDER BY idx
#     """, (stock_entry_name,), as_dict=True)
    
#     return stock_entry_details





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
    
    # Get the supplied items data
    all_supplied_items = get_subcontracting_order_details(purchase_order_list)
    print("\n\nall_supplied_items\n\n", all_supplied_items)
    
    # Update the Process Loss document with the sent_details
    update_sent_details(docname, all_supplied_items)
    
    # Get the returned items data for return_details table
    all_returned_items = get_returned_items_details(purchase_order_list)
    print("\n\nall_returned_items\n\n", all_returned_items)
    
    # Update the Process Loss document with the return_details
    update_return_details(docname, all_returned_items)
    
    return {
        'sent_details': all_supplied_items,
        'return_details': all_returned_items
    }

def update_sent_details(docname, sent_details_data):
    """Update the sent_details table in the Process Loss document"""
    try:
        # Get the Process Loss document
        process_loss_doc = frappe.get_doc("Process Loss", docname)
        
        # Clear existing sent_details
        process_loss_doc.set("sent_details", [])
        
        # Add new sent_details rows
        for item in sent_details_data:
            process_loss_doc.append("sent_details", {
                "purchase_order": item.get("purchase_order"),
                "subcontracting_order": item.get("subcontracting_order"),
                "item_code": item.get("item_code"),
                "po_item_code": item.get("main_item_code", ""),
                "po_qty": item.get("po_qty", 0),
                "sent_qty": item.get("sent_qty", 0),
                "stock_entry": item.get("stock_entry"),
                "uom": item.get("uom", "")
            })
        
        # Save the document
        process_loss_doc.save()
        frappe.db.commit()
        
        print(f"\n\nSuccessfully updated sent_details for {docname}")
        return True
        
    except Exception as e:
        frappe.log_error(f"Error updating sent_details for {docname}: {str(e)}")
        frappe.throw(f"Failed to update sent details: {str(e)}")
        return False

def update_return_details(docname, return_details_data):
    """Update the return_details table in the Process Loss document"""
    try:
        # Get the Process Loss document
        process_loss_doc = frappe.get_doc("Process Loss", docname)
        
        # Clear existing return_details
        process_loss_doc.set("return_details", [])
        
        # Add new return_details rows
        for item in return_details_data:
            process_loss_doc.append("return_details", {
                "purchase_order": item.get("purchase_order"),
                "subcontracting_order": item.get("subcontracting_order"),
                "item_code": item.get("item_code"),
                "po_item_code": item.get("main_item_code", ""),
                "return_qty": item.get("return_qty", 0),
                "stock_entry": item.get("stock_entry"),
                "uom": item.get("uom", "")
            })
        
        # Save the document
        process_loss_doc.save()
        frappe.db.commit()
        
        print(f"\n\nSuccessfully updated return_details for {docname}")
        return True
        
    except Exception as e:
        frappe.log_error(f"Error updating return_details for {docname}: {str(e)}")
        frappe.throw(f"Failed to update return details: {str(e)}")
        return False

@frappe.whitelist()
def get_subcontracting_order_details(purchase_order_list):
    print("\n\nget_subcontracting_order_details\n\n", purchase_order_list)
    
    if not purchase_order_list:
        return []
    
    # Convert to tuple for SQL query
    po_tuple = tuple(purchase_order_list)
    print("\npo_tuple\n", po_tuple)
    
    # Get all Subcontracting Orders linked to these Purchase Orders
    sco_list = frappe.db.sql("""
        SELECT name, purchase_order, supplier_warehouse
        FROM `tabSubcontracting Order`
        WHERE purchase_order IN %s AND docstatus = 1
    """, (po_tuple,), as_dict=True)
    
    print("\n\nSubcontracting Orders found:\n", sco_list)
    
    if not sco_list:
        return []
    
    # Get SCO names
    sco_names = [sco['name'] for sco in sco_list]
    sco_tuple = tuple(sco_names)
    
    # Get Subcontracting Order Supplied Items (raw materials)
    sco_supplied_items = frappe.db.sql("""
        SELECT 
            parent as subcontracting_order,
            rm_item_code as item_code,
            main_item_code,
            required_qty as po_qty
        FROM `tabSubcontracting Order Supplied Item`
        WHERE parent IN %s
    """, (sco_tuple,), as_dict=True)
    
    print("\n\nSubcontracting Order Supplied Items found:\n", sco_supplied_items)
    
    # Get UOM for each item from Item master
    item_codes = list(set([item['item_code'] for item in sco_supplied_items if item['item_code']]))
    item_uom_map = {}
    
    if item_codes:
        item_tuple = tuple(item_codes)
        item_data = frappe.db.sql("""
            SELECT item_code, stock_uom
            FROM `tabItem`
            WHERE item_code IN %s
        """, (item_tuple,), as_dict=True)
        
        item_uom_map = {item['item_code']: item['stock_uom'] for item in item_data}
    
    print("\n\nItem UOM Map:\n", item_uom_map)
    
    # Get all Stock Entries linked to these Subcontracting Orders for sent items
    stock_entries_data = get_stock_entries_for_sco(sco_names, 'Send to Subcontractor')
    
    # Combine data for sent_details
    sent_details = []
    
    for sco in sco_list:
        # Find supplied items for this SCO
        sco_items_filtered = [item for item in sco_supplied_items if item['subcontracting_order'] == sco['name']]
        
        # Find matching stock entries for this SCO
        matching_entries = [
            entry for entry in stock_entries_data 
            if entry['subcontracting_order'] == sco['name']
        ]
        
        for sco_item in sco_items_filtered:
            uom = item_uom_map.get(sco_item['item_code'], '')
            
            for entry in matching_entries:
                # Find matching items in the stock entry
                for stock_item in entry.get('items', []):
                    if stock_item.get('item_code') == sco_item['item_code']:
                        sent_details.append({
                            'purchase_order': sco['purchase_order'],
                            'subcontracting_order': sco['name'],
                            'item_code': sco_item['item_code'],
                            'main_item_code': sco_item.get('main_item_code', ''),
                            'po_qty': sco_item['po_qty'],
                            'sent_qty': stock_item.get('qty', 0),
                            'stock_entry': entry['name'],
                            'uom': uom
                        })
    
    print("\n\nFinal sent_details:\n", sent_details)
    return sent_details

def get_returned_items_details(purchase_order_list):
    """Get returned items data for return_details table"""
    if not purchase_order_list:
        return []
    
    # Convert to tuple for SQL query
    po_tuple = tuple(purchase_order_list)
    print("\npo_tuple for returned items\n", po_tuple)
    
    # Get all Subcontracting Orders linked to these Purchase Orders with supplier_warehouse
    sco_list = frappe.db.sql("""
        SELECT name, purchase_order, supplier_warehouse
        FROM `tabSubcontracting Order`
        WHERE purchase_order IN %s AND docstatus = 1
    """, (po_tuple,), as_dict=True)
    
    print("\n\nSubcontracting Orders for returned items:\n", sco_list)
    
    if not sco_list:
        return []
    
    # Get SCO names
    sco_names = [sco['name'] for sco in sco_list]
    sco_tuple = tuple(sco_names)
    
    # Get supplier warehouses
    supplier_warehouses = [sco['supplier_warehouse'] for sco in sco_list if sco.get('supplier_warehouse')]
    
    if not supplier_warehouses:
        return []
    
    # Get all Stock Entries linked to these Subcontracting Orders with purpose "Material Transfer"
    # and where s_warehouse is the supplier_warehouse
    stock_entries_data = get_return_stock_entries_for_sco(sco_names, supplier_warehouses)
    
    # Get Subcontracting Order Supplied Items for main_item_code mapping
    sco_supplied_items = frappe.db.sql("""
        SELECT 
            parent as subcontracting_order,
            rm_item_code as item_code,
            main_item_code
        FROM `tabSubcontracting Order Supplied Item`
        WHERE parent IN %s
    """, (sco_tuple,), as_dict=True)
    
    # Create mapping for main_item_code
    item_main_item_map = {}
    for item in sco_supplied_items:
        key = (item['subcontracting_order'], item['item_code'])
        item_main_item_map[key] = item.get('main_item_code', '')
    
    # Get UOM for each item from Item master
    item_codes = list(set([item['item_code'] for item in sco_supplied_items if item['item_code']]))
    item_uom_map = {}
    
    if item_codes:
        item_tuple = tuple(item_codes)
        item_data = frappe.db.sql("""
            SELECT item_code, stock_uom
            FROM `tabItem`
            WHERE item_code IN %s
        """, (item_tuple,), as_dict=True)
        
        item_uom_map = {item['item_code']: item['stock_uom'] for item in item_data}
    
    # Combine data for return_details
    return_details = []
    
    for sco in sco_list:
        # Find matching stock entries for this SCO
        matching_entries = [
            entry for entry in stock_entries_data 
            if entry['subcontracting_order'] == sco['name']
        ]
        
        for entry in matching_entries:
            for stock_item in entry.get('items', []):
                # Get main_item_code from mapping
                key = (sco['name'], stock_item.get('item_code'))
                main_item_code = item_main_item_map.get(key, '')
                
                uom = item_uom_map.get(stock_item.get('item_code'), '')
                
                return_details.append({
                    'purchase_order': sco['purchase_order'],
                    'subcontracting_order': sco['name'],
                    'item_code': stock_item.get('item_code'),
                    'main_item_code': main_item_code,
                    'return_qty': stock_item.get('qty', 0),
                    'stock_entry': entry['name'],
                    'uom': uom
                })
    
    print("\n\nFinal return_details:\n", return_details)
    return return_details

def get_stock_entries_for_sco(sco_names, purpose):
    """Get stock entries for specific purpose"""
    if not sco_names:
        return []
    
    # Convert to tuple for SQL query
    sco_tuple = tuple(sco_names)
    print(f"\nsco_tuple for stock entries ({purpose}):\n", sco_tuple)
    
    # Get all Stock Entries linked to these Subcontracting Orders with specific purpose
    stock_entry_list = frappe.db.sql(f"""
        SELECT name, subcontracting_order, purpose, posting_date
        FROM `tabStock Entry`
        WHERE subcontracting_order IN %s AND docstatus = 1 AND purpose = %s
        ORDER BY posting_date
    """, (sco_tuple, purpose), as_dict=True)
    
    print(f"\n\nStock Entries found ({purpose}):\n", stock_entry_list)
    
    # Fetch stock entry details for each stock entry
    for stock_entry in stock_entry_list:
        stock_entry['items'] = get_stock_entry_details(stock_entry['name'])
    
    return stock_entry_list

def get_return_stock_entries_for_sco(sco_names, supplier_warehouses):
    """Get return stock entries where s_warehouse is supplier_warehouse"""
    if not sco_names or not supplier_warehouses:
        return []
    
    # Convert to tuples for SQL query
    sco_tuple = tuple(sco_names)
    warehouse_tuple = tuple(supplier_warehouses)
    
    print(f"\nsco_tuple for return stock entries:\n", sco_tuple)
    print(f"warehouse_tuple for return stock entries:\n", warehouse_tuple)
    
    # Get all Stock Entries linked to these Subcontracting Orders with purpose "Material Transfer"
    # and where items have s_warehouse matching supplier_warehouse
    stock_entry_list = frappe.db.sql("""
        SELECT DISTINCT se.name, se.subcontracting_order, se.purpose, se.posting_date
        FROM `tabStock Entry` se
        INNER JOIN `tabStock Entry Detail` sed ON se.name = sed.parent
        WHERE se.subcontracting_order IN %s 
        AND se.docstatus = 1 
        AND se.purpose = 'Material Transfer'
        AND sed.s_warehouse IN %s
        ORDER BY se.posting_date
    """, (sco_tuple, warehouse_tuple), as_dict=True)
    
    print(f"\n\nReturn Stock Entries found:\n", stock_entry_list)
    
    # Fetch stock entry details for each stock entry
    for stock_entry in stock_entry_list:
        stock_entry['items'] = get_stock_entry_details(stock_entry['name'])
    
    return stock_entry_list

def get_stock_entry_details(stock_entry_name):
    """Fetch all items from Stock Entry Detail table for a given Stock Entry"""
    stock_entry_details = frappe.db.sql("""
        SELECT 
            item_code, qty, uom, 
            s_warehouse, t_warehouse, po_detail
        FROM `tabStock Entry Detail`
        WHERE parent = %s
        ORDER BY idx
    """, (stock_entry_name,), as_dict=True)
    
    return stock_entry_details