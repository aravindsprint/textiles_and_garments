# Copyright (c) 2026, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt
import json

class ProjectWiseMRR(Document):
    pass


@frappe.whitelist()
def calculate_process_loss_by_project(doc):
    """
    Main function to fetch data for sent, return, and received details 
    based on projects for both Work Orders and Purchase Orders
    """
    if isinstance(doc, str):
        doc = frappe.get_doc(json.loads(doc))
    
    # Clear existing child table data
    doc.project_wo_sent_details = []
    doc.project_wo_return_details = []
    doc.project_wo_received_details = []
    doc.project_po_sent_details = []
    doc.project_po_return_details = []
    doc.project_po_received_details = []
    
    # Get all projects from the Projects child table
    projects = [row.project for row in doc.projects if row.project]
    
    if not projects:
        frappe.msgprint(_("No Projects found to calculate process loss"))
        return doc
    
    print(f"\n\n=== Processing Projects: {projects} ===\n")
    
    # ========== WORK ORDER PROCESSING ==========
    print("\n=== WORK ORDER PROCESSING ===")
    fetch_wo_sent_details_by_project(doc, projects)
    fetch_wo_return_details_by_project(doc, projects)
    fetch_wo_received_details_by_project(doc, projects)
    
    # ========== PURCHASE ORDER PROCESSING ==========
    print("\n=== PURCHASE ORDER PROCESSING ===")
    fetch_po_sent_details_by_project(doc, projects)
    fetch_po_return_details_by_project(doc, projects)
    fetch_po_received_details_by_project(doc, projects)
    
    return doc


# ============================================================================
# WORK ORDER FUNCTIONS
# ============================================================================

def fetch_wo_sent_details_by_project(doc, projects):
    """
    Fetch material sent to work orders filtered by project
    """
    stock_entries = frappe.db.sql("""
        SELECT 
            se.name as stock_entry,
            se.work_order,
            wo.project,
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
            AND wo.project IN %(projects)s
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
            se.name,
            wo.project
        ORDER BY
            se.posting_date, se.posting_time
    """, {"projects": projects}, as_dict=1)
    
    print(f"\nWork Order Sent Details found: {len(stock_entries)}")
    
    for entry in stock_entries:
        doc.append("project_wo_sent_details", {
            "project": entry.project,
            "work_order": entry.work_order,
            "stock_entry": entry.stock_entry,
            "item_code": entry.item_code,
            "wo_item_code": entry.wo_item_code,
            "wo_qty": entry.wo_qty,
            "sent_qty": entry.sent_qty,
            "uom": entry.uom
        })


def fetch_wo_return_details_by_project(doc, projects):
    """
    Fetch material returned from work orders filtered by project
    """
    stock_entries = frappe.db.sql("""
        SELECT 
            se.name as stock_entry,
            se.work_order,
            wo.project,
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
            AND wo.project IN %(projects)s
            AND (se.naming_series LIKE 'YRET%%' OR se.naming_series LIKE 'MT%%')
            AND sed.s_warehouse IS NOT NULL
            AND sed.t_warehouse IS NOT NULL
            AND sed.s_warehouse = wo.wip_warehouse
        GROUP BY
            se.work_order,
            sed.item_code,
            se.name,
            wo.project
        ORDER BY
            se.posting_date, se.posting_time
    """, {"projects": projects}, as_dict=1)
    
    print(f"\nWork Order Return Details found: {len(stock_entries)}")
    
    for entry in stock_entries:
        doc.append("project_wo_return_details", {
            "project": entry.project,
            "work_order": entry.work_order,
            "stock_entry": entry.stock_entry,
            "item_code": entry.item_code,
            "wo_item_code": entry.wo_item_code,
            "wo_qty": entry.wo_qty,
            "return_qty": entry.return_qty,
            "uom": entry.uom
        })


