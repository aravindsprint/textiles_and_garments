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
    
#     # Get the returned items data for return_details table
#     all_returned_items = get_returned_items_details(purchase_order_list)
#     print("\n\nall_returned_items\n\n", all_returned_items)
    
#     # Update the Process Loss document with the return_details
#     update_return_details(docname, all_returned_items)
    
#     return {
#         'sent_details': all_supplied_items,
#         'return_details': all_returned_items
#     }


# @frappe.whitelist()
# def calculate_summary(docname):
#     print("\n\ncalculate_summary\n\n")
    
#     try:
#         # Get the Process Loss document
#         process_loss_doc = frappe.get_doc("Process Loss", docname)
        
#         # Get data from all three tables
#         sent_details = process_loss_doc.get("sent_details", [])
#         return_details = process_loss_doc.get("return_details", [])
#         received_details = process_loss_doc.get("received_details", [])
        
#         print(f"\nSent Details: {len(sent_details)} items")
#         print(f"Return Details: {len(return_details)} items")
#         print(f"Received Details: {len(received_details)} items")
        
#         # Create a dictionary to aggregate data by (purchase_order, subcontracting_order, item_code)
#         summary_data = {}
        
#         # Process sent_details
#         for sent_item in sent_details:
#             key = (
#                 sent_item.get("purchase_order"),
#                 sent_item.get("subcontracting_order"),
#                 sent_item.get("item_code"),
#                 sent_item.get("uom")
#             )
            
#             if key not in summary_data:
#                 summary_data[key] = {
#                     "purchase_order": sent_item.get("purchase_order"),
#                     "subcontracting_order": sent_item.get("subcontracting_order"),
#                     "item_code": sent_item.get("item_code"),
#                     "uom": sent_item.get("uom"),
#                     "po_qty": 0,
#                     "sent_qty": 0,
#                     "return_qty": 0,
#                     "received_qty": 0
#                 }
            
#             summary_data[key]["sent_qty"] += flt(sent_item.get("sent_qty", 0))
#             summary_data[key]["po_qty"] = flt(sent_item.get("po_qty", 0))  # Use the PO qty from sent items
        
#         # Process return_details
#         for return_item in return_details:
#             key = (
#                 return_item.get("purchase_order"),
#                 return_item.get("subcontracting_order"),
#                 return_item.get("item_code"),
#                 return_item.get("uom")
#             )
            
#             if key not in summary_data:
#                 summary_data[key] = {
#                     "purchase_order": return_item.get("purchase_order"),
#                     "subcontracting_order": return_item.get("subcontracting_order"),
#                     "item_code": return_item.get("item_code"),
#                     "uom": return_item.get("uom"),
#                     "po_qty": 0,
#                     "sent_qty": 0,
#                     "return_qty": 0,
#                     "received_qty": 0
#                 }
            
#             summary_data[key]["return_qty"] += flt(return_item.get("return_qty", 0))
        
#         # Process received_details
#         for received_item in received_details:
#             key = (
#                 received_item.get("purchase_order"),
#                 received_item.get("subcontracting_order"),
#                 received_item.get("item_code"),
#                 received_item.get("uom")
#             )
            
#             if key not in summary_data:
#                 summary_data[key] = {
#                     "purchase_order": received_item.get("purchase_order"),
#                     "subcontracting_order": received_item.get("subcontracting_order"),
#                     "item_code": received_item.get("item_code"),
#                     "uom": received_item.get("uom"),
#                     "po_qty": 0,
#                     "sent_qty": 0,
#                     "return_qty": 0,
#                     "received_qty": 0
#                 }
            
#             summary_data[key]["received_qty"] += flt(received_item.get("received_qty", 0))
#             # Update PO qty from received items if not already set
#             if summary_data[key]["po_qty"] == 0:
#                 summary_data[key]["po_qty"] = flt(received_item.get("po_qty", 0))
        
#         # Calculate process loss quantities and percentages
#         process_loss_details = []
#         for key, data in summary_data.items():
#             # Calculate process loss quantity
#             process_loss_qty = flt(data["sent_qty"]) - flt(data["return_qty"]) - flt(data["received_qty"])
            
#             # Calculate process loss percentage (avoid division by zero)
#             process_loss_percentage = 0
#             if data["sent_qty"] > 0:
#                 process_loss_percentage = (process_loss_qty / data["sent_qty"]) * 100
            
#             process_loss_details.append({
#                 "purchase_order": data["purchase_order"],
#                 "subcontracting_order": data["subcontracting_order"],
#                 "item_code": data["item_code"],
#                 "uom": data["uom"],
#                 "po_qty": flt(data["po_qty"]),
#                 "sent_qty": flt(data["sent_qty"]),
#                 "return_qty": flt(data["return_qty"]),
#                 "received_qty": flt(data["received_qty"]),
#                 "process_loss_qty": process_loss_qty,
#                 "process_loss_percentage": process_loss_percentage
#             })
        
#         print(f"\nProcess Loss Details: {len(process_loss_details)} items")
#         print(f"Process Loss Details: {process_loss_details}")
        
#         # Update the Process Loss document with the process_loss_details
#         process_loss_doc.set("process_loss_details", [])
        
#         for item in process_loss_details:
#             process_loss_doc.append("process_loss_details", {
#                 "purchase_order": item.get("purchase_order"),
#                 "subcontracting_order": item.get("subcontracting_order"),
#                 "item_code": item.get("item_code"),
#                 "uom": item.get("uom"),
#                 "po_qty": item.get("po_qty", 0),
#                 "sent_qty": item.get("sent_qty", 0),
#                 "return_qty": item.get("return_qty", 0),
#                 "received_qty": item.get("received_qty", 0),
#                 "process_loss_qty": item.get("process_loss_qty", 0),
#                 "process_loss_percentage": item.get("process_loss_percentage", 0)
#             })
        
#         # Save the document
#         process_loss_doc.save()
#         frappe.db.commit()
        
#         print(f"\n\nSuccessfully updated process_loss_details for {docname}")
#         return process_loss_details
        
#     except Exception as e:
#         frappe.log_error(f"Error calculating summary for {docname}: {str(e)}")
#         frappe.throw(f"Failed to calculate summary: {str(e)}")
#         return []


# @frappe.whitelist()
# def calculate_summary(docname):
#     print("\n\ncalculate_summary\n\n")
    
#     try:
#         # Get the Process Loss document
#         process_loss_doc = frappe.get_doc("Process Loss", docname)
        
#         # Get data from all three tables
#         sent_details = process_loss_doc.get("sent_details", [])
#         return_details = process_loss_doc.get("return_details", [])
#         received_details = process_loss_doc.get("received_details", [])
        
#         print(f"\nSent Details: {len(sent_details)} items")
#         print(f"Return Details: {len(return_details)} items")
#         print(f"Received Details: {len(received_details)} items")

#         print(f"\nSent Details: {sent_details} items")
#         print(f"Return Details: {return_details} items")
#         print(f"Received Details: {received_details} items")
        
#         # Create a dictionary to aggregate data by (purchase_order, subcontracting_order, item_code, uom)
#         summary_data = {}
        
#         # Process sent_details - use po_item_code and map to item_code for aggregation
#         for sent_item in sent_details:
#             # Use po_item_code as the main item code for aggregation
#             main_item_code = sent_item.get("po_item_code")
#             key = (
#                 sent_item.get("purchase_order"),
#                 sent_item.get("subcontracting_order"),
#                 main_item_code,  # Use po_item_code as the main identifier
#                 sent_item.get("uom")
#             )
            
#             if key not in summary_data:
#                 summary_data[key] = {
#                     "purchase_order": sent_item.get("purchase_order"),
#                     "subcontracting_order": sent_item.get("subcontracting_order"),
#                     "item_code": main_item_code,  # Store the main item code
#                     "uom": sent_item.get("uom"),
#                     "po_qty": 0,
#                     "sent_qty": 0,
#                     "return_qty": 0,
#                     "received_qty": 0
#                 }
            
#             summary_data[key]["sent_qty"] += flt(sent_item.get("sent_qty", 0))
#             summary_data[key]["po_qty"] = flt(sent_item.get("po_qty", 0))  # Use the PO qty from sent items
        
#         # Process return_details - use po_item_code and map to item_code for aggregation
#         for return_item in return_details:
#             # Use po_item_code as the main item code for aggregation
#             main_item_code = return_item.get("po_item_code") or return_item.get("item_code")
#             key = (
#                 return_item.get("purchase_order"),
#                 return_item.get("subcontracting_order"),
#                 main_item_code,  # Use po_item_code as the main identifier
#                 return_item.get("uom")
#             )
            
#             if key not in summary_data:
#                 summary_data[key] = {
#                     "purchase_order": return_item.get("purchase_order"),
#                     "subcontracting_order": return_item.get("subcontracting_order"),
#                     "item_code": main_item_code,  # Store the main item code
#                     "uom": return_item.get("uom"),
#                     "po_qty": 0,
#                     "sent_qty": 0,
#                     "return_qty": 0,
#                     "received_qty": 0
#                 }
            
#             summary_data[key]["return_qty"] += flt(return_item.get("return_qty", 0))
        
#         # Process received_details - use item_code directly
#         for received_item in received_details:
#             # For received items, use item_code directly
#             main_item_code = received_item.get("item_code", "")
#             key = (
#                 received_item.get("purchase_order"),
#                 received_item.get("subcontracting_order"),
#                 main_item_code,  # Use item_code directly
#                 received_item.get("uom")
#             )
            
#             if key not in summary_data:
#                 summary_data[key] = {
#                     "purchase_order": received_item.get("purchase_order"),
#                     "subcontracting_order": received_item.get("subcontracting_order"),
#                     "item_code": main_item_code,  # Store the item code
#                     "uom": received_item.get("uom"),
#                     "po_qty": 0,
#                     "sent_qty": 0,
#                     "return_qty": 0,
#                     "received_qty": 0
#                 }
            
#             summary_data[key]["received_qty"] += flt(received_item.get("received_qty", 0))
#             # Update PO qty from received items if not already set
#             if summary_data[key]["po_qty"] == 0:
#                 summary_data[key]["po_qty"] = flt(received_item.get("po_qty", 0))
        
#         # Calculate process loss quantities and percentages
#         process_loss_details = []
#         for key, data in summary_data.items():
#             # Calculate process loss quantity
#             process_loss_qty = flt(data["sent_qty"]) - flt(data["return_qty"]) - flt(data["received_qty"])
            
#             # Calculate process loss percentage (avoid division by zero)
#             process_loss_percentage = 0
#             if data["sent_qty"] > 0:
#                 process_loss_percentage = (process_loss_qty / data["sent_qty"]) * 100
            
#             process_loss_details.append({
#                 "purchase_order": data["purchase_order"],
#                 "subcontracting_order": data["subcontracting_order"],
#                 "item_code": data["item_code"],
#                 "uom": data["uom"],
#                 "po_qty": flt(data["po_qty"]),
#                 "sent_qty": flt(data["sent_qty"]),
#                 "return_qty": flt(data["return_qty"]),
#                 "received_qty": flt(data["received_qty"]),
#                 "process_loss_qty": process_loss_qty,
#                 "process_loss_percentage": process_loss_percentage
#             })
        
#         print(f"\nProcess Loss Details: {len(process_loss_details)} items")
#         print(f"Process Loss Details: {process_loss_details}")
        
