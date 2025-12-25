# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt
import json

class WorkOrderProcessLoss(Document):
    pass

@frappe.whitelist()
def calculate_process_loss(doc):
    """
    Fetch data for sent, return, and received details based on work orders
    """
    if isinstance(doc, str):
        doc = frappe.get_doc(json.loads(doc))
    
    # Clear existing child table data
    doc.work_order_sent_details = []
    doc.work_order_return_details = []
    doc.work_order_received_details = []
    
    # Get all work orders from the Work Orders child table
    work_orders = [row.work_order for row in doc.work_orders if row.work_order]
    
    if not work_orders:
        frappe.msgprint(_("No Work Orders found to calculate process loss"))
        return doc
    
    # Fetch Sent Details (Material Transfer for Manufacture - Outgoing)
    fetch_sent_details(doc, work_orders)
    
    # Fetch Return Details (Material Transfer for Manufacture - Incoming/Return)
    fetch_return_details(doc, work_orders)
    
    # Fetch Received Details (Manufacture - Finished Goods)
    fetch_received_details(doc, work_orders)
    
    return doc


def fetch_sent_details(doc, work_orders):
    """
    Fetch material sent to work orders (Material Transfer for Manufacture)
    """
    stock_entries = frappe.db.sql("""
        SELECT 
            se.name as stock_entry,
            se.work_order,
            sed.item_code,
            wo.production_item as wo_item_code,
            wo.qty as wo_qty,
            SUM(sed.qty) as sent_qty,
            sed.uom
        FROM 
            `tabStock Entry` se
        INNER JOIN 
            `tabStock Entry Detail` sed ON se.name = sed.parent
        INNER JOIN
            `tabWork Order` wo ON se.work_order = wo.name
        WHERE 
            se.docstatus = 1
            AND se.work_order IN %(work_orders)s
            AND (
                se.purpose = 'Material Transfer for Manufacture'
                OR se.purpose = 'Material Transfer'
            )
            AND (
                se.naming_series LIKE 'YEI%%'
                OR se.naming_series LIKE 'MTM%%'
            )
            AND sed.s_warehouse IS NOT NULL
            AND sed.t_warehouse IS NOT NULL
        GROUP BY
            se.work_order,
            sed.item_code,
            se.name
        ORDER BY
            se.posting_date, se.posting_time
    """, {"work_orders": work_orders}, as_dict=1)
    
    for entry in stock_entries:
        doc.append("work_order_sent_details", {
            "work_order": entry.work_order,
            "stock_entry": entry.stock_entry,
            "item_code": entry.item_code,
            "wo_item_code": entry.wo_item_code,
            "wo_qty": entry.wo_qty,
            "sent_qty": entry.sent_qty,
            "uom": entry.uom
        })


def fetch_return_details(doc, work_orders):
    """
    Fetch material returned from work orders
    """
    stock_entries = frappe.db.sql("""
        SELECT 
            se.name as stock_entry,
            se.work_order,
            sed.item_code,
            wo.production_item as wo_item_code,
            wo.qty as wo_qty,
            SUM(sed.qty) as return_qty,
            sed.uom
        FROM 
            `tabStock Entry` se
        INNER JOIN 
            `tabStock Entry Detail` sed ON se.name = sed.parent
        INNER JOIN
            `tabWork Order` wo ON se.work_order = wo.name
        WHERE 
            se.docstatus = 1
            AND se.work_order IN %(work_orders)s
            AND (se.naming_series LIKE 'YRET%%' OR se.naming_series LIKE 'MT%%')
            AND sed.s_warehouse IS NOT NULL
            AND sed.t_warehouse IS NOT NULL
            AND sed.s_warehouse = wo.wip_warehouse
        GROUP BY
            se.work_order,
            sed.item_code,
            se.name
        ORDER BY
            se.posting_date, se.posting_time
    """, {"work_orders": work_orders}, as_dict=1)
    
    for entry in stock_entries:
        doc.append("work_order_return_details", {
            "work_order": entry.work_order,
            "stock_entry": entry.stock_entry,
            "item_code": entry.item_code,
            "wo_item_code": entry.wo_item_code,
            "wo_qty": entry.wo_qty,
            "return_qty": entry.return_qty,
            "uom": entry.uom
        })


def fetch_received_details(doc, work_orders):
    """
    Fetch finished goods received from work orders (Manufacture entries)
    """
    stock_entries = frappe.db.sql("""
        SELECT 
            se.name as stock_entry,
            se.work_order,
            sed.item_code,
            wo.qty as wo_qty,
            SUM(sed.qty) as received_qty,
            sed.uom
        FROM 
            `tabStock Entry` se
        INNER JOIN 
            `tabStock Entry Detail` sed ON se.name = sed.parent
        INNER JOIN
            `tabWork Order` wo ON se.work_order = wo.name
        WHERE 
            se.docstatus = 1
            AND se.work_order IN %(work_orders)s
            AND se.purpose = 'Manufacture'
            AND sed.is_finished_item = 1
            AND sed.t_warehouse IS NOT NULL
        GROUP BY
            se.work_order,
            sed.item_code,
            se.name
        ORDER BY
            se.posting_date, se.posting_time
    """, {"work_orders": work_orders}, as_dict=1)
    
    for entry in stock_entries:
        doc.append("work_order_received_details", {
            "work_order": entry.work_order,
            "stock_entry": entry.stock_entry,
            "item_code": entry.item_code,
            "wo_qty": entry.wo_qty,
            "received_qty": entry.received_qty,
            "uom": entry.uom
        })


