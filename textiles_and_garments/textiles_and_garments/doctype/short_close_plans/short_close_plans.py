# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today
import json
from collections import defaultdict
from frappe import _
import json # <--- Import json module



class ShortClosePlans(Document):
    print("\n\nShortClosePlans\n\n")
    




@frappe.whitelist()
def get_work_order_orders_by_plan_no(doctype, txt, searchfield, start, page_len, filters):
    parsed_filters = filters
    plans_no = parsed_filters.get("plans_no")

    if not plans_no:
        return []

    # Get the names of Work Orders that match the custom_plans_no
    # frappe.db.sql is used here to get a list of names, as frappe.db.get_value
    # is for a single record's single field.
    work_order_names_list = frappe.db.sql(
        """
        SELECT name
        FROM `tabWork Order`
        WHERE custom_plans = %s
          AND docstatus = 1
        ORDER BY creation DESC
        LIMIT %s OFFSET %s
        """,
        (plans_no, page_len, start),
        as_list=True # Get results as a list of lists/tuples
    )

    results = []
    for wo_name_tuple in work_order_names_list:
        wo_name = wo_name_tuple[0] # Extract the name from the tuple
        if wo_name:
            # You *could* use frappe.db.get_value here if you needed another field
            # from the Work Order itself, but for just the name, it's redundant
            # as you already have the name from the SQL query.
            # Example (if you needed to fetch, say, its 'status' separately):
            # wo_status = frappe.db.get_value("Work Order", wo_name, "status")
            results.append([wo_name, wo_name])

    return results


@frappe.whitelist()
def get_purchase_orders_by_plan_no(doctype, txt, searchfield, start, page_len, filters):
    parsed_filters = filters
    plans_no = parsed_filters.get("plans_no")
    print("\n\nplans_no\n\n", plans_no)
    item_code = parsed_filters.get("item_code")
    print("\n\nitem_code\n\n",item_code)

    if not plans_no:
        return []

    # Get distinct parent names from Purchase Order Item table
    # This uses frappe.db.sql to perform a direct SQL query,
    # as frappe.db.get_value is for single value retrieval
    # and not optimized for fetching multiple distinct parents from child tables easily.
    # Note: This is an alternative to frappe.get_list for this specific step.
    # frappe.get_list is generally preferred for its ORM capabilities.
    po_names_raw = frappe.db.sql(
        """
        SELECT DISTINCT parent
        FROM `tabPurchase Order Item`
        WHERE custom_plans = %s AND fg_item = %s
          AND parenttype = 'Purchase Order'
          AND parentfield = 'items'
          AND docstatus = 1
        ORDER BY creation DESC
        LIMIT %s OFFSET %s
        """,
        (plans_no, item_code, page_len, start),
        as_dict=True
    )

    print("\n\npo_names_raw\n\n", po_names_raw)

    results = []
    for item in po_names_raw:
        po_name = item.get("parent")
        if po_name:
            # You could technically use frappe.db.get_value here if you needed more fields
            # from the parent PO, but for just the name, it's redundant after the SQL query.
            # Example (not needed for just the name):
            # po_doc_status = frappe.db.get_value("Purchase Order", po_name, "docstatus")
            results.append([po_name, po_name])

    return results

@frappe.whitelist()
def get_psr_details(plans_no):
    """
    Fetches the 'sb_entries' table from the Production Stock Reservation document
    based on the provided plans_no.
    """
    print(f"\n\nFetching PSR details for plans_no: {plans_no}\n\n")

    # Find the Production Stock Reservation document where 'plans_no' matches
    psr_doc_name = frappe.db.get_value(
        "Production Stock Reservation",
        {"plans_no": plans_no},
        "name"
    )

    if psr_doc_name:
        # If a matching document is found, fetch its 'sb_entries' child table
        psr_doc = frappe.get_doc("Production Stock Reservation", psr_doc_name)
        return psr_doc.get("sb_entries")
    else:
        return [] # Return an empty list if no matching document is found


@frappe.whitelist()
def get_po_item_details(purchase_order, item_code):
    print(f"\n\nFetching item_code details for purchase_order: {purchase_order}, item_code: {item_code}\n\n")

    if not purchase_order or not item_code:
        return None # Return None if essential filters are missing

    # Get the 'qty' from the 'Purchase Order Item' child table
    # where the parent is the specified purchase_order
    # and the item_code matches.
    qty = frappe.db.get_value(
        "Purchase Order Item",
        filters={
            "parent": purchase_order,
            "fg_item": item_code
        },
        fieldname="qty" # Specify the field you want to retrieve
    )

    print(f"\n\nRetrieved Quantity: {qty}\n\n")
    return qty