#         # Update the Process Loss document with the process_loss_details
#         process_loss_doc.set("process_loss_details", [])
        
#         for item in process_loss_details:
#             process_loss_doc.append("process_loss_details", {
#                 "purchase_order": item.get("purchase_order"),
#                 "subcontracting_order": item.get("subcontracting_order"),
#                 "item_code": item.get("item_code"),
#                 "uom": item.get("uom"),
#                 "po_qty": item.get("po_qty", 0),
#                 "sent_qty": item.get("sent_qty", 0),
#                 "return_qty": item.get("return_qty", 0),
#                 "received_qty": item.get("received_qty", 0),
#                 "process_loss_qty": item.get("process_loss_qty", 0),
#                 "process_loss_percentage": item.get("process_loss_percentage", 0)
#             })
        
#         # Save the document
#         process_loss_doc.save()
#         frappe.db.commit()
        
#         print(f"\n\nSuccessfully updated process_loss_details for {docname}")
#         return process_loss_details
        
#     except Exception as e:
#         frappe.log_error(f"Error calculating summary for {docname}: {str(e)}")
#         frappe.throw(f"Failed to calculate summary: {str(e)}")
#         return []


# @frappe.whitelist()
# def calculate_summary(docname):
#     print("\n\ncalculate_summary\n\n")
    
#     try:
#         # Get the Process Loss document
#         process_loss_doc = frappe.get_doc("Process Loss", docname)
        
#         # Get data from all three tables
#         sent_details = process_loss_doc.get("sent_details", [])
#         return_details = process_loss_doc.get("return_details", [])
#         received_details = process_loss_doc.get("received_details", [])
        
#         print(f"\nSent Details: {len(sent_details)} items")
#         print(f"Return Details: {len(return_details)} items")
#         print(f"Received Details: {len(received_details)} items")
        
#         # Get average weights from the Process Loss document
#         collar_avg_weight = flt(process_loss_doc.get("collar_avg_weight", 0))
#         cuff_avg_weight = flt(process_loss_doc.get("cuff_avg_weight", 0))
        
#         print(f"\nCollar Avg Weight: {collar_avg_weight}")
#         print(f"Cuff Avg Weight: {cuff_avg_weight}")
        
#         # Create a dictionary to aggregate data by (purchase_order, subcontracting_order, item_code)
#         summary_data = {}
        
#         # Process sent_details - use po_item_code and map to item_code for aggregation
#         for sent_item in sent_details:
#             # Use po_item_code as the main item code for aggregation
#             main_item_code = sent_item.get("po_item_code")
#             key = (
#                 sent_item.get("purchase_order"),
#                 sent_item.get("subcontracting_order"),
#                 main_item_code  # Use po_item_code as the main identifier
#             )
            
#             if key not in summary_data:
#                 summary_data[key] = {
#                     "purchase_order": sent_item.get("purchase_order"),
#                     "subcontracting_order": sent_item.get("subcontracting_order"),
#                     "item_code": main_item_code,  # Store the main item code
#                     "uom": "",  # Will be determined later
#                     "po_qty": 0,
#                     "sent_qty": 0,
#                     "return_qty": 0,
#                     "received_qty": 0,
#                     "sent_uom": sent_item.get("uom"),  # Store original sent UOM
#                     "is_converted": False  # Track if sent_qty has been converted
#                 }
            
#             summary_data[key]["sent_qty"] += flt(sent_item.get("sent_qty", 0))
#             summary_data[key]["po_qty"] = flt(sent_item.get("po_qty", 0))  # Use the PO qty from sent items
        
#         # Process return_details - use po_item_code and map to item_code for aggregation
#         for return_item in return_details:
#             # Use po_item_code as the main item code for aggregation
#             main_item_code = return_item.get("po_item_code") or return_item.get("item_code")
#             key = (
#                 return_item.get("purchase_order"),
#                 return_item.get("subcontracting_order"),
#                 main_item_code  # Use po_item_code as the main identifier
#             )
            
#             if key not in summary_data:
#                 summary_data[key] = {
#                     "purchase_order": return_item.get("purchase_order"),
#                     "subcontracting_order": return_item.get("subcontracting_order"),
#                     "item_code": main_item_code,  # Store the main item code
#                     "uom": "",  # Will be determined later
#                     "po_qty": 0,
#                     "sent_qty": 0,
#                     "return_qty": 0,
#                     "received_qty": 0,
#                     "sent_uom": "",
#                     "is_converted": False
#                 }
            
#             summary_data[key]["return_qty"] += flt(return_item.get("return_qty", 0))
        
#         # Process received_details - use item_code directly
#         for received_item in received_details:
#             # For received items, use item_code directly
#             main_item_code = received_item.get("item_code", "")
#             key = (
#                 received_item.get("purchase_order"),
#                 received_item.get("subcontracting_order"),
#                 main_item_code  # Use item_code directly
#             )
            
#             if key not in summary_data:
#                 summary_data[key] = {
#                     "purchase_order": received_item.get("purchase_order"),
#                     "subcontracting_order": received_item.get("subcontracting_order"),
#                     "item_code": main_item_code,  # Store the item code
#                     "uom": received_item.get("uom"),  # Use received UOM
#                     "po_qty": 0,
#                     "sent_qty": 0,
#                     "return_qty": 0,
#                     "received_qty": 0,
#                     "sent_uom": "",
#                     "is_converted": False
#                 }
#             else:
#                 # Update UOM from received items
#                 summary_data[key]["uom"] = received_item.get("uom")
            
#             summary_data[key]["received_qty"] += flt(received_item.get("received_qty", 0))
#             # Update PO qty from received items if not already set
#             if summary_data[key]["po_qty"] == 0:
#                 summary_data[key]["po_qty"] = flt(received_item.get("po_qty", 0))
        
#         # Convert sent quantities if needed (Kgs to Pcs/Nos)
#         for key, data in summary_data.items():
#             if data["sent_uom"] in ["Kgs", "Kg"] and data["uom"] in ["Pcs", "Nos"]:
#                 # Get item type to determine which average weight to use
#                 item_code = data["item_code"]
#                 item_type = get_item_type(item_code)
                
#                 conversion_factor = 1
#                 if item_type == "collar" and collar_avg_weight > 0:
#                     conversion_factor = collar_avg_weight
#                     print(f"Using collar conversion factor: {conversion_factor} for {item_code}")
#                 elif item_type == "cuff" and cuff_avg_weight > 0:
#                     conversion_factor = cuff_avg_weight
#                     print(f"Using cuff conversion factor: {conversion_factor} for {item_code}")
#                 else:
#                     print(f"No conversion factor found for {item_code}, type: {item_type}")
                
#                 if conversion_factor > 0 and conversion_factor != 1:
#                     original_sent_qty = data["sent_qty"]
#                     data["sent_qty"] = data["sent_qty"] / conversion_factor
#                     data["is_converted"] = True
#                     print(f"Converted {original_sent_qty} {data['sent_uom']} to {data['sent_qty']} {data['uom']} for {item_code} (factor: {conversion_factor})")
        
#         # Calculate process loss quantities and percentages
#         process_loss_details = []
#         for key, data in summary_data.items():
#             # Calculate process loss quantity
#             process_loss_qty = flt(data["sent_qty"]) - flt(data["return_qty"]) - flt(data["received_qty"])
            
#             # Calculate process loss percentage (avoid division by zero)
#             process_loss_percentage = 0
#             if data["sent_qty"] > 0:
#                 process_loss_percentage = (process_loss_qty / data["sent_qty"]) * 100
            
#             process_loss_details.append({
#                 "purchase_order": data["purchase_order"],
#                 "subcontracting_order": data["subcontracting_order"],
#                 "item_code": data["item_code"],
#                 "uom": data["uom"],
#                 "po_qty": flt(data["po_qty"]),
#                 "sent_qty": flt(data["sent_qty"]),
#                 "return_qty": flt(data["return_qty"]),
#                 "received_qty": flt(data["received_qty"]),
#                 "process_loss_qty": process_loss_qty,
#                 "process_loss_percentage": process_loss_percentage
#             })
        
#         print(f"\nProcess Loss Details: {len(process_loss_details)} items")
#         print(f"Process Loss Details: {process_loss_details}")
        
#         # Update the Process Loss document with the process_loss_details
#         process_loss_doc.set("process_loss_details", [])
        
#         for item in process_loss_details:
#             process_loss_doc.append("process_loss_details", {
#                 "purchase_order": item.get("purchase_order"),
#                 "subcontracting_order": item.get("subcontracting_order"),
#                 "item_code": item.get("item_code"),
#                 "uom": item.get("uom"),
#                 "po_qty": item.get("po_qty", 0),
#                 "sent_qty": item.get("sent_qty", 0),
#                 "return_qty": item.get("return_qty", 0),
#                 "received_qty": item.get("received_qty", 0),
#                 "process_loss_qty": item.get("process_loss_qty", 0),
#                 "process_loss_percentage": item.get("process_loss_percentage", 0)
#             })
        
#         # Save the document
#         process_loss_doc.save()
#         frappe.db.commit()
        
#         print(f"\n\nSuccessfully updated process_loss_details for {docname}")
#         return process_loss_details
        
#     except Exception as e:
#         frappe.log_error(f"Error calculating summary for {docname}: {str(e)}")
#         frappe.throw(f"Failed to calculate summary: {str(e)}")
#         return []

# def get_item_type(item_code):
#     """Get item type from Item master"""
#     try:
#         item_doc = frappe.get_doc("Item", item_code)
#         return item_doc.get("textile_item_type", "").lower()
#     except:
#         return ""


# @frappe.whitelist()
# def calculate_summary(docname):
#     print("\n\ncalculate_summary\n\n")
    
#     try:
#         process_loss_doc = frappe.get_doc("Process Loss", docname)

#         sent_details = process_loss_doc.get("sent_details", [])
#         return_details = process_loss_doc.get("return_details", [])
#         received_details = process_loss_doc.get("received_details", [])

#         print(f"\nSent Details: {len(sent_details)} items")
#         print(f"Return Details: {len(return_details)} items")
#         print(f"Received Details: {len(received_details)} items")

#         collar_avg_weight = flt(process_loss_doc.get("collar_avg_weight", 0))
#         cuff_avg_weight = flt(process_loss_doc.get("cuff_avg_weight", 0))

#         print(f"\nCollar Avg Weight: {collar_avg_weight}")
#         print(f"Cuff Avg Weight: {cuff_avg_weight}")

#         summary_data = {}

#         # --------------------------
#         # Process Sent Details
#         # --------------------------
#         for sent_item in sent_details:
#             main_item_code = sent_item.get("po_item_code") or sent_item.get("main_item_code") or sent_item.get("item_code")
#             key = (
#                 sent_item.get("purchase_order"),
#                 sent_item.get("subcontracting_order"),
#                 main_item_code
#             )

#             if key not in summary_data:
#                 summary_data[key] = {
#                     "purchase_order": sent_item.get("purchase_order"),
#                     "subcontracting_order": sent_item.get("subcontracting_order"),
#                     "item_code": main_item_code,
#                     "uom": "",  # will be filled from received
#                     "po_qty": flt(sent_item.get("po_qty", 0)),
#                     "sent_qty": 0,
#                     "return_qty": 0,
#                     "received_qty": 0,
#                     "sent_uom": sent_item.get("uom"),
#                     "is_converted": False
#                 }

#             summary_data[key]["sent_qty"] += flt(sent_item.get("sent_qty", 0))