def fetch_wo_received_details_by_project(doc, projects):
    """
    Fetch finished goods received from work orders filtered by project
    """
    stock_entries = frappe.db.sql("""
        SELECT 
            se.name as stock_entry,
            se.work_order,
            wo.project,
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
            AND wo.project IN %(projects)s
            AND se.purpose = 'Manufacture'
            AND sed.is_finished_item = 1
            AND sed.t_warehouse IS NOT NULL
        GROUP BY
            se.work_order,
            sed.item_code,
            se.name,
            wo.project
        ORDER BY
            se.posting_date, se.posting_time
    """, {"projects": projects}, as_dict=1)
    
    print(f"\nWork Order Received Details found: {len(stock_entries)}")
    
    for entry in stock_entries:
        doc.append("project_wo_received_details", {
            "project": entry.project,
            "work_order": entry.work_order,
            "stock_entry": entry.stock_entry,
            "item_code": entry.item_code,
            "wo_qty": entry.wo_qty,
            "received_qty": entry.received_qty,
            "uom": entry.uom
        })


# ============================================================================
# PURCHASE ORDER FUNCTIONS
# ============================================================================

def fetch_po_sent_details_by_project(doc, projects):
    """
    Fetch material sent to subcontracting orders filtered by project
    """
    # Get Subcontracting Orders for the projects
    sco_list = frappe.db.sql("""
        SELECT 
            sco.name,
            sco.purchase_order,
            po.project
        FROM 
            `tabSubcontracting Order` sco
        INNER JOIN
            `tabPurchase Order` po ON sco.purchase_order = po.name
        WHERE 
            sco.docstatus = 1
            AND po.project IN %(projects)s
    """, {"projects": projects}, as_dict=1)
    
    if not sco_list:
        print("\nNo Subcontracting Orders found for the projects")
        return
    
    sco_names = [sco['name'] for sco in sco_list]
    sco_to_project_map = {sco['name']: sco['project'] for sco in sco_list}
    sco_to_po_map = {sco['name']: sco['purchase_order'] for sco in sco_list}
    
    print(f"\nSubcontracting Orders found: {len(sco_list)}")
    
    # Get Stock Entries for these SCOs
    stock_entries = frappe.db.sql("""
        SELECT 
            se.name as stock_entry,
            se.subcontracting_order,
            sed.item_code,
            sed.sco_rm_detail,
            SUM(sed.qty) as sent_qty,
            sed.uom
        FROM 
            `tabStock Entry` se
        INNER JOIN 
            `tabStock Entry Detail` sed ON se.name = sed.parent
        WHERE 
            se.docstatus = 1
            AND se.subcontracting_order IN %(sco_names)s
            AND se.purpose = 'Send to Subcontractor'
            AND (se.naming_series LIKE 'ST%%' OR se.naming_series LIKE 'YEI%%' OR se.naming_series LIKE 'DTS%%')
        GROUP BY
            se.subcontracting_order,
            sed.item_code,
            se.name
        ORDER BY
            se.posting_date, se.posting_time
    """, {"sco_names": sco_names}, as_dict=1)
    
    # Get SCO Supplied Items for main_item_code mapping
    sco_supplied_items = frappe.db.sql("""
        SELECT 
            parent as subcontracting_order,
            rm_item_code as item_code,
            main_item_code,
            name,
            required_qty as po_qty
        FROM 
            `tabSubcontracting Order Supplied Item`
        WHERE 
            parent IN %(sco_names)s
    """, {"sco_names": sco_names}, as_dict=1)
    
    # Create mapping for main_item_code
    sco_item_map = {}
    for item in sco_supplied_items:
        key = (item['subcontracting_order'], item['item_code'])
        sco_item_map[key] = {
            'main_item_code': item.get('main_item_code', ''),
            'po_qty': item.get('po_qty', 0)
        }
    
    print(f"\nPO Sent Details (Stock Entries) found: {len(stock_entries)}")
    
    for entry in stock_entries:
        sco_name = entry.subcontracting_order
        project = sco_to_project_map.get(sco_name)
        purchase_order = sco_to_po_map.get(sco_name)
        
        # Get main_item_code from mapping
        key = (sco_name, entry.item_code)
        item_info = sco_item_map.get(key, {})
        
        # Skip DYES% and CHEM% items
        if entry.item_code and (entry.item_code.startswith("DYES") or entry.item_code.startswith("CHEM")):
            continue
        
        doc.append("project_po_sent_details", {
            "project": project,
            "purchase_order": purchase_order,
            "subcontracting_order": sco_name,
            "stock_entry": entry.stock_entry,
            "item_code": entry.item_code,
            "po_item_code": item_info.get('main_item_code', ''),
            "po_qty": item_info.get('po_qty', 0),
            "sent_qty": entry.sent_qty,
            "uom": entry.uom
        })