@frappe.whitelist()
def update_production_stock_reservation(plans_no, sb_entries):
    """
    Update the short_close_qty in Production Stock Reservation based on Short Close Plan
    
    Args:
        plans_no (str): The plans_no field value in Production Stock Reservation
        sb_entries (list/dict): List of stock entry items with warehouse, batch_no and short_close_qty
    """
    print("\n\nupdate_production_stock_reservation\n\n")
    print("\n\nplans_no\n\n", plans_no)
    print("\n\nsb_entries\n\n", sb_entries)
    
    if not plans_no:
        frappe.throw(_("plans_no is missing."))
    
    try:
        if isinstance(sb_entries, str):
            sb_entries = json.loads(sb_entries)
        elif not isinstance(sb_entries, list):
            frappe.throw(_("Invalid format for sb_entries. Expected a list or JSON string."))
    except json.JSONDecodeError:
        frappe.throw(_("Could not parse sb_entries. Invalid JSON format."))
    
    if not sb_entries:
        frappe.msgprint(_("No stock entries provided from Short Close Plan to update Production Stock Reservation."))
        return False

    try:
        # Find Production Stock Reservation document where plans_no field matches
        psr_name = frappe.db.get_value(
            "Production Stock Reservation",
            filters={"plans_no": plans_no},
            fieldname="name"
        )
        
        if not psr_name:
            frappe.throw(_(f"Production Stock Reservation with plans_no '{plans_no}' not found."))
            
        psr_doc = frappe.get_doc("Production Stock Reservation", psr_name)
    except Exception as e:
        frappe.throw(_(f"Error fetching Production Stock Reservation: {e}"))

    # Create a dictionary for quick lookup of short close quantities by warehouse and batch_no
    short_close_map = {}
    for entry in sb_entries:
        key = (entry.get('warehouse'), entry.get('batch_no'))
        if key:
            short_close_map[key] = entry.get('short_close_qty', 0)
    
    print("\n\nshort_close_map built:", short_close_map, "\n\n")

    updated_any_item = False
    for psr_item in psr_doc.sb_entries:
        # Create the same key for matching
        key = (psr_item.warehouse, psr_item.batch_no)
        print("\n\nProcessing PSR Item:", psr_item.name, "Warehouse:", psr_item.warehouse, 
              "Batch:", psr_item.batch_no, "Key:", key, "\n\n")
        
        if key in short_close_map:
            psr_item.short_close_qty = short_close_map[key]
            updated_any_item = True
            print(f"Updated PSR Item {psr_item.name} (Warehouse: {psr_item.warehouse}, Batch: {psr_item.batch_no}) with short_close_qty: {psr_item.short_close_qty}")
        else:
            print(f"PSR Item's warehouse/batch combination {key} not found in short_close_map.")

    if updated_any_item:
        try:
            psr_doc.save(ignore_permissions=False)
            frappe.db.commit()
            frappe.msgprint(_(f"Production Stock Reservation '{psr_name}' updated successfully."))
            return True
        except Exception as e:
            frappe.db.rollback()
            frappe.throw(_(f"Error saving Production Stock Reservation '{psr_name}': {e}"))
    else:
        frappe.msgprint(_("No matching items found in Production Stock Reservation to update based on sb_entries."))
        return False