#         # --------------------------
#         # Process Return Details
#         # --------------------------
#         for return_item in return_details:
#             main_item_code = return_item.get("po_item_code") or return_item.get("item_code")
#             key = (
#                 return_item.get("purchase_order"),
#                 return_item.get("subcontracting_order"),
#                 main_item_code
#             )

#             if key not in summary_data:
#                 summary_data[key] = {
#                     "purchase_order": return_item.get("purchase_order"),
#                     "subcontracting_order": return_item.get("subcontracting_order"),
#                     "item_code": main_item_code,
#                     "uom": "",
#                     "po_qty": 0,
#                     "sent_qty": 0,
#                     "return_qty": 0,
#                     "received_qty": 0,
#                     "sent_uom": "",
#                     "is_converted": False
#                 }

#             summary_data[key]["return_qty"] += flt(return_item.get("return_qty", 0))

#         # --------------------------
#         # Process Received Details
#         # --------------------------
#         for received_item in received_details:
#             main_item_code = received_item.get("item_code")
#             key = (
#                 received_item.get("purchase_order"),
#                 received_item.get("subcontracting_order"),
#                 main_item_code
#             )

#             if key not in summary_data:
#                 summary_data[key] = {
#                     "purchase_order": received_item.get("purchase_order"),
#                     "subcontracting_order": received_item.get("subcontracting_order"),
#                     "item_code": main_item_code,
#                     "uom": received_item.get("uom"),
#                     "po_qty": flt(received_item.get("po_qty", 0)),
#                     "sent_qty": 0,
#                     "return_qty": 0,
#                     "received_qty": 0,
#                     "sent_uom": "",
#                     "is_converted": False
#                 }
#             else:
#                 summary_data[key]["uom"] = received_item.get("uom")
#                 if summary_data[key]["po_qty"] == 0:
#                     summary_data[key]["po_qty"] = flt(received_item.get("po_qty", 0))

#             summary_data[key]["received_qty"] += flt(received_item.get("received_qty", 0))

#         # --------------------------
#         # Convert Sent Qty (if required)
#         # --------------------------
#         for key, data in summary_data.items():
#             if data["sent_uom"] in ["Kg", "Kgs"] and data["uom"] in ["Pcs", "Nos"]:
#                 item_code = data["item_code"]
#                 item_type = get_item_type(item_code)
#                 print("\n\nitem_code\n\n",item_code)
#                 print("\n\nitem_type\n\n",item_type)

#                 conversion_factor = 1
#                 if item_type == "Collar" and collar_avg_weight > 0:
#                     conversion_factor = collar_avg_weight
#                     print(f"Using collar conversion factor: {conversion_factor} for {item_code}")
#                 elif item_type == "Cuff" and cuff_avg_weight > 0:
#                     conversion_factor = cuff_avg_weight
#                     print(f"Using cuff conversion factor: {conversion_factor} for {item_code}")
#                 else:
#                     print(f"No conversion factor found for {item_code}, type: {item_type}")

#                 if conversion_factor > 0 and conversion_factor != 1:
#                     original_sent_qty = data["sent_qty"]
#                     data["sent_qty"] = original_sent_qty / conversion_factor
#                     data["is_converted"] = True
#                     print(f"Converted {original_sent_qty} {data['sent_uom']} to {data['sent_qty']} {data['uom']} for {item_code} (factor: {conversion_factor})")

#         # --------------------------
#         # Calculate Process Loss
#         # --------------------------
#         process_loss_details = []
#         for key, data in summary_data.items():
#             process_loss_qty = flt(data["sent_qty"]) - flt(data["return_qty"]) - flt(data["received_qty"])
#             process_loss_percentage = 0
#             if data["sent_qty"] > 0:
#                 process_loss_percentage = (process_loss_qty / data["sent_qty"]) * 100

#             process_loss_details.append({
#                 "purchase_order": data["purchase_order"],
#                 "subcontracting_order": data["subcontracting_order"],
#                 "item_code": data["item_code"],
#                 "uom": data["uom"],
#                 "po_qty": data["po_qty"],
#                 "sent_qty": data["sent_qty"],
#                 "return_qty": data["return_qty"],
#                 "received_qty": data["received_qty"],
#                 "process_loss_qty": process_loss_qty,
#                 "process_loss_percentage": process_loss_percentage
#             })

#         print(f"\nProcess Loss Details: {len(process_loss_details)} items")
#         print(f"Process Loss Details: {process_loss_details}")

#         # --------------------------
#         # Update Process Loss Doc
#         # --------------------------
#         process_loss_doc.set("process_loss_details", [])

#         for item in process_loss_details:
#             process_loss_doc.append("process_loss_details", {
#                 "purchase_order": item.get("purchase_order"),
#                 "subcontracting_order": item.get("subcontracting_order"),
#                 "item_code": item.get("item_code"),
#                 "uom": item.get("uom"),
#                 "po_qty": item.get("po_qty"),
#                 "sent_qty": item.get("sent_qty"),
#                 "return_qty": item.get("return_qty"),
#                 "received_qty": item.get("received_qty"),
#                 "process_loss_qty": item.get("process_loss_qty"),
#                 "process_loss_percentage": item.get("process_loss_percentage")
#             })

#         process_loss_doc.save()
#         frappe.db.commit()

#         print(f"\n\nSuccessfully updated process_loss_details for {docname}")
#         return process_loss_details

#     except Exception as e:
#         frappe.log_error(f"Error calculating summary for {docname}: {str(e)}")
#         frappe.throw(f"Failed to calculate summary: {str(e)}")
#         return []

# # --------------------------
# # Helper Function
# # --------------------------
# def get_item_type(item_code):
#     try:
#         item_doc = frappe.get_doc("Item", item_code)
#         return item_doc.get("custom_item_type", "")
#     except:
#         return ""

# @frappe.whitelist()
# def calculate_summary(docname):
#     print("\n\ncalculate_summary\n\n")

#     try:
#         process_loss_doc = frappe.get_doc("Process Loss", docname)

#         sent_details = process_loss_doc.get("sent_details", [])
#         return_details = process_loss_doc.get("return_details", [])
#         received_details = process_loss_doc.get("received_details", [])

#         print(f"\nSent Details: {len(sent_details)} items")
#         print(f"Return Details: {len(return_details)} items")
#         print(f"Received Details: {len(received_details)} items")

#         collar_avg_weight = flt(process_loss_doc.get("collar_avg_weight", 0))
#         cuff_avg_weight = flt(process_loss_doc.get("cuff_avg_weight", 0))

#         print(f"\nCollar Avg Weight: {collar_avg_weight}")
#         print(f"Cuff Avg Weight: {cuff_avg_weight}")

#         summary_data = {}

#         # --------------------------
#         # Process Sent Details
#         # --------------------------
#         for sent_item in sent_details:
#             main_item_code = sent_item.get("po_item_code") or sent_item.get("main_item_code") or sent_item.get("item_code")
#             key = (
#                 sent_item.get("purchase_order"),
#                 sent_item.get("subcontracting_order"),
#                 main_item_code
#             )

#             if key not in summary_data:
#                 summary_data[key] = {
#                     "purchase_order": sent_item.get("purchase_order"),
#                     "subcontracting_order": sent_item.get("subcontracting_order"),
#                     "item_code": main_item_code,
#                     "uom": "",  # will be filled from received
#                     "po_qty": 0,  # will be set from received_details later
#                     "sent_qty": 0,
#                     "return_qty": 0,
#                     "received_qty": 0,
#                     "sent_uom": sent_item.get("uom"),
#                     "is_converted": False
#                 }

#             summary_data[key]["sent_qty"] += flt(sent_item.get("sent_qty", 0))

#         # --------------------------
#         # Process Return Details
#         # --------------------------
#         for return_item in return_details:
#             main_item_code = return_item.get("po_item_code") or return_item.get("item_code")
#             key = (
#                 return_item.get("purchase_order"),
#                 return_item.get("subcontracting_order"),
#                 main_item_code
#             )

#             if key not in summary_data:
#                 summary_data[key] = {
#                     "purchase_order": return_item.get("purchase_order"),
#                     "subcontracting_order": return_item.get("subcontracting_order"),
#                     "item_code": main_item_code,
#                     "uom": "",
#                     "po_qty": 0,
#                     "sent_qty": 0,
#                     "return_qty": 0,
#                     "received_qty": 0,
#                     "sent_uom": "",
#                     "is_converted": False
#                 }

#             summary_data[key]["return_qty"] += flt(return_item.get("return_qty", 0))

#         # --------------------------
#         # Process Received Details
#         # --------------------------
#         for received_item in received_details:
#             main_item_code = received_item.get("item_code")
#             key = (
#                 received_item.get("purchase_order"),
#                 received_item.get("subcontracting_order"),
#                 main_item_code
#             )

#             if key not in summary_data:
#                 summary_data[key] = {
#                     "purchase_order": received_item.get("purchase_order"),
#                     "subcontracting_order": received_item.get("subcontracting_order"),
#                     "item_code": main_item_code,
#                     "uom": received_item.get("uom"),
#                     "po_qty": flt(received_item.get("po_qty", 0)),  # ✅ Always set from received_details
#                     "sent_qty": 0,
#                     "return_qty": 0,
#                     "received_qty": 0,
#                     "sent_uom": "",
#                     "is_converted": False
#                 }
#             else:
#                 summary_data[key]["uom"] = received_item.get("uom")
#                 summary_data[key]["po_qty"] = flt(received_item.get("po_qty", 0))  # ✅ Always override

#             summary_data[key]["received_qty"] += flt(received_item.get("received_qty", 0))

#         # --------------------------
#         # Convert Sent Qty (if required)
#         # --------------------------
#         for key, data in summary_data.items():
#             if data["sent_uom"] in ["Kg", "Kgs"] and data["uom"] in ["Pcs", "Nos"]:
#                 item_code = data["item_code"]
#                 item_type = get_item_type(item_code)
#                 print("\n\nitem_code\n\n", item_code)
#                 print("\n\nitem_type\n\n", item_type)

#                 conversion_factor = 1
#                 if item_type == "Collar" and collar_avg_weight > 0:
#                     conversion_factor = collar_avg_weight
#                     print(f"Using collar conversion factor: {conversion_factor} for {item_code}")
#                 elif item_type == "Cuff" and cuff_avg_weight > 0:
#                     conversion_factor = cuff_avg_weight
#                     print(f"Using cuff conversion factor: {conversion_factor} for {item_code}")
#                 else:
#                     print(f"No conversion factor found for {item_code}, type: {item_type}")

#                 if conversion_factor > 0 and conversion_factor != 1:
#                     original_sent_qty = data["sent_qty"]
#                     data["sent_qty"] = original_sent_qty / conversion_factor
#                     data["is_converted"] = True
#                     print(f"Converted {original_sent_qty} {data['sent_uom']} to {data['sent_qty']} {data['uom']} for {item_code} (factor: {conversion_factor})")

#         # --------------------------
#         # Calculate Process Loss
#         # --------------------------
#         process_loss_details = []
#         for key, data in summary_data.items():
#             process_loss_qty = flt(data["sent_qty"]) - flt(data["return_qty"]) - flt(data["received_qty"])
#             process_loss_percentage = 0
#             if data["sent_qty"] > 0:
#                 process_loss_percentage = (process_loss_qty / data["sent_qty"]) * 100