def fetch_po_return_details_by_project(doc, projects):
    """
    Fetch material returned from subcontracting orders filtered by project
    """
    # Get Subcontracting Orders with supplier warehouses
    sco_list = frappe.db.sql("""
        SELECT 
            sco.name,
            sco.purchase_order,
            sco.supplier_warehouse,
            po.project
        FROM 
            `tabSubcontracting Order` sco
        INNER JOIN
            `tabPurchase Order` po ON sco.purchase_order = po.name
        WHERE 
            sco.docstatus = 1
            AND po.project IN %(projects)s
            AND sco.supplier_warehouse IS NOT NULL
    """, {"projects": projects}, as_dict=1)
    
    if not sco_list:
        print("\nNo Subcontracting Orders found for return details")
        return
    
    sco_names = [sco['name'] for sco in sco_list]
    supplier_warehouses = [sco['supplier_warehouse'] for sco in sco_list]
    sco_to_project_map = {sco['name']: sco['project'] for sco in sco_list}
    sco_to_po_map = {sco['name']: sco['purchase_order'] for sco in sco_list}
    
    print(f"\nSubcontracting Orders for return: {len(sco_list)}")
    
    # Get Return Stock Entries
    stock_entries = frappe.db.sql("""
        SELECT DISTINCT
            se.name as stock_entry,
            se.subcontracting_order,
            sed.item_code,
            SUM(sed.qty) as return_qty,
            sed.uom
        FROM 
            `tabStock Entry` se
        INNER JOIN 
            `tabStock Entry Detail` sed ON se.name = sed.parent
        WHERE 
            se.docstatus = 1
            AND se.subcontracting_order IN %(sco_names)s
            AND se.purpose = 'Material Transfer'
            AND sed.s_warehouse IN %(supplier_warehouses)s
        GROUP BY
            se.subcontracting_order,
            sed.item_code,
            se.name
        ORDER BY
            se.posting_date, se.posting_time
    """, {"sco_names": sco_names, "supplier_warehouses": supplier_warehouses}, as_dict=1)
    
    # Get SCO Supplied Items for main_item_code mapping
    sco_supplied_items = frappe.db.sql("""
        SELECT 
            parent as subcontracting_order,
            rm_item_code as item_code,
            main_item_code,
            required_qty as po_qty
        FROM 
            `tabSubcontracting Order Supplied Item`
        WHERE 
            parent IN %(sco_names)s
    """, {"sco_names": sco_names}, as_dict=1)
    
    # Create mapping
    sco_item_map = {}
    for item in sco_supplied_items:
        key = (item['subcontracting_order'], item['item_code'])
        sco_item_map[key] = {
            'main_item_code': item.get('main_item_code', ''),
            'po_qty': item.get('po_qty', 0)
        }
    
    print(f"\nPO Return Details found: {len(stock_entries)}")
    
    for entry in stock_entries:
        sco_name = entry.subcontracting_order
        project = sco_to_project_map.get(sco_name)
        purchase_order = sco_to_po_map.get(sco_name)
        
        # Get main_item_code from mapping
        key = (sco_name, entry.item_code)
        item_info = sco_item_map.get(key, {})
        
        # Skip DYES% and CHEM% items
        if entry.item_code and (entry.item_code.startswith("DYES") or entry.item_code.startswith("CHEM")):
            continue
        
        doc.append("project_po_return_details", {
            "project": project,
            "purchase_order": purchase_order,
            "subcontracting_order": sco_name,
            "stock_entry": entry.stock_entry,
            "item_code": entry.item_code,
            "po_item_code": item_info.get('main_item_code', ''),
            "po_qty": item_info.get('po_qty', 0),
            "return_qty": entry.return_qty,
            "uom": entry.uom
        })