def get_work_order_item_mapping(work_order_list):
    """
    Get mapping of raw materials to finished goods from Work Order's required_items table
    Returns: dict with structure {work_order: {finished_item: 'SKF...', raw_items: {...}}}
    """
    if not work_order_list:
        return {}
    
    # Get Work Order details with production_item
    work_orders = frappe.db.sql("""
        SELECT name, production_item
        FROM `tabWork Order`
        WHERE name IN %(work_orders)s
    """, {"work_orders": work_order_list}, as_dict=1)
    
    # Create mapping structure
    wo_mapping = {}
    
    for wo in work_orders:
        wo_name = wo['name']
        finished_item = wo['production_item']
        
        # Get required items for this work order
        required_items = frappe.db.sql("""
            SELECT item_code, required_qty
            FROM `tabWork Order Item`
            WHERE parent = %s
        """, (wo_name,), as_dict=1)
        
        # Map each raw material to the finished product
        wo_mapping[wo_name] = {
            'finished_item': finished_item,
            'raw_items': {}
        }
        
        for item in required_items:
            wo_mapping[wo_name]['raw_items'][item['item_code']] = {
                'finished_item': finished_item,
                'required_qty': item['required_qty']
            }
    
    print(f"\nWork Order Item Mapping: {wo_mapping}")
    return wo_mapping


def get_finished_to_raw_mapping(work_order_list):
    """
    Get reverse mapping from finished goods to raw materials
    Returns: dict with structure {work_order: {finished_item: [raw_item_codes]}}
    """
    if not work_order_list:
        return {}
    
    # Get Work Order details with production_item
    work_orders = frappe.db.sql("""
        SELECT name, production_item
        FROM `tabWork Order`
        WHERE name IN %(work_orders)s
    """, {"work_orders": work_order_list}, as_dict=1)
    
    # Create reverse mapping structure
    finished_to_raw = {}
    
    for wo in work_orders:
        wo_name = wo['name']
        finished_item = wo['production_item']
        
        # Get required items for this work order
        required_items = frappe.db.sql("""
            SELECT item_code, required_qty
            FROM `tabWork Order Item`
            WHERE parent = %s
        """, (wo_name,), as_dict=1)
        
        finished_to_raw[wo_name] = {
            'finished_item': finished_item,
            'raw_items': [item['item_code'] for item in required_items]
        }
    
    print(f"\nFinished to Raw Mapping: {finished_to_raw}")
    return finished_to_raw