#             process_loss_details.append({
#                 "purchase_order": data["purchase_order"],
#                 "subcontracting_order": data["subcontracting_order"],
#                 "item_code": data["item_code"],
#                 "uom": data["uom"],
#                 "po_qty": data["po_qty"],
#                 "sent_qty": data["sent_qty"],
#                 "return_qty": data["return_qty"],
#                 "received_qty": data["received_qty"],
#                 "process_loss_qty": process_loss_qty,
#                 "process_loss_percentage": process_loss_percentage
#             })

#         print(f"\nProcess Loss Details: {len(process_loss_details)} items")
#         print(f"Process Loss Details: {process_loss_details}")

#         # --------------------------
#         # Update Process Loss Doc
#         # --------------------------
#         process_loss_doc.set("process_loss_details", [])

#         for item in process_loss_details:
#             process_loss_doc.append("process_loss_details", {
#                 "purchase_order": item.get("purchase_order"),
#                 "subcontracting_order": item.get("subcontracting_order"),
#                 "item_code": item.get("item_code"),
#                 "uom": item.get("uom"),
#                 "po_qty": item.get("po_qty"),
#                 "sent_qty": item.get("sent_qty"),
#                 "return_qty": item.get("return_qty"),
#                 "received_qty": item.get("received_qty"),
#                 "process_loss_qty": item.get("process_loss_qty"),
#                 "process_loss_percentage": item.get("process_loss_percentage")
#             })

#         process_loss_doc.save()
#         frappe.db.commit()

#         print(f"\n\nSuccessfully updated process_loss_details for {docname}")
#         return process_loss_details

#     except Exception as e:
#         frappe.log_error(f"Error calculating summary for {docname}: {str(e)}")
#         frappe.throw(f"Failed to calculate summary: {str(e)}")
#         return []

# # --------------------------
# # Helper Function
# # --------------------------
# def get_item_type(item_code):
#     try:
#         item_doc = frappe.get_doc("Item", item_code)
#         return item_doc.get("custom_item_type", "")
#     except:
#         return ""


@frappe.whitelist()
def calculate_summary(docname):
    print("\n\ncalculate_summary\n\n")

    try:
        process_loss_doc = frappe.get_doc("Process Loss", docname)

        sent_details = process_loss_doc.get("sent_details", [])
        return_details = process_loss_doc.get("return_details", [])
        received_details = process_loss_doc.get("received_details", [])

        print(f"\nSent Details: {len(sent_details)} items")
        print(f"Return Details: {len(return_details)} items")
        print(f"Received Details: {len(received_details)} items")

        collar_avg_weight = flt(process_loss_doc.get("collar_avg_weight", 0))
        cuff_avg_weight = flt(process_loss_doc.get("cuff_avg_weight", 0))

        print(f"\nCollar Avg Weight: {collar_avg_weight}")
        print(f"Cuff Avg Weight: {cuff_avg_weight}")

        summary_data = {}

        # --------------------------
        # Process Sent Details
        # --------------------------
        for sent_item in sent_details:
            # main_item_code = sent_item.get("po_item_code") or sent_item.get("main_item_code") or sent_item.get("item_code")
            main_item_code = sent_item.get("item_code")
            print("\n\nmain_item_code\n\n",main_item_code)
            po_item_code = sent_item.get("po_item_code")
            
            # Skip DYES% and CHEM% items for sent_qty calculation
            if main_item_code and (main_item_code.startswith("DYES") or main_item_code.startswith("CHEM")):
                print(f"Skipping sent item: {main_item_code} (DYES/CHEM item)")
                continue
                
            key = (
                sent_item.get("purchase_order"),
                sent_item.get("subcontracting_order"),
                po_item_code
            )

            if key not in summary_data:
                summary_data[key] = {
                    "purchase_order": sent_item.get("purchase_order"),
                    "subcontracting_order": sent_item.get("subcontracting_order"),
                    "item_code": po_item_code,
                    "uom": "",  # will be filled from received
                    "po_qty": 0,  # will be set from received_details later
                    "sent_qty": 0,
                    "return_qty": 0,
                    "received_qty": 0,
                    "sent_uom": sent_item.get("uom"),
                    "is_converted": False
                }

            summary_data[key]["sent_qty"] += flt(sent_item.get("sent_qty", 0))

        # --------------------------
        # Process Return Details
        # --------------------------
        for return_item in return_details:
            # main_item_code = return_item.get("po_item_code") or return_item.get("item_code")
            main_item_code = return_item.get("item_code")
            po_item_code = sent_item.get("po_item_code")
            
            # Skip DYES% and CHEM% items for return_qty calculation
            if main_item_code and (main_item_code.startswith("DYES") or main_item_code.startswith("CHEM")):
                print(f"Skipping return item: {main_item_code} (DYES/CHEM item)")
                continue
                
            key = (
                return_item.get("purchase_order"),
                return_item.get("subcontracting_order"),
                po_item_code
            )

            if key not in summary_data:
                summary_data[key] = {
                    "purchase_order": return_item.get("purchase_order"),
                    "subcontracting_order": return_item.get("subcontracting_order"),
                    "item_code": po_item_code,
                    "uom": "",
                    "po_qty": 0,
                    "sent_qty": 0,
                    "return_qty": 0,
                    "received_qty": 0,
                    "sent_uom": "",
                    "is_converted": False
                }

            summary_data[key]["return_qty"] += flt(return_item.get("return_qty", 0))

        # --------------------------
        # Process Received Details
        # --------------------------
        for received_item in received_details:
            main_item_code = received_item.get("item_code")
            print("\n\nmain_item_code\n\n",main_item_code)
            key = (
                received_item.get("purchase_order"),
                received_item.get("subcontracting_order"),
                main_item_code
            )

            if key not in summary_data:
                summary_data[key] = {
                    "purchase_order": received_item.get("purchase_order"),
                    "subcontracting_order": received_item.get("subcontracting_order"),
                    "item_code": main_item_code,
                    "uom": received_item.get("uom"),
                    "po_qty": flt(received_item.get("po_qty", 0)),  # ✅ Always set from received_details
                    "sent_qty": 0,
                    "return_qty": 0,
                    "received_qty": 0,
                    "sent_uom": "",
                    "is_converted": False
                }
            else:
                summary_data[key]["uom"] = received_item.get("uom")
                summary_data[key]["po_qty"] = flt(received_item.get("po_qty", 0))  # ✅ Always override

            summary_data[key]["received_qty"] += flt(received_item.get("received_qty", 0))

        # --------------------------
        # Convert Sent Qty (if required)
        # --------------------------
        for key, data in summary_data.items():
            print("\n\ndata01\n\n", data)
            if data["sent_uom"] in ["Kg", "Kgs"] and data["uom"] in ["Pcs", "Nos"]:
                item_code = data["item_code"]
                item_type = get_item_type(item_code)
                print("\n\nitem_code\n\n", item_code)
                print("\n\nitem_type\n\n", item_type)

                conversion_factor = 1
                if item_type == "Collar" and collar_avg_weight > 0:
                    conversion_factor = collar_avg_weight
                    print(f"Using collar conversion factor: {conversion_factor} for {item_code}")
                elif item_type == "Cuff" and cuff_avg_weight > 0:
                    conversion_factor = cuff_avg_weight
                    print(f"Using cuff conversion factor: {conversion_factor} for {item_code}")
                else:
                    print(f"No conversion factor found for {item_code}, type: {item_type}")

                if conversion_factor > 0 and conversion_factor != 1:
                    original_sent_qty = data["sent_qty"]
                    data["sent_qty"] = original_sent_qty / conversion_factor
                    data["is_converted"] = True
                    print(f"Converted {original_sent_qty} {data['sent_uom']} to {data['sent_qty']} {data['uom']} for {item_code} (factor: {conversion_factor})")

        # --------------------------
        # Calculate Process Loss
        # --------------------------
        process_loss_details = []
        for key, data in summary_data.items():
            print("\n\ndata\n\n",data)
            process_loss_qty = flt(data["sent_qty"]) - flt(data["return_qty"]) - flt(data["received_qty"])
            process_loss_percentage = 0
            if data["sent_qty"] > 0:
                process_loss_percentage = (process_loss_qty / data["sent_qty"]) * 100

            process_loss_details.append({
                "purchase_order": data["purchase_order"],
                "subcontracting_order": data["subcontracting_order"],
                "item_code": data["item_code"],
                "uom": data["uom"],
                "po_qty": data["po_qty"],
                "sent_qty": data["sent_qty"],
                "return_qty": data["return_qty"],
                "received_qty": data["received_qty"],
                "process_loss_qty": process_loss_qty,
                "process_loss_percentage": process_loss_percentage
            })

        print(f"\nProcess Loss Details: {len(process_loss_details)} items")
        print(f"Process Loss Details: {process_loss_details}")

        # --------------------------
        # Update Process Loss Doc
        # --------------------------
        process_loss_doc.set("process_loss_details", [])

        for item in process_loss_details:
            process_loss_doc.append("process_loss_details", {
                "purchase_order": item.get("purchase_order"),
                "subcontracting_order": item.get("subcontracting_order"),
                "item_code": item.get("item_code"),
                "uom": item.get("uom"),
                "po_qty": item.get("po_qty"),
                "sent_qty": item.get("sent_qty"),
                "return_qty": item.get("return_qty"),
                "received_qty": item.get("received_qty"),
                "process_loss_qty": item.get("process_loss_qty"),
                "process_loss_percentage": item.get("process_loss_percentage")
            })

        process_loss_doc.save()
        frappe.db.commit()

        print(f"\n\nSuccessfully updated process_loss_details for {docname}")
        return process_loss_details

    except Exception as e:
        frappe.log_error(f"Error calculating summary for {docname}: {str(e)}")
        frappe.throw(f"Failed to calculate summary: {str(e)}")
        return []

# --------------------------
# Helper Function
# --------------------------
def get_item_type(item_code):
    try:
        item_doc = frappe.get_doc("Item", item_code)
        return item_doc.get("custom_item_type", "")
    except:
        return ""
        


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
    
    # Get the received items data for received_details table
    all_received_items = get_received_items_details(purchase_order_list)
    print("\n\nall_received_items\n\n", all_received_items)
    
    # Update the Process Loss document with the received_details
    update_received_details(docname, all_received_items)
    
    return {
        'sent_details': all_supplied_items,
        'return_details': all_returned_items,
        'received_details': all_received_items
    }

def update_received_details(docname, received_details_data):
    """Update the received_details table in the Process Loss document"""
    try:
        # Get the Process Loss document
        process_loss_doc = frappe.get_doc("Process Loss", docname)
        
        # Clear existing received_details
        process_loss_doc.set("received_details", [])
        
        # Add new received_details rows
        for item in received_details_data:
            process_loss_doc.append("received_details", {
                "purchase_order": item.get("purchase_order"),
                "subcontracting_order": item.get("subcontracting_order"),
                "item_code": item.get("item_code"),
                "po_qty": item.get("po_qty", 0),
                "po_rate": item.get("po_rate", 0),
                "received_qty": item.get("received_qty", 0),
                "subcontracting_receipt": item.get("subcontracting_receipt"),
                "purchase_receipt": item.get("purchase_receipt"),
                "bill_rate": item.get("pi_rate"),
                "bill_no": item.get("bill_no"),
                "diff_rate": item.get("diff_rate"),
                "purchase_invoice": item.get("purchase_invoice"),
                "uom": item.get("uom", "")
            })
        
        # Save the document
        process_loss_doc.save()
        frappe.db.commit()
        
        print(f"\n\nSuccessfully updated received_details for {docname}")
        return True
        
    except Exception as e:
        frappe.log_error(f"Error updating received_details for {docname}: {str(e)}")
        frappe.throw(f"Failed to update received details: {str(e)}")
        return False