def fetch_po_received_details_by_project(doc, projects):
    """
    Fetch finished goods received from subcontracting orders filtered by project
    """
    # Get Subcontracting Orders
    sco_list = frappe.db.sql("""
        SELECT 
            sco.name,
            sco.purchase_order,
            po.project
        FROM 
            `tabSubcontracting Order` sco
        INNER JOIN
            `tabPurchase Order` po ON sco.purchase_order = po.name
        WHERE 
            sco.docstatus = 1
            AND po.project IN %(projects)s
    """, {"projects": projects}, as_dict=1)
    
    if not sco_list:
        print("\nNo Subcontracting Orders found for received details")
        return
    
    sco_names = [sco['name'] for sco in sco_list]
    sco_to_project_map = {sco['name']: sco['project'] for sco in sco_list}
    sco_to_po_map = {sco['name']: sco['purchase_order'] for sco in sco_list}
    
    print(f"\nSubcontracting Orders for received: {len(sco_list)}")
    
    # Get Subcontracting Receipt Items
    receipt_items = frappe.db.sql("""
        SELECT 
            sri.parent as subcontracting_receipt,
            sri.subcontracting_order,
            sri.item_code,
            SUM(sri.qty) as received_qty,
            sri.stock_uom as uom
        FROM 
            `tabSubcontracting Receipt Item` sri
        INNER JOIN 
            `tabSubcontracting Receipt` sr ON sri.parent = sr.name
        WHERE 
            sri.subcontracting_order IN %(sco_names)s
            AND sr.docstatus = 1
        GROUP BY
            sri.subcontracting_order,
            sri.item_code,
            sri.parent
        ORDER BY
            sr.posting_date
    """, {"sco_names": sco_names}, as_dict=1)
    
    # Get SCO Items for po_qty
    sco_items = frappe.db.sql("""
        SELECT 
            parent as subcontracting_order,
            item_code,
            qty as po_qty
        FROM 
            `tabSubcontracting Order Item`
        WHERE 
            parent IN %(sco_names)s
    """, {"sco_names": sco_names}, as_dict=1)
    
    # Create mapping for po_qty
    po_qty_map = {}
    for item in sco_items:
        key = (item['subcontracting_order'], item['item_code'])
        po_qty_map[key] = item.get('po_qty', 0)
    
    print(f"\nPO Received Details found: {len(receipt_items)}")
    
    for entry in receipt_items:
        sco_name = entry.subcontracting_order
        project = sco_to_project_map.get(sco_name)
        purchase_order = sco_to_po_map.get(sco_name)
        
        # Get po_qty from mapping
        key = (sco_name, entry.item_code)
        po_qty = po_qty_map.get(key, 0)
        
        doc.append("project_po_received_details", {
            "project": project,
            "purchase_order": purchase_order,
            "subcontracting_order": sco_name,
            "subcontracting_receipt": entry.subcontracting_receipt,
            "item_code": entry.item_code,
            "po_qty": po_qty,
            "received_qty": entry.received_qty,
            "uom": entry.uom
        })


# ============================================================================
# SUMMARY CALCULATION FUNCTIONS
# ============================================================================