@frappe.whitelist()
def cancel_production_stock_reservation(plans_no, sb_entries):
    """
    Update the short_close_qty in Production Stock Reservation based on Short Close Plan
    
    Args:
        plans_no (str): The plans_no field value in Production Stock Reservation
        sb_entries (list/dict): List of stock entry items with warehouse, batch_no and short_close_qty
    """
    print("\n\ncancel_production_stock_reservation\n\n")
    print("\n\nplans_no\n\n", plans_no)
    print("\n\nsb_entries\n\n", sb_entries)
    
    if not plans_no:
        frappe.throw(_("plans_no is missing."))
    
    try:
        if isinstance(sb_entries, str):
            sb_entries = json.loads(sb_entries)
        elif not isinstance(sb_entries, list):
            frappe.throw(_("Invalid format for sb_entries. Expected a list or JSON string."))
    except json.JSONDecodeError:
        frappe.throw(_("Could not parse sb_entries. Invalid JSON format."))
    
    if not sb_entries:
        frappe.msgprint(_("No stock entries provided from Short Close Plan to update Production Stock Reservation."))
        return False

    try:
        # Find Production Stock Reservation document where plans_no field matches
        psr_name = frappe.db.get_value(
            "Production Stock Reservation",
            filters={"plans_no": plans_no},
            fieldname="name"
        )
        
        if not psr_name:
            frappe.throw(_(f"Production Stock Reservation with plans_no '{plans_no}' not found."))
            
        psr_doc = frappe.get_doc("Production Stock Reservation", psr_name)
    except Exception as e:
        frappe.throw(_(f"Error fetching Production Stock Reservation: {e}"))

    # Create a dictionary for quick lookup of short close quantities by warehouse and batch_no
    short_close_map = {}
    for entry in sb_entries:
        key = (entry.get('warehouse'), entry.get('batch_no'))
        if key:
            short_close_map[key] = entry.get('short_close_qty', 0)
    
    print("\n\nshort_close_map built:", short_close_map, "\n\n")

    updated_any_item = False
    for psr_item in psr_doc.sb_entries:
        # Create the same key for matching
        key = (psr_item.warehouse, psr_item.batch_no)
        print("\n\nProcessing PSR Item:", psr_item.name, "Warehouse:", psr_item.warehouse, 
              "Batch:", psr_item.batch_no, "Key:", key, "\n\n")
        
        if key in short_close_map:
            psr_item.short_close_qty = 0
            updated_any_item = True
            print(f"Updated PSR Item {psr_item.name} (Warehouse: {psr_item.warehouse}, Batch: {psr_item.batch_no}) with short_close_qty: {psr_item.short_close_qty}")
        else:
            print(f"PSR Item's warehouse/batch combination {key} not found in short_close_map.")

    if updated_any_item:
        try:
            psr_doc.save(ignore_permissions=False)
            frappe.db.commit()
            frappe.msgprint(_(f"Production Stock Reservation '{psr_name}' updated successfully."))
            return True
        except Exception as e:
            frappe.db.rollback()
            frappe.throw(_(f"Error saving Production Stock Reservation '{psr_name}': {e}"))
    else:
        frappe.msgprint(_("No matching items found in Production Stock Reservation to update based on sb_entries."))
        return False        


@frappe.whitelist()
def update_purchase_order_quantities(purchase_order_name, short_close_plan_items):
    print("\n\nupdate_purchase_order_quantities\n\n")
    print("\n\npurchase_order_name\n\n",purchase_order_name)
    print("\n\nshort_close_plan_items\n\n",short_close_plan_items)
    if not purchase_order_name:
        frappe.throw(_("Purchase Order name is missing."))
    
    try:
        if isinstance(short_close_plan_items, str):
            short_close_plan_items = json.loads(short_close_plan_items)
        elif not isinstance(short_close_plan_items, list):
            frappe.throw(_("Invalid format for Short Close Plan items. Expected a list or JSON string."))
    except json.JSONDecodeError:
        frappe.throw(_("Could not parse Short Close Plan items. Invalid JSON format."))
    
    if not short_close_plan_items:
        frappe.msgprint(_("No items provided from Short Close Plan to update Purchase Order."))
        return False

    try:
        po_doc = frappe.get_doc("Purchase Order", purchase_order_name)
    except frappe.DoesNotExistError:
        frappe.throw(_(f"Purchase Order '{purchase_order_name}' not found."))
    except Exception as e:
        frappe.throw(_(f"Error fetching Purchase Order '{purchase_order_name}': {e}"))

    # Create a dictionary for quick lookup of short close quantities by fg_item
    # Use 'fg_item' as the key from the incoming data
    short_close_map = {item['fg_item']: item['short_close_qty'] for item in short_close_plan_items}
    print("\n\nshort_close_map built: {short_close_map}\n\n")

    updated_any_item = False
    for po_item in po_doc.items:
        # Consistently use 'fg_item' for matching against the map
        print("\n\nProcessing PO Item: {po_item.name}, Item Code: {po_item.item_code}, FG Item: {po_item.fg_item}\n\n") # Debugging print
        if po_item.fg_item in short_close_map:
            po_item.custom_short_close_plan_qty = short_close_map[po_item.fg_item] # Use fg_item as the key to retrieve the value
            updated_any_item = True
            print(f"Updated PO Item {po_item.name} (FG Item: {po_item.fg_item}) with custom_short_close_plan_qty: {po_item.custom_short_close_plan_qty}")
        else:
            print(f"PO Item's fg_item '{po_item.fg_item}' not found in short_close_map.")

    if updated_any_item:
        try:
            po_doc.save(ignore_permissions=False)
            frappe.db.commit()
            frappe.msgprint(_(f"Purchase Order '{purchase_order_name}' updated successfully."))
            return True
        except Exception as e:
            frappe.db.rollback()
            frappe.throw(_(f"Error saving Purchase Order '{purchase_order_name}': {e}"))
    else:
        frappe.msgprint(_("No matching items found in Purchase Order to update based on Short Close Plan items."))
        return False        