# def get_received_items_details(purchase_order_list):
#     """Get received items data from Subcontracting Receipt Item table"""
#     if not purchase_order_list:
#         return []
    
#     # Convert to tuple for SQL query
#     po_tuple = tuple(purchase_order_list)
#     print("\npo_tuple for received items\n", po_tuple)
    
#     # Get all Subcontracting Orders linked to these Purchase Orders
#     sco_list = frappe.db.sql("""
#         SELECT name, purchase_order
#         FROM `tabSubcontracting Order`
#         WHERE purchase_order IN %s AND docstatus = 1
#     """, (po_tuple,), as_dict=True)
    
#     print("\n\nSubcontracting Orders for received items:\n", sco_list)
    
#     if not sco_list:
#         return []
    
#     # Get SCO names
#     sco_names = [sco['name'] for sco in sco_list]
#     sco_tuple = tuple(sco_names)
    
#     # Get all Subcontracting Receipt Items directly filtered by subcontracting_order
#     receipt_items = frappe.db.sql("""
#         SELECT 
#             sri.parent as subcontracting_receipt,
#             sri.name as subcontracting_receipt_item,
#             sri.item_code,
#             sri.qty as received_qty,
#             sri.rate as po_rate,
#             sri.stock_uom,
#             sri.subcontracting_order,
#             sr.posting_date
#         FROM `tabSubcontracting Receipt Item` sri
#         INNER JOIN `tabSubcontracting Receipt` sr ON sri.parent = sr.name
#         WHERE sri.subcontracting_order IN %s AND sr.docstatus = 1
#         ORDER BY sr.posting_date
#     """, (sco_tuple,), as_dict=True)
    
#     print("\n\nSubcontracting Receipt Items found:\n", receipt_items)
    
#     if not receipt_items:
#         return []
    
#     # Get Subcontracting Order Items for po_qty mapping
#     sco_order_items = frappe.db.sql("""
#         SELECT 
#             parent as subcontracting_order,
#             item_code,
#             qty as po_qty
#         FROM `tabSubcontracting Order Item`
#         WHERE parent IN %s
#     """, (sco_tuple,), as_dict=True)
    
#     print("\n\nSubcontracting Order Items found:\n", sco_order_items)
    
#     # Create mapping for po_qty by (subcontracting_order, item_code)
#     po_qty_map = {}
#     for item in sco_order_items:
#         key = (item['subcontracting_order'], item['item_code'])
#         po_qty_map[key] = item.get('po_qty', 0)
    
#     # Get UOM for each item from Item master (as fallback)
#     item_codes = list(set([item['item_code'] for item in receipt_items if item['item_code']]))
#     item_uom_map = {}
    
#     if item_codes:
#         item_tuple = tuple(item_codes)
#         item_data = frappe.db.sql("""
#             SELECT item_code, stock_uom
#             FROM `tabItem`
#             WHERE item_code IN %s
#         """, (item_tuple,), as_dict=True)
        
#         item_uom_map = {item['item_code']: item['stock_uom'] for item in item_data}
    
#     # Create mapping from SCO name to purchase order
#     sco_po_map = {sco['name']: sco['purchase_order'] for sco in sco_list}
    
#     # Get all Purchase Receipts linked to these Subcontracting Receipts
#     subcontracting_receipts = list(set([item['subcontracting_receipt'] for item in receipt_items]))
#     pr_receipt_map = {}
#     pr_items_map = {}
    
#     if subcontracting_receipts:
#         pr_tuple = tuple(subcontracting_receipts)
#         # Get Purchase Receipts
#         purchase_receipts = frappe.db.sql("""
#             SELECT name, subcontracting_receipt
#             FROM `tabPurchase Receipt`
#             WHERE subcontracting_receipt IN %s AND docstatus = 1
#         """, (pr_tuple,), as_dict=True)
        
#         pr_receipt_map = {pr['subcontracting_receipt']: pr['name'] for pr in purchase_receipts}
        
#         # Get Purchase Receipt Items with subcontracting_receipt_item reference
#         purchase_receipt_names = list(pr_receipt_map.values())
#         if purchase_receipt_names:
#             pr_name_tuple = tuple(purchase_receipt_names)
#             purchase_receipt_items = frappe.db.sql("""
#                 SELECT 
#                     parent as purchase_receipt,
#                     name as purchase_receipt_item,
#                     subcontracting_receipt_item,
#                     item_code,
#                     qty,
#                     rate,
#                     amount
#                 FROM `tabPurchase Receipt Item`
#                 WHERE parent IN %s
#             """, (pr_name_tuple,), as_dict=True)
            
#             for pri in purchase_receipt_items:
#                 if pri['purchase_receipt'] not in pr_items_map:
#                     pr_items_map[pri['purchase_receipt']] = {}
#                 pr_items_map[pri['purchase_receipt']][pri['subcontracting_receipt_item']] = pri
    
#     print("\n\nPurchase Receipts found:\n", pr_receipt_map)
#     print("\n\nPurchase Receipt Items found:\n", pr_items_map)
    
#     # Get all Purchase Invoices linked to these Purchase Receipts
#     purchase_receipt_names = list(pr_receipt_map.values())
#     pi_receipt_map = {}
#     pi_bill_map = {}
#     pi_items_map = {}
    
#     if purchase_receipt_names:
#         pr_tuple = tuple(purchase_receipt_names)
#         # Get Purchase Invoices linked to Purchase Receipts
#         purchase_invoices = frappe.db.sql("""
#             SELECT pi.name, pi.bill_no, pii.purchase_receipt, pii.pr_detail
#             FROM `tabPurchase Invoice` pi
#             INNER JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
#             WHERE pii.purchase_receipt IN %s AND pi.docstatus != 2
#         """, (pr_tuple,), as_dict=True)
        
#         for pi in purchase_invoices:
#             pi_receipt_map[pi['purchase_receipt']] = pi['name']
#             pi_bill_map[pi['name']] = pi.get('bill_no', '')
        
#         # Get Purchase Invoice Items for additional details
#         purchase_invoice_names = list(set([pi['name'] for pi in purchase_invoices]))
#         if purchase_invoice_names:
#             pi_tuple = tuple(purchase_invoice_names)
#             purchase_invoice_items = frappe.db.sql("""
#                 SELECT 
#                     parent as purchase_invoice,
#                     pr_detail,
#                     item_code,
#                     qty,
#                     rate,
#                     amount
#                 FROM `tabPurchase Invoice Item`
#                 WHERE parent IN %s
#             """, (pi_tuple,), as_dict=True)
            
#             for pii in purchase_invoice_items:
#                 if pii['purchase_invoice'] not in pi_items_map:
#                     pi_items_map[pii['purchase_invoice']] = {}
#                 # Use pr_detail as the key directly (it contains the Purchase Receipt Item name)
#                 pi_items_map[pii['purchase_invoice']][pii['pr_detail']] = pii
    
#     print("\n\nPurchase Invoices found:\n", pi_receipt_map)
#     print("\n\nPurchase Invoice Bill Numbers:\n", pi_bill_map)
#     print("\n\nPurchase Invoice Items found:\n", pi_items_map)
    
#     # Combine data for received_details
#     received_details = []
    
#     for item in receipt_items:
#         # Use UOM from receipt item, fallback to item master
#         uom = item.get('stock_uom') or item_uom_map.get(item['item_code'], '')
        
#         # Get purchase order from mapping
#         purchase_order = sco_po_map.get(item['subcontracting_order'], '')
        
#         # Get po_qty from mapping
#         key = (item['subcontracting_order'], item['item_code'])
#         po_qty = po_qty_map.get(key, 0)
        
#         # Get linked Purchase Receipt
#         purchase_receipt = pr_receipt_map.get(item['subcontracting_receipt'], '')
        
#         # Get Purchase Receipt Item details using subcontracting_receipt_item
#         pr_item_details = {}
#         if purchase_receipt in pr_items_map:
#             pr_item_details = pr_items_map[purchase_receipt].get(item['subcontracting_receipt_item'], {})
        
#         # Get the Purchase Receipt Item name (this will be used as pr_detail)
#         purchase_receipt_item_name = pr_item_details.get('purchase_receipt_item', '')
        
#         # Get linked Purchase Invoice and Bill No
#         purchase_invoice = pi_receipt_map.get(purchase_receipt, '')
#         bill_no = pi_bill_map.get(purchase_invoice, '')
        
#         # Get Purchase Invoice Item details using purchase_receipt_item_name as pr_detail
#         pi_item_details = {}
#         if purchase_invoice in pi_items_map and purchase_receipt_item_name:
#             pi_item_details = pi_items_map[purchase_invoice].get(purchase_receipt_item_name, {})
        
#         received_details.append({
#             'purchase_order': purchase_order,
#             'subcontracting_order': item['subcontracting_order'],
#             'item_code': item['item_code'],
#             'po_rate': item['po_rate'],
#             'po_qty': po_qty,
#             'received_qty': item['received_qty'],
#             'subcontracting_receipt': item['subcontracting_receipt'],
#             'subcontracting_receipt_item': item['subcontracting_receipt_item'],
#             'purchase_receipt': purchase_receipt,
#             'purchase_receipt_item': purchase_receipt_item_name,
#             'pr_detail': purchase_receipt_item_name,
#             'pr_qty': pr_item_details.get('qty', 0),
#             'pr_rate': pr_item_details.get('rate', 0),
#             'pr_amount': pr_item_details.get('amount', 0),
#             'purchase_invoice': purchase_invoice,
#             'bill_no': bill_no,
#             'pi_qty': pi_item_details.get('qty', 0),
#             'pi_rate': pi_item_details.get('rate', 0),
#             'pi_amount': pi_item_details.get('amount', 0),
#             'diff_rate': pi_item_details.get('rate', 0) - item.get('po_rate', 0),  # Calculate difference
#             'uom': uom
#         })
    
#     print("\n\nFinal received_details:\n", received_details)
#     return received_details

# def get_received_items_details(purchase_order_list):
#     """Get received items data from Subcontracting Receipt Item table"""
#     if not purchase_order_list:
#         return []
    
#     # Convert to tuple for SQL query
#     po_tuple = tuple(purchase_order_list)
#     print("\npo_tuple for received items\n", po_tuple)
    
#     # Get all Subcontracting Orders linked to these Purchase Orders
#     sco_list = frappe.db.sql("""
#         SELECT name, purchase_order, supplier_warehouse
#         FROM `tabSubcontracting Order`
#         WHERE purchase_order IN %s AND docstatus = 1
#     """, (po_tuple,), as_dict=True)
    
#     print("\n\nSubcontracting Orders for received items:\n", sco_list)
    
#     if not sco_list:
#         return []
    
#     # Get SCO names
#     sco_names = [sco['name'] for sco in sco_list]
#     sco_tuple = tuple(sco_names)
    
