# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    """Main function called by Frappe to execute the report"""
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    """Define report columns"""
    return [
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "width": 150
        },
        {
            "label": _("Commercial Name"),
            "fieldname": "commercial_name",
            "width": 150
        },
        {
            "label": _("Color"),
            "fieldname": "color",
            "width": 100
        },
        {
            "label": _("Quantity"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("UOM"),
            "fieldname": "uom",
            "width": 80
        },
        {
            "label": _("Planned Qty"),
            "fieldname": "planned_qty",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Need to Plan Qty"),
            "fieldname": "need_to_plan_qty",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("Plan Items"),
            "fieldname": "plan_items",
            "fieldtype": "Link",
            "options": "Plan Items",
            "width": 120
        },
        {
            "label": _("PO Count"),
            "fieldname": "purchase_order_count",
            "fieldtype": "Int",
            "width": 80
        },
        {
            "label": _("Total Ordered"),
            "fieldname": "total_ordered",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("Total Received"),
            "fieldname": "total_received",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("Total Pending"),
            "fieldname": "total_pending",
            "fieldtype": "Float",
            "width": 120
        }
    ]

def get_data(filters):
    """Get and merge plan items with purchase order data"""
    plan_items_data = get_plan_items_data(filters)
    purchase_order_data = get_purchase_order_data(filters)
    
    # Create dictionary to group by plan_items and item_code
    merged_data = {}
    
    # Process plan items first
    for item in plan_items_data:
        key = (item['plan_items'], item['item_code'])
        merged_data[key] = {
            'item_code': item['item_code'],
            'posting_date': item['posting_date'],
            'commercial_name': item['commercial_name'],
            'color': item['color'],
            'qty': item['qty'],
            'uom': item['uom'],
            'planned_qty': item['planned_qty'],
            'need_to_plan_qty': item['need_to_plan_qty'],
            'plan_items': item['plan_items'],
            'item_name': item['item_name'],
            'source_doc_type': 'Plan Item',
            'purchase_order_count': 0,
            'total_ordered': 0,
            'total_received': 0,
            'total_pending': 0
        }
    
    # Process purchase orders and merge with plan items
    for po in purchase_order_data:
        key = (po['plan_items'], po['item_code'])
        if key in merged_data:
            merged_data[key]['purchase_order_count'] += 1
            merged_data[key]['total_ordered'] += po['qty']
            merged_data[key]['total_received'] += po['received_qty']
            merged_data[key]['total_pending'] += po['pending_qty']
        else:
            # Handle case where PO exists without plan item
            merged_data[key] = {
                'item_code': po['item_code'],
                'posting_date': po['posting_date'],
                'commercial_name': po['commercial_name'],
                'color': None,
                'qty': 0,
                'uom': po['uom'],
                'planned_qty': 0,
                'need_to_plan_qty': 0,
                'plan_items': po['plan_items'],
                'item_name': po['item_name'],
                'source_doc_type': 'Purchase Order',
                'purchase_order_count': 1,
                'total_ordered': po['qty'],
                'total_received': po['received_qty'],
                'total_pending': po['pending_qty']
            }
    
    return list(merged_data.values())

def get_plan_items_data(filters):
    """Get data from Plan Items Summary table"""
    query = """
        SELECT 
            pis.item_code,
            pi.posting_date, 
            pis.commercial_name,  
            item.color,
            pis.qty, 
            pis.uom,
            pis.planned_qty,
            pis.need_to_plan_qty, 
            pis.parent as plan_items,
            item.item_name
        FROM `tabPlan Items Summary` AS pis
        JOIN `tabItem` AS item ON item.name = pis.item_code
        JOIN `tabPlan Items` AS pi ON pi.name = pis.parent
        WHERE pi.docstatus != 2
    """

    conditions = []
    filter_values = {}

    if filters.get("from_date"):
        conditions.append("pi.posting_date >= %(from_date)s")
        filter_values["from_date"] = filters.get("from_date")
    if filters.get("to_date"):
        conditions.append("pi.posting_date <= %(to_date)s")
        filter_values["to_date"] = filters.get("to_date")
    # if filters.get("plans"):
    #     conditions.append("pis.parent = %(plans)s")
    #     filter_values["plans"] = filters.get("plans")    
    if filters.get("plan_items"):
        conditions.append("pis.parent = %(plan_items)s")
        filter_values["plan_items"] = filters.get("plan_items")
    if filters.get("item_code"):
        conditions.append("pis.item_code = %(item_code)s")
        filter_values["item_code"] = filters.get("item_code")
    if filters.get("commercial_name"):
        conditions.append("pis.custom_commercial_name = %(commercial_name)s")
        filter_values["commercial_name"] = filters.get("commercial_name")
    if filters.get("color"):
        conditions.append("pis.custom_color = %(color)s")
        filter_values["color"] = filters.get("color")
    if filters.get("docstatus") is not None:
        conditions.append("pi.docstatus = %(docstatus)s")
        filter_values["docstatus"] = int(filters.get("docstatus"))

    if conditions:
        query += " AND " + " AND ".join(conditions) if "WHERE" in query else " WHERE " + " AND ".join(conditions)

    return frappe.db.sql(query, filter_values, as_dict=1)

def get_purchase_order_data(filters):
    """Get purchase order data with proper pending quantity calculation"""
    query = """
        SELECT 
            poi.item_code,
            po.transaction_date as posting_date,
            poi.item_name as commercial_name,
            poi.qty,
            poi.uom,
            po.custom_plan_items as plan_items,
            poi.item_name,
            po.name as purchase_order,
            (poi.qty - IFNULL(poi.received_qty, 0)) as pending_qty,
            IFNULL(poi.received_qty, 0) as received_qty
        FROM `tabPurchase Order Item` poi
        JOIN `tabPurchase Order` po ON po.name = poi.parent
        JOIN `tabItem` item ON item.name = poi.item_code
        WHERE po.docstatus = 1
        AND po.custom_plan_items IS NOT NULL
        AND po.custom_plan_items != ''
        AND poi.qty > 0
    """

    conditions = []
    filter_values = {}

    if filters.get("from_date"):
        conditions.append("po.transaction_date >= %(from_date)s")
        filter_values["from_date"] = filters.get("from_date")
    if filters.get("to_date"):
        conditions.append("po.transaction_date <= %(to_date)s")
        filter_values["to_date"] = filters.get("to_date")
    if filters.get("item_code"):
        conditions.append("poi.item_code = %(item_code)s")
        filter_values["item_code"] = filters.get("item_code")
    if filters.get("commercial_name"):
        conditions.append("poi.item_name = %(commercial_name)s")
        filter_values["commercial_name"] = filters.get("commercial_name")
    if filters.get("plan_items"):
        conditions.append("po.custom_plan_items = %(plan_items)s")
        filter_values["plan_items"] = filters.get("plan_items")

    if conditions:
        query += " AND " + " AND ".join(conditions) if "WHERE" in query else " WHERE " + " AND ".join(conditions)

    return frappe.db.sql(query, filter_values, as_dict=1)