@frappe.whitelist()
def calculate_wo_summary_by_project(doc):
    """
    Calculate Work Order process loss summary by project
    Similar to WorkOrderProcessLoss calculate_summary
    """
    if isinstance(doc, str):
        doc = frappe.get_doc(json.loads(doc))
    
    # Clear existing summary
    doc.project_wo_process_loss_details = []
    
    # Get unique projects and work orders
    projects = list(set([row.project for row in doc.projects if row.project]))
    
    if not projects:
        frappe.msgprint(_("No Projects found"))
        return doc
    
    # Get all work orders from sent details
    work_order_list = list(set([row.work_order for row in doc.project_wo_sent_details if row.work_order]))
    
    if not work_order_list:
        print("No Work Orders found in sent details")
        return doc
    
    # Check if GKF work order (similar logic as original)
    is_gkf_work_order = False
    gkf_stock_uom = None
    
    if doc.project_wo_sent_details and len(doc.project_wo_sent_details) > 0:
        first_wo_name = doc.project_wo_sent_details[0].work_order
        if first_wo_name:
            production_item, stock_uom = frappe.db.get_value(
                "Work Order", 
                first_wo_name, 
                ["production_item", "stock_uom"]
            )
            
            if production_item and production_item.startswith("GKF") and stock_uom == "Pcs":
                is_gkf_work_order = True
                gkf_stock_uom = stock_uom
                print(f"GKF Work Order detected for project-wise processing")
    
    # Get item mapping
    wo_item_mapping = get_work_order_item_mapping(work_order_list)
    finished_to_raw = get_finished_to_raw_mapping(work_order_list)
    
    # Dictionary to aggregate data by (project, work_order, raw_item)
    summary_data = {}
    
    # Process Sent Details
    for sent in doc.project_wo_sent_details:
        project = sent.project
        work_order = sent.work_order
        raw_item_code = sent.item_code
        
        if work_order not in wo_item_mapping:
            continue
        
        finished_item_code = wo_item_mapping[work_order]['finished_item']
        
        if raw_item_code not in wo_item_mapping[work_order]['raw_items']:
            if not (raw_item_code and (raw_item_code.startswith("DYES") or raw_item_code.startswith("CHEM"))):
                print(f"Skipping sent item: {raw_item_code} - not in required items")
            continue
        
        if raw_item_code and (raw_item_code.startswith("DYES") or raw_item_code.startswith("CHEM")):
            continue
        
        key = (project, work_order, raw_item_code)
        
        if key not in summary_data:
            summary_data[key] = {
                'project': project,
                'work_order': work_order,
                'item_code': raw_item_code,
                'finished_item_code': finished_item_code,
                'wo_qty': sent.wo_qty,
                'uom': sent.uom,
                'sent_qty': 0,
                'return_qty': 0,
                'received_qty': 0
            }
        
        summary_data[key]['sent_qty'] += flt(sent.sent_qty)
    
    # Process Return Details
    for ret in doc.project_wo_return_details:
        project = ret.project
        work_order = ret.work_order
        raw_item_code = ret.item_code
        
        if work_order not in wo_item_mapping:
            continue
        
        finished_item_code = wo_item_mapping[work_order]['finished_item']
        
        if raw_item_code not in wo_item_mapping[work_order]['raw_items']:
            if not (raw_item_code and (raw_item_code.startswith("DYES") or raw_item_code.startswith("CHEM"))):
                print(f"Skipping return item: {raw_item_code} - not in required items")
            continue
        
        if raw_item_code and (raw_item_code.startswith("DYES") or raw_item_code.startswith("CHEM")):
            continue
        
        key = (project, work_order, raw_item_code)
        
        if key not in summary_data:
            summary_data[key] = {
                'project': project,
                'work_order': work_order,
                'item_code': raw_item_code,
                'finished_item_code': finished_item_code,
                'wo_qty': ret.wo_qty,
                'uom': ret.uom,
                'sent_qty': 0,
                'return_qty': 0,
                'received_qty': 0
            }
        
        summary_data[key]['return_qty'] += flt(ret.return_qty)
    
    # Process Received Details
    if is_gkf_work_order:
        # GKF logic - use consumed_qty
        print("\n=== GKF Work Order - Using consumed_qty ===")
        
        for work_order in work_order_list:
            required_items = frappe.db.sql("""
                SELECT 
                    item_code,
                    required_qty,
                    consumed_qty,
                    stock_uom
                FROM 
                    `tabWork Order Item`
                WHERE 
                    parent = %s
            """, (work_order), as_dict=1)
            
            # Get project for this work order
            project = frappe.db.get_value("Work Order", work_order, "project")
            
            for item in required_items:
                raw_item_code = item['item_code']
                
                if raw_item_code and (raw_item_code.startswith("DYES") or raw_item_code.startswith("CHEM")):
                    continue
                
                key = (project, work_order, raw_item_code)
                
                if key in summary_data:
                    summary_data[key]['wo_qty'] = flt(item['required_qty'])
                    summary_data[key]['received_qty'] = flt(item['consumed_qty'])
                else:
                    if work_order in wo_item_mapping:
                        finished_item_code = wo_item_mapping[work_order]['finished_item']
                        summary_data[key] = {
                            'project': project,
                            'work_order': work_order,
                            'item_code': raw_item_code,
                            'finished_item_code': finished_item_code,
                            'wo_qty': flt(item['required_qty']),
                            'uom': item['stock_uom'],
                            'sent_qty': 0,
                            'return_qty': 0,
                            'received_qty': flt(item['consumed_qty'])
                        }
    else:
        # Non-GKF logic - proportional distribution
        print("\n=== Non-GKF Work Order - Proportional distribution ===")
        
        for received in doc.project_wo_received_details:
            project = received.project
            work_order = received.work_order
            finished_item_code = received.item_code
            received_qty = flt(received.received_qty)
            
            if not finished_item_code or work_order not in finished_to_raw:
                continue
            
            raw_items = finished_to_raw[work_order]['raw_items']
            
            if not raw_items:
                continue
            
            # Calculate proportional distribution
            total_sent_qty = 0
            raw_item_sent_map = {}
            
            for raw_item in raw_items:
                key = (project, work_order, raw_item)
                if key in summary_data:
                    sent_qty = summary_data[key]['sent_qty']
                    raw_item_sent_map[raw_item] = sent_qty
                    total_sent_qty += sent_qty
            
            if total_sent_qty > 0:
                for raw_item, sent_qty in raw_item_sent_map.items():
                    key = (project, work_order, raw_item)
                    if key in summary_data:
                        proportion = sent_qty / total_sent_qty
                        proportional_received_qty = received_qty * proportion
                        summary_data[key]['received_qty'] += proportional_received_qty
    
    # Calculate process loss
    for key, data in summary_data.items():
        sent_qty = flt(data['sent_qty'])
        return_qty = flt(data['return_qty'])
        received_qty = flt(data['received_qty'])
        
        net_material_used = sent_qty - return_qty
        process_loss_qty = net_material_used - received_qty
        
        if net_material_used > 0:
            process_loss_percentage = (process_loss_qty / net_material_used) * 100
        else:
            process_loss_percentage = 0
        
        doc.append("project_wo_process_loss_details", {
            "project": data['project'],
            "work_order": data['work_order'],
            "item_code": data['item_code'],
            "wo_qty": data['wo_qty'],
            "uom": data['uom'],
            "sent_qty": sent_qty,
            "return_qty": return_qty,
            "received_qty": received_qty,
            "process_loss_qty": process_loss_qty,
            "process_loss_percentage": round(process_loss_percentage, 2)
        })
    
    # Sort by project, work order, and item code
    doc.project_wo_process_loss_details = sorted(
        doc.project_wo_process_loss_details,
        key=lambda x: (x.project or '', x.work_order or '', x.item_code or '')
    )
    
    print(f"\nWO Process Loss Summary: {len(doc.project_wo_process_loss_details)} items")
    
    return doc