#     # Get all Subcontracting Receipt Items directly filtered by subcontracting_order
#     receipt_items = frappe.db.sql("""
#         SELECT 
#             sri.parent as subcontracting_receipt,
#             sri.name as subcontracting_receipt_item,
#             sri.item_code,
#             sri.qty as received_qty,
#             sri.stock_uom,
#             sri.subcontracting_order,
#             sr.posting_date
#         FROM `tabSubcontracting Receipt Item` sri
#         INNER JOIN `tabSubcontracting Receipt` sr ON sri.parent = sr.name
#         WHERE sri.subcontracting_order IN %s AND sr.docstatus = 1
#         ORDER BY sr.posting_date
#     """, (sco_tuple,), as_dict=True)
    
#     print("\n\nSubcontracting Receipt Items found:\n", receipt_items)
    
#     if not receipt_items:
#         return []
    
#     # Get Subcontracting Order Items for po_qty and purchase_order_item mapping
#     sco_order_items = frappe.db.sql("""
#         SELECT 
#             parent as subcontracting_order,
#             item_code,
#             qty as po_qty,
#             purchase_order_item
#         FROM `tabSubcontracting Order Item`
#         WHERE parent IN %s
#     """, (sco_tuple,), as_dict=True)
    
#     print("\n\nSubcontracting Order Items found:\n", sco_order_items)
    
#     # Create mapping for po_qty and purchase_order_item by (subcontracting_order, item_code)
#     po_qty_map = {}
#     purchase_order_item_map = {}
#     for item in sco_order_items:
#         key = (item['subcontracting_order'], item['item_code'])
#         po_qty_map[key] = item.get('po_qty', 0)
#         purchase_order_item_map[key] = item.get('purchase_order_item', '')
    
#     # Get PO Rate from Purchase Order Item table
#     purchase_order_items_list = list(set([item.get('purchase_order_item') for item in sco_order_items if item.get('purchase_order_item')]))
#     po_rate_map = {}
    
#     if purchase_order_items_list:
#         po_item_tuple = tuple(purchase_order_items_list)
#         purchase_order_items = frappe.db.sql("""
#             SELECT 
#                 name,
#                 rate as po_rate
#             FROM `tabPurchase Order Item`
#             WHERE name IN %s
#         """, (po_item_tuple,), as_dict=True)
        
#         po_rate_map = {item['name']: item.get('po_rate', 0) for item in purchase_order_items}
    
#     print("\n\nPurchase Order Items Rate Map:\n", po_rate_map)
    
#     # Get UOM for each item from Item master (as fallback)
#     item_codes = list(set([item['item_code'] for item in receipt_items if item['item_code']]))
#     item_uom_map = {}
    
#     if item_codes:
#         item_tuple = tuple(item_codes)
#         item_data = frappe.db.sql("""
#             SELECT item_code, stock_uom
#             FROM `tabItem`
#             WHERE item_code IN %s
#         """, (item_tuple,), as_dict=True)
        
#         item_uom_map = {item['item_code']: item['stock_uom'] for item in item_data}
    
#     # Create mapping from SCO name to purchase order
#     sco_po_map = {sco['name']: sco['purchase_order'] for sco in sco_list}
    
#     # Get all Purchase Receipts linked to these Subcontracting Receipts
#     subcontracting_receipts = list(set([item['subcontracting_receipt'] for item in receipt_items]))
#     pr_receipt_map = {}
#     pr_items_map = {}
    
#     if subcontracting_receipts:
#         pr_tuple = tuple(subcontracting_receipts)
#         # Get Purchase Receipts
#         purchase_receipts = frappe.db.sql("""
#             SELECT name, subcontracting_receipt
#             FROM `tabPurchase Receipt`
#             WHERE subcontracting_receipt IN %s AND docstatus = 1
#         """, (pr_tuple,), as_dict=True)
        
#         pr_receipt_map = {pr['subcontracting_receipt']: pr['name'] for pr in purchase_receipts}
        
#         # Get Purchase Receipt Items with subcontracting_receipt_item reference
#         purchase_receipt_names = list(pr_receipt_map.values())
#         if purchase_receipt_names:
#             pr_name_tuple = tuple(purchase_receipt_names)
#             purchase_receipt_items = frappe.db.sql("""
#                 SELECT 
#                     parent as purchase_receipt,
#                     name as purchase_receipt_item,
#                     subcontracting_receipt_item,
#                     item_code,
#                     qty,
#                     rate,
#                     amount
#                 FROM `tabPurchase Receipt Item`
#                 WHERE parent IN %s
#             """, (pr_name_tuple,), as_dict=True)
            
#             for pri in purchase_receipt_items:
#                 if pri['purchase_receipt'] not in pr_items_map:
#                     pr_items_map[pri['purchase_receipt']] = {}
#                 pr_items_map[pri['purchase_receipt']][pri['subcontracting_receipt_item']] = pri
    
#     print("\n\nPurchase Receipts found:\n", pr_receipt_map)
#     print("\n\nPurchase Receipt Items found:\n", pr_items_map)
    
#     # Get all Purchase Invoices linked to these Purchase Receipts
#     purchase_receipt_names = list(pr_receipt_map.values())
#     pi_receipt_map = {}
#     pi_bill_map = {}
#     pi_items_map = {}
    
#     if purchase_receipt_names:
#         pr_tuple = tuple(purchase_receipt_names)
#         # Get Purchase Invoices linked to Purchase Receipts
#         purchase_invoices = frappe.db.sql("""
#             SELECT pi.name, pi.bill_no, pii.purchase_receipt, pii.pr_detail
#             FROM `tabPurchase Invoice` pi
#             INNER JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
#             WHERE pii.purchase_receipt IN %s AND pi.docstatus != 2
#         """, (pr_tuple,), as_dict=True)
        
#         for pi in purchase_invoices:
#             pi_receipt_map[pi['purchase_receipt']] = pi['name']
#             pi_bill_map[pi['name']] = pi.get('bill_no', '')
        
#         # Get Purchase Invoice Items for additional details
#         purchase_invoice_names = list(set([pi['name'] for pi in purchase_invoices]))
#         if purchase_invoice_names:
#             pi_tuple = tuple(purchase_invoice_names)
#             purchase_invoice_items = frappe.db.sql("""
#                 SELECT 
#                     parent as purchase_invoice,
#                     pr_detail,
#                     item_code,
#                     qty,
#                     rate,
#                     amount
#                 FROM `tabPurchase Invoice Item`
#                 WHERE parent IN %s
#             """, (pi_tuple,), as_dict=True)
            
#             for pii in purchase_invoice_items:
#                 if pii['purchase_invoice'] not in pi_items_map:
#                     pi_items_map[pii['purchase_invoice']] = {}
#                 # Use pr_detail as the key directly (it contains the Purchase Receipt Item name)
#                 pi_items_map[pii['purchase_invoice']][pii['pr_detail']] = pii
    
#     print("\n\nPurchase Invoices found:\n", pi_receipt_map)
#     print("\n\nPurchase Invoice Bill Numbers:\n", pi_bill_map)
#     print("\n\nPurchase Invoice Items found:\n", pi_items_map)
    
#     # Combine data for received_details
#     received_details = []
    
#     for item in receipt_items:
#         # Use UOM from receipt item, fallback to item master
#         uom = item.get('stock_uom') or item_uom_map.get(item['item_code'], '')
        
#         # Get purchase order from mapping
#         purchase_order = sco_po_map.get(item['subcontracting_order'], '')
        
#         # Get po_qty and purchase_order_item from mapping
#         key = (item['subcontracting_order'], item['item_code'])
#         po_qty = po_qty_map.get(key, 0)
#         purchase_order_item = purchase_order_item_map.get(key, '')
        
#         # Get po_rate from Purchase Order Item table
#         po_rate = po_rate_map.get(purchase_order_item, 0)
        
#         # Get linked Purchase Receipt
#         purchase_receipt = pr_receipt_map.get(item['subcontracting_receipt'], '')
        
#         # Get Purchase Receipt Item details using subcontracting_receipt_item
#         pr_item_details = {}
#         if purchase_receipt in pr_items_map:
#             pr_item_details = pr_items_map[purchase_receipt].get(item['subcontracting_receipt_item'], {})
        
#         # Get the Purchase Receipt Item name (this will be used as pr_detail)
#         purchase_receipt_item_name = pr_item_details.get('purchase_receipt_item', '')
        
#         # Get linked Purchase Invoice and Bill No
#         purchase_invoice = pi_receipt_map.get(purchase_receipt, '')
#         bill_no = pi_bill_map.get(purchase_invoice, '')
        
#         # Get Purchase Invoice Item details using purchase_receipt_item_name as pr_detail
#         pi_item_details = {}
#         if purchase_invoice in pi_items_map and purchase_receipt_item_name:
#             pi_item_details = pi_items_map[purchase_invoice].get(purchase_receipt_item_name, {})
        
#         received_details.append({
#             'purchase_order': purchase_order,
#             'subcontracting_order': item['subcontracting_order'],
#             'item_code': item['item_code'],
#             'po_rate': po_rate,  # Use PO Rate from Purchase Order Item
#             'po_qty': po_qty,
#             'received_qty': item['received_qty'],
#             'subcontracting_receipt': item['subcontracting_receipt'],
#             'subcontracting_receipt_item': item['subcontracting_receipt_item'],
#             'purchase_receipt': purchase_receipt,
#             'purchase_receipt_item': purchase_receipt_item_name,
#             'pr_detail': purchase_receipt_item_name,
#             'pr_qty': pr_item_details.get('qty', 0),
#             'pr_rate': pr_item_details.get('rate', 0),
#             'pr_amount': pr_item_details.get('amount', 0),
#             'purchase_invoice': purchase_invoice,
#             'bill_no': bill_no,
#             'pi_qty': pi_item_details.get('qty', 0),
#             'pi_rate': pi_item_details.get('rate', 0),
#             'pi_amount': pi_item_details.get('amount', 0),
#             'diff_rate': pi_item_details.get('rate', 0) - po_rate,  # Calculate difference using PO Rate
#             'uom': uom
#         })
    
#     print("\n\nFinal received_details:\n", received_details)
#     return received_details

# def get_received_items_details(purchase_order_list):
#     """Get received items data from Subcontracting Receipt Item table"""
#     if not purchase_order_list:
#         return []
    
#     # Convert to tuple for SQL query
#     po_tuple = tuple(purchase_order_list)
#     print("\npo_tuple for received items\n", po_tuple)
    
#     # Get all Subcontracting Orders linked to these Purchase Orders
#     sco_list = frappe.db.sql("""
#         SELECT name, purchase_order, supplier_warehouse
#         FROM `tabSubcontracting Order`
#         WHERE purchase_order IN %s AND docstatus = 1
#     """, (po_tuple,), as_dict=True)
    
#     print("\n\nSubcontracting Orders for received items:\n", sco_list)
    
#     if not sco_list:
#         return []
    
#     # Get SCO names
#     sco_names = [sco['name'] for sco in sco_list]
#     sco_tuple = tuple(sco_names)
    
#     # Get all Subcontracting Receipt Items directly filtered by subcontracting_order
#     receipt_items = frappe.db.sql("""
#         SELECT 
#             sri.parent as subcontracting_receipt,
#             sri.name as subcontracting_receipt_item,
#             sri.item_code,
#             sri.qty as received_qty,
#             sri.stock_uom,
#             sri.subcontracting_order,
#             sr.posting_date
#         FROM `tabSubcontracting Receipt Item` sri
#         INNER JOIN `tabSubcontracting Receipt` sr ON sri.parent = sr.name
#         WHERE sri.subcontracting_order IN %s AND sr.docstatus = 1
#         ORDER BY sr.posting_date
#     """, (sco_tuple,), as_dict=True)
    