@frappe.whitelist()
def update_work_order_quantities(work_order_name, short_close_plan_items):
    """
    Updates the 'custom_short_close_plan_qty' (or similar field) in the Work Order document itself
    or its relevant child table, based on the items from Short Close Plan.
    
    Assumes Work Order has a 'custom_short_close_plan_qty' field or a child table with 'fg_item'
    and a quantity field to update. For simplicity, this example updates a custom field
    on the main Work Order document if a single fg_item is provided,
    or a child table if Work Order uses a similar 'items' structure.
    
    NOTE: Work Orders don't typically have an 'items' child table like Purchase Orders.
    They have 'raw_materials', 'finished_goods', etc. You need to identify which field
    or child table within the Work Order you intend to update.
    
    For this example, I'll assume:
    1. The Work Order document itself has a field 'fg_item' and 'custom_short_close_plan_qty'.
       (This is common if the Short Close Plan is for a single finished good per Work Order).
    2. If the Work Order has a child table that needs updating, you'd iterate that.
    """
    print("\n\nupdate_work_order_quantities\n\n")
    print("\n\nwork_order_name\n\n", work_order_name)
    print("\n\nshort_close_plan_items\n\n", short_close_plan_items)

    if not work_order_name:
        frappe.throw(_("Work Order name is missing."))
    
    try:
        if isinstance(short_close_plan_items, str):
            short_close_plan_items = json.loads(short_close_plan_items)
        elif not isinstance(short_close_plan_items, list):
            frappe.throw(_("Invalid format for Short Close Plan items. Expected a list or JSON string."))
    except json.JSONDecodeError:
        frappe.throw(_("Could not parse Short Close Plan items. Invalid JSON format."))
    
    if not short_close_plan_items:
        frappe.msgprint(_("No items provided from Short Close Plan to update Work Order."))
        return False

    try:
        wo_doc = frappe.get_doc("Work Order", work_order_name)
    except frappe.DoesNotExistError:
        frappe.throw(_(f"Work Order '{work_order_name}' not found."))
    except Exception as e:
        frappe.throw(_(f"Error fetching Work Order '{work_order_name}': {e}"))

    # Create a dictionary for quick lookup of short close quantities by fg_item
    short_close_map = {item['fg_item']: item['short_close_qty'] for item in short_close_plan_items}
    print(f"\n\nshort_close_map built: {short_close_map}\n\n")

    updated_any_item = False

    # IMPORTANT: Work Orders typically don't have a generic 'items' child table like POs.
    # You need to decide where 'fg_item' and 'custom_short_close_plan_qty' are.

    # Option A: If custom_short_close_plan_qty is directly on the Work Order document
    # and it's for the main production_item of the WO.
    if wo_doc.production_item in short_close_map:
        # Assuming 'custom_short_close_plan_qty' is a field on the Work Order DocType itself.
        wo_doc.custom_short_close_plan_qty = short_close_map[wo_doc.production_item]
        updated_any_item = True
        print(f"Updated Work Order {wo_doc.name} (Finished Item: {wo_doc.production_item}) with custom_short_close_plan_qty: {wo_doc.custom_short_close_plan_qty}")
    else:
        print(f"Work Order's production_item '{wo_doc.production_item}' not found in short_close_map.")

    # Option B: If Work Order has a custom child table (e.g., 'wo_finished_items')
    # similar to Purchase Order Items, and you want to iterate through it.
    # Replace 'wo_finished_items' with the actual fieldname of your child table if it exists.
    # for wo_finished_item_row in wo_doc.wo_finished_items:
    #     if wo_finished_item_row.fg_item in short_close_map:
    #         wo_finished_item_row.custom_short_close_plan_qty = short_close_map[wo_finished_item_row.fg_item]
    #         updated_any_item = True
    #         print(f"Updated WO Item {wo_finished_item_row.name} (FG Item: {wo_finished_item_row.fg_item}) with custom_short_close_plan_qty: {wo_finished_item_row.custom_short_close_plan_qty}")
    #     else:
    #         print(f"WO Finished Item's fg_item '{wo_finished_item_row.fg_item}' not found in short_close_map.")


    if updated_any_item:
        try:
            # For Work Order, 'Allow on Submit' is crucial if already submitted.
            wo_doc.save(ignore_permissions=False)
            frappe.db.commit()
            frappe.msgprint(_(f"Work Order '{work_order_name}' updated successfully."))
            return True
        except Exception as e:
            frappe.db.rollback()
            frappe.throw(_(f"Error saving Work Order '{work_order_name}': {e}"))
    else:
        frappe.msgprint(_("No matching items found in Work Order to update based on Short Close Plan items."))
        return False