@frappe.whitelist()
def calculate_po_summary_by_project(doc):
    """
    Calculate Purchase Order process loss summary by project
    Similar to ProcessLoss calculate_summary
    """
    if isinstance(doc, str):
        doc = frappe.get_doc(json.loads(doc))
    
    # Clear existing summary
    doc.project_po_process_loss_details = []
    
    # Get conversion factors
    collar_avg_weight = flt(doc.get("collar_avg_weight", 0))
    cuff_avg_weight = flt(doc.get("cuff_avg_weight", 0))
    
    # Dictionary to aggregate data by (project, purchase_order, subcontracting_order, finished_item)
    summary_data = {}
    
    # Create main item mapping
    main_item_mapping = {}
    for sent_item in doc.project_po_sent_details:
        main_item_code = sent_item.get("po_item_code")
        raw_item_code = sent_item.get("item_code")
        
        if main_item_code and main_item_code not in main_item_mapping:
            main_item_mapping[main_item_code] = {
                "raw_item_code": raw_item_code,
                "sent_uom": sent_item.get("uom"),
                "po_qty": sent_item.get("po_qty", 0)
            }
    
    # Process Sent Details
    for sent_item in doc.project_po_sent_details:
        project = sent_item.project
        main_item_code = sent_item.get("po_item_code")
        raw_item_code = sent_item.get("item_code")
        
        if not main_item_code:
            continue
        
        if raw_item_code and (raw_item_code.startswith("DYES") or raw_item_code.startswith("CHEM")):
            continue
        
        key = (
            project,
            sent_item.get("purchase_order"),
            sent_item.get("subcontracting_order"),
            main_item_code
        )
        
        if key not in summary_data:
            summary_data[key] = {
                "project": project,
                "purchase_order": sent_item.get("purchase_order"),
                "subcontracting_order": sent_item.get("subcontracting_order"),
                "item_code": main_item_code,
                "raw_item_code": raw_item_code,
                "uom": "",
                "po_qty": 0,
                "sent_qty": 0,
                "return_qty": 0,
                "received_qty": 0,
                "sent_uom": sent_item.get("uom"),
                "is_converted": False
            }
        
        summary_data[key]["sent_qty"] += flt(sent_item.get("sent_qty", 0))
    
    # Process Return Details
    for return_item in doc.project_po_return_details:
        project = return_item.project
        main_item_code = return_item.get("po_item_code")
        raw_item_code = return_item.get("item_code")
        
        if not main_item_code:
            continue
        
        if raw_item_code and (raw_item_code.startswith("DYES") or raw_item_code.startswith("CHEM")):
            continue
        
        key = (
            project,
            return_item.get("purchase_order"),
            return_item.get("subcontracting_order"),
            main_item_code
        )
        
        if key not in summary_data:
            raw_mapping = main_item_mapping.get(main_item_code, {})
            summary_data[key] = {
                "project": project,
                "purchase_order": return_item.get("purchase_order"),
                "subcontracting_order": return_item.get("subcontracting_order"),
                "item_code": main_item_code,
                "raw_item_code": raw_mapping.get("raw_item_code", raw_item_code),
                "uom": "",
                "po_qty": 0,
                "sent_qty": 0,
                "return_qty": 0,
                "received_qty": 0,
                "sent_uom": raw_mapping.get("sent_uom", ""),
                "is_converted": False
            }
        
        summary_data[key]["return_qty"] += flt(return_item.get("return_qty", 0))
    
    # Process Received Details
    for received_item in doc.project_po_received_details:
        project = received_item.project
        main_item_code = received_item.get("item_code")
        
        if not main_item_code:
            continue
        
        key = (
            project,
            received_item.get("purchase_order"),
            received_item.get("subcontracting_order"),
            main_item_code
        )
        
        if key not in summary_data:
            raw_mapping = main_item_mapping.get(main_item_code, {})
            summary_data[key] = {
                "project": project,
                "purchase_order": received_item.get("purchase_order"),
                "subcontracting_order": received_item.get("subcontracting_order"),
                "item_code": main_item_code,
                "raw_item_code": raw_mapping.get("raw_item_code", ""),
                "uom": received_item.get("uom"),
                "po_qty": flt(received_item.get("po_qty", 0)),
                "sent_qty": 0,
                "return_qty": 0,
                "received_qty": 0,
                "sent_uom": raw_mapping.get("sent_uom", ""),
                "is_converted": False
            }
        else:
            summary_data[key]["uom"] = received_item.get("uom")
            summary_data[key]["po_qty"] = flt(received_item.get("po_qty", 0))
        
        summary_data[key]["received_qty"] += flt(received_item.get("received_qty", 0))
    
    # Convert Sent Qty if required
    for key, data in summary_data.items():
        if data["sent_uom"] in ["Kg", "Kgs"] and data["uom"] in ["Pcs", "Nos"]:
            item_code = data["item_code"]
            item_type = get_item_type(item_code)
            
            conversion_factor = 1
            if item_type == "Collar" and collar_avg_weight > 0:
                conversion_factor = collar_avg_weight
            elif item_type == "Cuff" and cuff_avg_weight > 0:
                conversion_factor = cuff_avg_weight
            
            if conversion_factor > 0 and conversion_factor != 1:
                original_sent_qty = data["sent_qty"]
                data["sent_qty"] = original_sent_qty / conversion_factor
                data["is_converted"] = True
    
    # Calculate Process Loss
    for key, data in summary_data.items():
        process_loss_qty = flt(data["sent_qty"]) - flt(data["return_qty"]) - flt(data["received_qty"])
        process_loss_percentage = 0
        if data["sent_qty"] > 0:
            process_loss_percentage = (process_loss_qty / data["sent_qty"]) * 100
        
        doc.append("project_po_process_loss_details", {
            "project": data["project"],
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
    
    # Sort by project, purchase order, and item code
    doc.project_po_process_loss_details = sorted(
        doc.project_po_process_loss_details,
        key=lambda x: (x.project or '', x.purchase_order or '', x.item_code or '')
    )
    
    print(f"\nPO Process Loss Summary: {len(doc.project_po_process_loss_details)} items")
    
    return doc


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_item_type(item_code):
    """Get item type from Item master"""
    try:
        item_doc = frappe.get_doc("Item", item_code)
        return item_doc.get("custom_item_type", "")
    except:
        return ""


def get_work_order_item_mapping(work_order_list):
    """Get mapping of raw materials to finished goods from Work Order"""
    if not work_order_list:
        return {}
    
    work_orders = frappe.db.sql("""
        SELECT name, production_item
        FROM `tabWork Order`
        WHERE name IN %(work_orders)s
    """, {"work_orders": work_order_list}, as_dict=1)
    
    wo_mapping = {}
    
    for wo in work_orders:
        wo_name = wo['name']
        finished_item = wo['production_item']
        
        required_items = frappe.db.sql("""
            SELECT item_code, required_qty
            FROM `tabWork Order Item`
            WHERE parent = %s
        """, (wo_name,), as_dict=1)
        
        wo_mapping[wo_name] = {
            'finished_item': finished_item,
            'raw_items': {}
        }
        
        for item in required_items:
            wo_mapping[wo_name]['raw_items'][item['item_code']] = {
                'finished_item': finished_item,
                'required_qty': item['required_qty']
            }
    
    return wo_mapping


def get_finished_to_raw_mapping(work_order_list):
    """Get reverse mapping from finished goods to raw materials"""
    if not work_order_list:
        return {}
    
    work_orders = frappe.db.sql("""
        SELECT name, production_item
        FROM `tabWork Order`
        WHERE name IN %(work_orders)s
    """, {"work_orders": work_order_list}, as_dict=1)
    
    finished_to_raw = {}
    
    for wo in work_orders:
        wo_name = wo['name']
        finished_item = wo['production_item']
        
        required_items = frappe.db.sql("""
            SELECT item_code, required_qty
            FROM `tabWork Order Item`
            WHERE parent = %s
        """, (wo_name,), as_dict=1)
        
        finished_to_raw[wo_name] = {
            'finished_item': finished_item,
            'raw_items': [item['item_code'] for item in required_items]
        }
    
    return finished_to_raw