#     print("\n\nSubcontracting Receipt Items found:\n", receipt_items)
    
#     if not receipt_items:
#         return []
    
#     # Get Subcontracting Order Items for po_qty and purchase_order_item mapping
#     sco_order_items = frappe.db.sql("""
#         SELECT 
#             parent as subcontracting_order,
#             item_code,
#             qty as po_qty,
#             purchase_order_item
#         FROM `tabSubcontracting Order Item`
#         WHERE parent IN %s
#     """, (sco_tuple,), as_dict=True)
    
#     print("\n\nSubcontracting Order Items found:\n", sco_order_items)
    
#     # Create mapping for po_qty and purchase_order_item by (subcontracting_order, item_code)
#     po_qty_map = {}
#     purchase_order_item_map = {}
#     for item in sco_order_items:
#         key = (item['subcontracting_order'], item['item_code'])
#         po_qty_map[key] = item.get('po_qty', 0)
#         purchase_order_item_map[key] = item.get('purchase_order_item', '')
    
#     # Get PO Rate from Purchase Order Item table
#     purchase_order_items_list = list(set([item.get('purchase_order_item') for item in sco_order_items if item.get('purchase_order_item')]))
#     po_rate_map = {}
    
#     if purchase_order_items_list:
#         po_item_tuple = tuple(purchase_order_items_list)
#         purchase_order_items = frappe.db.sql("""
#             SELECT 
#                 name,
#                 rate as po_rate
#             FROM `tabPurchase Order Item`
#             WHERE name IN %s
#         """, (po_item_tuple,), as_dict=True)
        
#         po_rate_map = {item['name']: item.get('po_rate', 0) for item in purchase_order_items}
    
#     print("\n\nPurchase Order Items Rate Map:\n", po_rate_map)
    
#     # Get UOM for each item from Item master (as fallback)
#     item_codes = list(set([item['item_code'] for item in receipt_items if item['item_code']]))
#     item_uom_map = {}
    
#     if item_codes:
#         item_tuple = tuple(item_codes)
#         item_data = frappe.db.sql("""
#             SELECT item_code, stock_uom
#             FROM `tabItem`
#             WHERE item_code IN %s
#         """, (item_tuple,), as_dict=True)
        
#         item_uom_map = {item['item_code']: item['stock_uom'] for item in item_data}
    
#     # Create mapping from SCO name to purchase order
#     sco_po_map = {sco['name']: sco['purchase_order'] for sco in sco_list}
    
#     # Get all Purchase Receipts linked to these Subcontracting Receipts
#     subcontracting_receipts = list(set([item['subcontracting_receipt'] for item in receipt_items]))
#     pr_receipt_map = {}
#     pr_items_map = {}
    
#     if subcontracting_receipts:
#         pr_tuple = tuple(subcontracting_receipts)
#         # Get Purchase Receipts
#         purchase_receipts = frappe.db.sql("""
#             SELECT name, subcontracting_receipt
#             FROM `tabPurchase Receipt`
#             WHERE subcontracting_receipt IN %s AND docstatus = 1
#         """, (pr_tuple,), as_dict=True)
        
#         pr_receipt_map = {pr['subcontracting_receipt']: pr['name'] for pr in purchase_receipts}
        
#         # Get Purchase Receipt Items with subcontracting_receipt_item reference
#         purchase_receipt_names = list(pr_receipt_map.values())
#         if purchase_receipt_names:
#             pr_name_tuple = tuple(purchase_receipt_names)
#             purchase_receipt_items = frappe.db.sql("""
#                 SELECT 
#                     parent as purchase_receipt,
#                     name as purchase_receipt_item,
#                     subcontracting_receipt_item,
#                     item_code,
#                     qty,
#                     rate,
#                     amount
#                 FROM `tabPurchase Receipt Item`
#                 WHERE parent IN %s
#             """, (pr_name_tuple,), as_dict=True)
            
#             for pri in purchase_receipt_items:
#                 if pri['purchase_receipt'] not in pr_items_map:
#                     pr_items_map[pri['purchase_receipt']] = {}
#                 pr_items_map[pri['purchase_receipt']][pri['subcontracting_receipt_item']] = pri
    
#     print("\n\nPurchase Receipts found:\n", pr_receipt_map)
#     print("\n\nPurchase Receipt Items found:\n", pr_items_map)
    
#     # Get all Purchase Invoices linked to these Purchase Receipts
#     purchase_receipt_names = list(pr_receipt_map.values())
#     pi_receipt_map = {}  # Changed to store list of PIs per PR
#     pi_bill_map = {}
#     pi_items_map = {}
    
#     if purchase_receipt_names:
#         pr_tuple = tuple(purchase_receipt_names)
#         # Get Purchase Invoices linked to Purchase Receipts
#         purchase_invoices = frappe.db.sql("""
#             SELECT pi.name, pi.bill_no, pii.purchase_receipt, pii.pr_detail
#             FROM `tabPurchase Invoice` pi
#             INNER JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
#             WHERE pii.purchase_receipt IN %s AND pi.docstatus != 2
#         """, (pr_tuple,), as_dict=True)
        
#         # Store multiple PIs per PR
#         for pi in purchase_invoices:
#             if pi['purchase_receipt'] not in pi_receipt_map:
#                 pi_receipt_map[pi['purchase_receipt']] = []
#             pi_receipt_map[pi['purchase_receipt']].append(pi['name'])
#             pi_bill_map[pi['name']] = pi.get('bill_no', '')
        
#         # Get Purchase Invoice Items for additional details
#         purchase_invoice_names = list(set([pi['name'] for pi in purchase_invoices]))
#         if purchase_invoice_names:
#             pi_tuple = tuple(purchase_invoice_names)
#             purchase_invoice_items = frappe.db.sql("""
#                 SELECT 
#                     parent as purchase_invoice,
#                     pr_detail,
#                     item_code,
#                     qty,
#                     rate,
#                     amount
#                 FROM `tabPurchase Invoice Item`
#                 WHERE parent IN %s
#             """, (pi_tuple,), as_dict=True)
            
#             for pii in purchase_invoice_items:
#                 if pii['purchase_invoice'] not in pi_items_map:
#                     pi_items_map[pii['purchase_invoice']] = {}
#                 # Use pr_detail as the key directly (it contains the Purchase Receipt Item name)
#                 pi_items_map[pii['purchase_invoice']][pii['pr_detail']] = pii
    
#     print("\n\nPurchase Invoices found:\n", pi_receipt_map)
#     print("\n\nPurchase Invoice Bill Numbers:\n", pi_bill_map)
#     print("\n\nPurchase Invoice Items found:\n", pi_items_map)
    
#     # Combine data for received_details
#     received_details = []
    
#     for item in receipt_items:
#         # Use UOM from receipt item, fallback to item master
#         uom = item.get('stock_uom') or item_uom_map.get(item['item_code'], '')
        
#         # Get purchase order from mapping
#         purchase_order = sco_po_map.get(item['subcontracting_order'], '')
        
#         # Get po_qty and purchase_order_item from mapping
#         key = (item['subcontracting_order'], item['item_code'])
#         po_qty = po_qty_map.get(key, 0)
#         purchase_order_item = purchase_order_item_map.get(key, '')
        
#         # Get po_rate from Purchase Order Item table
#         po_rate = po_rate_map.get(purchase_order_item, 0)
        
#         # Get linked Purchase Receipt
#         purchase_receipt = pr_receipt_map.get(item['subcontracting_receipt'], '')
        
#         # Get Purchase Receipt Item details using subcontracting_receipt_item
#         pr_item_details = {}
#         if purchase_receipt in pr_items_map:
#             pr_item_details = pr_items_map[purchase_receipt].get(item['subcontracting_receipt_item'], {})
        
#         # Get the Purchase Receipt Item name (this will be used as pr_detail)
#         purchase_receipt_item_name = pr_item_details.get('purchase_receipt_item', '')
        
#         # Get linked Purchase Invoices and Bill Nos (handle multiple PIs)
#         purchase_invoices = pi_receipt_map.get(purchase_receipt, [])
#         pi_details_list = []
        
#         # Collect all PI details for this PR item
#         for purchase_invoice in purchase_invoices:
#             bill_no = pi_bill_map.get(purchase_invoice, '')
            
#             # Get Purchase Invoice Item details using purchase_receipt_item_name as pr_detail
#             pi_item_details = {}
#             if purchase_invoice in pi_items_map and purchase_receipt_item_name:
#                 pi_item_details = pi_items_map[purchase_invoice].get(purchase_receipt_item_name, {})
            
#             if pi_item_details:  # Only add if there are actual details
#                 pi_details_list.append({
#                     'purchase_invoice': purchase_invoice,
#                     'bill_no': bill_no,
#                     'pi_qty': pi_item_details.get('qty', 0),
#                     'pi_rate': pi_item_details.get('rate', 0),
#                     'pi_amount': pi_item_details.get('amount', 0),
#                     'diff_rate': pi_item_details.get('rate', 0) - po_rate
#                 })
        
#         # If no PI details found, create empty entry
#         if not pi_details_list:
#             pi_details_list.append({
#                 'purchase_invoice': '',
#                 'bill_no': '',
#                 'pi_qty': 0,
#                 'pi_rate': 0,
#                 'pi_amount': 0,
#                 'diff_rate': 0
#             })
        
#         # Create one entry for each PI (or one entry if no PIs)
#         for pi_details in pi_details_list:
#             received_details.append({
#                 'purchase_order': purchase_order,
#                 'subcontracting_order': item['subcontracting_order'],
#                 'item_code': item['item_code'],
#                 'po_rate': po_rate,  # Use PO Rate from Purchase Order Item
#                 'po_qty': po_qty,
#                 'received_qty': item['received_qty'],
#                 'subcontracting_receipt': item['subcontracting_receipt'],
#                 'subcontracting_receipt_item': item['subcontracting_receipt_item'],
#                 'purchase_receipt': purchase_receipt,
#                 'purchase_receipt_item': purchase_receipt_item_name,
#                 'pr_detail': purchase_receipt_item_name,
#                 'pr_qty': pr_item_details.get('qty', 0),
#                 'pr_rate': pr_item_details.get('rate', 0),
#                 'pr_amount': pr_item_details.get('amount', 0),
#                 'purchase_invoice': pi_details['purchase_invoice'],
#                 'bill_no': pi_details['bill_no'],
#                 'pi_qty': pi_details['pi_qty'],
#                 'pi_rate': pi_details['pi_rate'],
#                 'pi_amount': pi_details['pi_amount'],
#                 'diff_rate': pi_details['diff_rate'],
#                 'uom': uom
#             })
    
#     print("\n\nFinal received_details:\n", received_details)
#     return received_details