@frappe.whitelist()
def calculate_summary(doc):
    """
    Calculate process loss summary based on sent, return, and received details
    Uses Work Order's required_items table to map raw materials to finished goods
    Shows RAW ITEMS in the summary table instead of finished items
    Formula: Process Loss Qty = (Sent Qty - Return Qty) - (Received Qty converted to raw material equivalent)
    Process Loss % = (Process Loss Qty / (Sent Qty - Return Qty)) * 100
    """
    if isinstance(doc, str):
        doc = frappe.get_doc(json.loads(doc))
    
    # Clear existing summary data
    doc.work_order_process_loss_details = []
    
    # Get all work orders
    work_order_list = list(set([row.work_order for row in doc.work_orders if row.work_order]))
    
    if not work_order_list:
        frappe.msgprint(_("No Work Orders found"))
        return doc
    
    # Get item mapping from Work Order's required_items table
    wo_item_mapping = get_work_order_item_mapping(work_order_list)
    finished_to_raw = get_finished_to_raw_mapping(work_order_list)
    
    # Dictionary to aggregate data by work_order and RAW ITEM CODE
    summary_data = {}
    
    # Process Sent Details - Group by RAW ITEM
    for sent in doc.work_order_sent_details:
        work_order = sent.work_order
        raw_item_code = sent.item_code
        
        # Get the finished item from work order mapping
        if work_order not in wo_item_mapping:
            print(f"Work Order {work_order} not found in mapping")
            continue
        
        finished_item_code = wo_item_mapping[work_order]['finished_item']
        
        # Skip if raw item is not in the required items list
        if raw_item_code not in wo_item_mapping[work_order]['raw_items']:
            # Skip DYES% and CHEM% items silently
            if not (raw_item_code and (raw_item_code.startswith("DYES") or raw_item_code.startswith("CHEM"))):
                print(f"Skipping sent item: {raw_item_code} - not in required items")
            continue
        
        # Skip DYES% and CHEM% items explicitly
        if raw_item_code and (raw_item_code.startswith("DYES") or raw_item_code.startswith("CHEM")):
            print(f"Skipping sent item: {raw_item_code} (DYES/CHEM item)")
            continue
        
        # Use RAW ITEM as the key
        key = (work_order, raw_item_code)

        if key not in summary_data:
            summary_data[key] = {
                'work_order': work_order,
                'item_code': raw_item_code,  # RAW ITEM
                'finished_item_code': finished_item_code,  # Store for reference
                'wo_qty': sent.wo_qty,
                'uom': sent.uom,
                'sent_qty': 0,
                'return_qty': 0,
                'received_qty': 0
            }

        summary_data[key]['sent_qty'] += flt(sent.sent_qty)
        print(f"Added sent_qty {flt(sent.sent_qty)} for raw item {raw_item_code}")

    # Process Return Details - Group by RAW ITEM
    for ret in doc.work_order_return_details:
        work_order = ret.work_order
        raw_item_code = ret.item_code
        
        # Get the finished item from work order mapping
        if work_order not in wo_item_mapping:
            print(f"Work Order {work_order} not found in mapping")
            continue
        
        finished_item_code = wo_item_mapping[work_order]['finished_item']
        
        # Skip if raw item is not in the required items list
        if raw_item_code not in wo_item_mapping[work_order]['raw_items']:
            # Skip DYES% and CHEM% items silently
            if not (raw_item_code and (raw_item_code.startswith("DYES") or raw_item_code.startswith("CHEM"))):
                print(f"Skipping return item: {raw_item_code} - not in required items")
            continue
        
        # Skip DYES% and CHEM% items explicitly
        if raw_item_code and (raw_item_code.startswith("DYES") or raw_item_code.startswith("CHEM")):
            print(f"Skipping return item: {raw_item_code} (DYES/CHEM item)")
            continue
        
        # Use RAW ITEM as the key
        key = (work_order, raw_item_code)

        if key not in summary_data:
            summary_data[key] = {
                'work_order': work_order,
                'item_code': raw_item_code,  # RAW ITEM
                'finished_item_code': finished_item_code,
                'wo_qty': ret.wo_qty,
                'uom': ret.uom,
                'sent_qty': 0,
                'return_qty': 0,
                'received_qty': 0
            }

        summary_data[key]['return_qty'] += flt(ret.return_qty)
        print(f"Added return_qty {flt(ret.return_qty)} for raw item {raw_item_code}")

    # Process Received Details - Convert finished goods to raw material equivalent
    # and distribute proportionally to all raw materials for that work order
    for received in doc.work_order_received_details:
        work_order = received.work_order
        finished_item_code = received.item_code
        received_qty = flt(received.received_qty)
        
        # Skip if item_code is None
        if not finished_item_code:
            print(f"Skipping received item - no item_code")
            continue
        
        # Get the raw items for this work order
        if work_order not in finished_to_raw:
            print(f"Work Order {work_order} not found in finished_to_raw mapping")
            continue
        
        raw_items = finished_to_raw[work_order]['raw_items']
        
        if not raw_items:
            print(f"No raw items found for Work Order {work_order}")
            continue
        
        # Calculate total sent qty for proportional distribution
        total_sent_qty = 0
        raw_item_sent_map = {}
        
        for raw_item in raw_items:
            key = (work_order, raw_item)
            if key in summary_data:
                sent_qty = summary_data[key]['sent_qty']
                raw_item_sent_map[raw_item] = sent_qty
                total_sent_qty += sent_qty
        
        # Distribute received qty proportionally to raw materials based on sent qty
        if total_sent_qty > 0:
            for raw_item, sent_qty in raw_item_sent_map.items():
                key = (work_order, raw_item)
                if key in summary_data:
                    # Proportional distribution
                    proportion = sent_qty / total_sent_qty
                    proportional_received_qty = received_qty * proportion
                    summary_data[key]['received_qty'] += proportional_received_qty
                    print(f"Added received_qty {proportional_received_qty} to raw item {raw_item} (proportion: {proportion:.2%})")

    # Calculate Process Loss for each raw item
    for key, data in summary_data.items():
        sent_qty = flt(data['sent_qty'])
        return_qty = flt(data['return_qty'])
        received_qty = flt(data['received_qty'])
        
        # Net material used = Sent - Return
        net_material_used = sent_qty - return_qty
        
        # Process Loss Qty = Net Material Used - Received Qty (converted to raw material equivalent)
        process_loss_qty = net_material_used - received_qty
        
        # Process Loss Percentage
        if net_material_used > 0:
            process_loss_percentage = (process_loss_qty / net_material_used) * 100
        else:
            process_loss_percentage = 0
        
        # Append to summary table
        doc.append("work_order_process_loss_details", {
            "work_order": data['work_order'],
            "item_code": data['item_code'],  # This is now the RAW ITEM
            "wo_qty": data['wo_qty'],
            "uom": data['uom'],
            "sent_qty": sent_qty,
            "return_qty": return_qty,
            "received_qty": received_qty,
            "process_loss_qty": process_loss_qty,
            "process_loss_percentage": round(process_loss_percentage, 2)
        })

    # Sort by work order and item code
    doc.work_order_process_loss_details = sorted(
        doc.work_order_process_loss_details,
        key=lambda x: (x.work_order or '', x.item_code or '')
    )
    
    print(f"\nProcess Loss Summary: {len(doc.work_order_process_loss_details)} items")
    
    return doc