def get_received_items_details(purchase_order_list):
    """Get received items data from Subcontracting Receipt Item table"""
    if not purchase_order_list:
        return []
    
    # Convert to tuple for SQL query
    po_tuple = tuple(purchase_order_list)
    print("\npo_tuple for received items\n", po_tuple)
    
    # Get all Subcontracting Orders linked to these Purchase Orders
    sco_list = frappe.db.sql("""
        SELECT name, purchase_order, supplier_warehouse
        FROM `tabSubcontracting Order`
        WHERE purchase_order IN %s AND docstatus = 1
    """, (po_tuple,), as_dict=True)
    
    print("\n\nSubcontracting Orders for received items:\n", sco_list)
    
    if not sco_list:
        return []
    
    # Get SCO names
    sco_names = [sco['name'] for sco in sco_list]
    sco_tuple = tuple(sco_names)
    
    # Get all Subcontracting Receipt Items directly filtered by subcontracting_order
    receipt_items = frappe.db.sql("""
        SELECT 
            sri.parent as subcontracting_receipt,
            sri.name as subcontracting_receipt_item,
            sri.item_code,
            sri.qty as received_qty,
            sri.stock_uom,
            sri.subcontracting_order,
            sr.posting_date
        FROM `tabSubcontracting Receipt Item` sri
        INNER JOIN `tabSubcontracting Receipt` sr ON sri.parent = sr.name
        WHERE sri.subcontracting_order IN %s AND sr.docstatus = 1
        ORDER BY sr.posting_date
    """, (sco_tuple,), as_dict=True)
    
    print("\n\nSubcontracting Receipt Items found:\n", receipt_items)
    
    if not receipt_items:
        return []
    
    # Get Subcontracting Order Items for po_qty and purchase_order_item mapping
    sco_order_items = frappe.db.sql("""
        SELECT 
            parent as subcontracting_order,
            item_code,
            qty as po_qty,
            purchase_order_item
        FROM `tabSubcontracting Order Item`
        WHERE parent IN %s
    """, (sco_tuple,), as_dict=True)
    
    print("\n\nSubcontracting Order Items found:\n", sco_order_items)
    
    # Create mapping for po_qty and purchase_order_item by (subcontracting_order, item_code)
    po_qty_map = {}
    purchase_order_item_map = {}
    for item in sco_order_items:
        key = (item['subcontracting_order'], item['item_code'])
        po_qty_map[key] = item.get('po_qty', 0)
        purchase_order_item_map[key] = item.get('purchase_order_item', '')
    
    # Get PO Rate from Purchase Order Item table
    purchase_order_items_list = list(set([item.get('purchase_order_item') for item in sco_order_items if item.get('purchase_order_item')]))
    po_rate_map = {}
    
    if purchase_order_items_list:
        po_item_tuple = tuple(purchase_order_items_list)
        purchase_order_items = frappe.db.sql("""
            SELECT 
                name,
                rate as po_rate
            FROM `tabPurchase Order Item`
            WHERE name IN %s
        """, (po_item_tuple,), as_dict=True)
        
        po_rate_map = {item['name']: item.get('po_rate', 0) for item in purchase_order_items}
    
    print("\n\nPurchase Order Items Rate Map:\n", po_rate_map)
    
    # Get UOM for each item from Item master (as fallback)
    item_codes = list(set([item['item_code'] for item in receipt_items if item['item_code']]))
    item_uom_map = {}
    
    if item_codes:
        item_tuple = tuple(item_codes)
        item_data = frappe.db.sql("""
            SELECT item_code, stock_uom
            FROM `tabItem`
            WHERE item_code IN %s
        """, (item_tuple,), as_dict=True)
        
        item_uom_map = {item['item_code']: item['stock_uom'] for item in item_data}
    
    # Create mapping from SCO name to purchase order
    sco_po_map = {sco['name']: sco['purchase_order'] for sco in sco_list}
    
    # Get all Purchase Receipts linked to these Subcontracting Receipts
    subcontracting_receipts = list(set([item['subcontracting_receipt'] for item in receipt_items]))
    pr_receipt_map = {}
    pr_items_map = {}
    
    if subcontracting_receipts:
        pr_tuple = tuple(subcontracting_receipts)
        # Get Purchase Receipts
        purchase_receipts = frappe.db.sql("""
            SELECT name, subcontracting_receipt
            FROM `tabPurchase Receipt`
            WHERE subcontracting_receipt IN %s AND docstatus = 1
        """, (pr_tuple,), as_dict=True)
        
        pr_receipt_map = {pr['subcontracting_receipt']: pr['name'] for pr in purchase_receipts}
        
        # Get Purchase Receipt Items with subcontracting_receipt_item reference
        purchase_receipt_names = list(pr_receipt_map.values())
        if purchase_receipt_names:
            pr_name_tuple = tuple(purchase_receipt_names)
            purchase_receipt_items = frappe.db.sql("""
                SELECT 
                    parent as purchase_receipt,
                    name as purchase_receipt_item,
                    subcontracting_receipt_item,
                    item_code,
                    qty,
                    rate,
                    amount
                FROM `tabPurchase Receipt Item`
                WHERE parent IN %s
            """, (pr_name_tuple,), as_dict=True)
            
            for pri in purchase_receipt_items:
                if pri['purchase_receipt'] not in pr_items_map:
                    pr_items_map[pri['purchase_receipt']] = {}
                pr_items_map[pri['purchase_receipt']][pri['subcontracting_receipt_item']] = pri
    
    print("\n\nPurchase Receipts found:\n", pr_receipt_map)
    print("\n\nPurchase Receipt Items found:\n", pr_items_map)
    
    # Get all Purchase Invoices linked to these Purchase Receipts
    purchase_receipt_names = list(pr_receipt_map.values())
    pi_receipt_map = {}  # Store list of PIs per PR
    pi_bill_map = {}
    
    if purchase_receipt_names:
        pr_tuple = tuple(purchase_receipt_names)
        # Get Purchase Invoices linked to Purchase Receipts
        purchase_invoices = frappe.db.sql("""
            SELECT pi.name, pi.bill_no, pii.purchase_receipt, pii.pr_detail
            FROM `tabPurchase Invoice` pi
            INNER JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
            WHERE pii.purchase_receipt IN %s AND pi.docstatus != 2
        """, (pr_tuple,), as_dict=True)
        
        # Store multiple PIs per PR
        for pi in purchase_invoices:
            if pi['purchase_receipt'] not in pi_receipt_map:
                pi_receipt_map[pi['purchase_receipt']] = []
            pi_receipt_map[pi['purchase_receipt']].append(pi['name'])
            pi_bill_map[pi['name']] = pi.get('bill_no', '')
    
    print("\n\nPurchase Invoices found:\n", pi_receipt_map)
    print("\n\nPurchase Invoice Bill Numbers:\n", pi_bill_map)
    
    # Combine data for received_details - ONE ENTRY PER RECEIPT ITEM
    received_details = []
    
    for item in receipt_items:
        # Use UOM from receipt item, fallback to item master
        uom = item.get('stock_uom') or item_uom_map.get(item['item_code'], '')
        
        # Get purchase order from mapping
        purchase_order = sco_po_map.get(item['subcontracting_order'], '')
        
        # Get po_qty and purchase_order_item from mapping
        key = (item['subcontracting_order'], item['item_code'])
        po_qty = po_qty_map.get(key, 0)
        purchase_order_item = purchase_order_item_map.get(key, '')
        
        # Get po_rate from Purchase Order Item table
        po_rate = po_rate_map.get(purchase_order_item, 0)
        
        # Get linked Purchase Receipt
        purchase_receipt = pr_receipt_map.get(item['subcontracting_receipt'], '')
        
        # Get Purchase Receipt Item details using subcontracting_receipt_item
        pr_item_details = {}
        if purchase_receipt and purchase_receipt in pr_items_map:
            pr_item_details = pr_items_map[purchase_receipt].get(item['subcontracting_receipt_item'], {})
        
        # Get the Purchase Receipt Item name (this will be used as pr_detail)
        purchase_receipt_item_name = pr_item_details.get('purchase_receipt_item', '')
        
        # Get linked Purchase Invoices and Bill Nos (handle multiple PIs)
        purchase_invoices = pi_receipt_map.get(purchase_receipt, [])
        
        # Instead of creating multiple entries, aggregate PI data or take the first one
        if purchase_invoices:
            # For multiple PIs, you might want to aggregate or choose one approach
            # Option 1: Take the first PI
            first_pi = purchase_invoices[0]
            bill_no = pi_bill_map.get(first_pi, '')
            
            # Option 2: Or you can create comma-separated values for multiple PIs
            # pi_list = ", ".join(purchase_invoices)
            # bill_list = ", ".join([pi_bill_map.get(pi, '') for pi in purchase_invoices if pi_bill_map.get(pi, '')])
            
            purchase_invoice = first_pi
        else:
            purchase_invoice = ''
            bill_no = ''
        
        # Create only ONE entry per receipt item
        received_details.append({
            'purchase_order': purchase_order,
            'subcontracting_order': item['subcontracting_order'],
            'item_code': item['item_code'],
            'po_rate': po_rate,  # Use PO Rate from Purchase Order Item
            'po_qty': po_qty,
            'received_qty': item['received_qty'],
            'subcontracting_receipt': item['subcontracting_receipt'],
            'subcontracting_receipt_item': item['subcontracting_receipt_item'],
            'purchase_receipt': purchase_receipt,
            'purchase_receipt_item': purchase_receipt_item_name,
            'pr_detail': purchase_receipt_item_name,
            'pr_qty': pr_item_details.get('qty', 0),
            'pr_rate': pr_item_details.get('rate', 0),
            'pr_amount': pr_item_details.get('amount', 0),
            'purchase_invoice': purchase_invoice,
            'bill_no': bill_no,
            'uom': uom
        })
    
    print("\n\nFinal received_details (deduplicated):\n", received_details)
    return received_details

    

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
                "po_item_code": item.get("po_item_code", ""),
                "po_qty": item.get("po_qty", 0),
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
            name,
            required_qty as po_qty
        FROM `tabSubcontracting Order Supplied Item`
        WHERE parent IN %s and docstatus = 1
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
    print("\n\nstock_entries_data\n\n",stock_entries_data)
    
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
                    # sco_rm_detail == name
                    if stock_item.get('sco_rm_detail') == sco_item['name']:
                    # if stock_item.get('item_code') == sco_item['item_code']:
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
    
    # Get Subcontracting Order Supplied Items for main_item_code and po_qty mapping
    sco_supplied_items = frappe.db.sql("""
        SELECT 
            parent as subcontracting_order,
            rm_item_code as item_code,
            main_item_code,
            name,
            required_qty as po_qty
        FROM `tabSubcontracting Order Supplied Item`
        WHERE parent IN %s
    """, (sco_tuple,), as_dict=True)
    
    # Create mapping for main_item_code and po_qty
    item_main_item_map = {}
    item_po_qty_map = {}
    print("\n\nsco_supplied_items\n\n",sco_supplied_items)
    for item in sco_supplied_items:
        key = (item['subcontracting_order'], item['item_code'])
        item_main_item_map[key] = item.get('main_item_code', '')
        item_po_qty_map[key] = item.get('po_qty', 0)
    
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
                # Get main_item_code and po_qty from mapping
                key = (sco['name'], stock_item.get('item_code'))
                main_item_code = item_main_item_map.get(key, '')
                po_qty = item_po_qty_map.get(key, 0)
                
                uom = item_uom_map.get(stock_item.get('item_code'), '')
                
                return_details.append({
                    'purchase_order': sco['purchase_order'],
                    'subcontracting_order': sco['name'],
                    'item_code': stock_item.get('item_code'),
                    'po_item_code': main_item_code,
                    'po_qty': po_qty,  # Added po_qty here
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
            item_code, qty, uom, sco_rm_detail,
            s_warehouse, t_warehouse, po_detail
        FROM `tabStock Entry Detail`
        WHERE parent = %s
        ORDER BY idx
    """, (stock_entry_name,), as_dict=True)
    
    return stock_entry_details