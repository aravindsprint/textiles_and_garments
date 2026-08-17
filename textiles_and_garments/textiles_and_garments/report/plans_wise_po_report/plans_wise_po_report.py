# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

# Copyright (c) 2025, Aravind and contributors
# For license information,please see license.txt

# from collections import defaultdict
# import frappe
# from frappe import _
# from frappe.query_builder.functions import Sum
# from frappe.utils import flt, today





# def execute(filters=None):
#     """Main function called by Frappe to execute the report"""
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data

# def get_columns():
#     """Define report columns"""
#     return [
#         {
#             "label": _("Item Code"),
#             "fieldname": "item_code",
#             "fieldtype": "Link",
#             "options": "Item",
#             "width": 120
#         },
#         {
#             "label": _("Item Name"),
#             "fieldname": "item_name",
#             "width": 150
#         },
#         {
#             "label": _("Commercial Name"),
#             "fieldname": "commercial_name",
#             "width": 150
#         },
#         {
#             "label": _("Color"),
#             "fieldname": "color",
#             "width": 100
#         },
#         {
#             "label": _("Quantity"),
#             "fieldname": "qty",
#             "fieldtype": "Float",
#             "width": 100
#         },
#         {
#             "label": _("UOM"),
#             "fieldname": "uom",
#             "width": 80
#         },
#         {
#             "label": _("Planned Qty"),
#             "fieldname": "planned_qty",
#             "fieldtype": "Float",
#             "width": 100
#         },
#         {
#             "label": _("Need to Plan Qty"),
#             "fieldname": "need_to_plan_qty",
#             "fieldtype": "Float",
#             "width": 120
#         },
#         {
#             "label": _("Plan Items"),
#             "fieldname": "plan_items",
#             "fieldtype": "Link",
#             "options": "Plan Items",
#             "width": 120
#         },
#         {
#             "label": _("Plans"),
#             "fieldname": "plans",
#             "fieldtype": "Link",
#             "options": "Plans",
#             "width": 120
#         },
#         {
#             "label": _("PO Count"),
#             "fieldname": "purchase_order_count",
#             "fieldtype": "Int",
#             "width": 80
#         },
#         {
#             "label": _("Total Ordered"),
#             "fieldname": "total_ordered",
#             "fieldtype": "Float",
#             "width": 120
#         },
#         {
#             "label": _("Total Received"),
#             "fieldname": "total_received",
#             "fieldtype": "Float",
#             "width": 120
#         },
#         {
#             "label": _("Total Pending"),
#             "fieldname": "total_pending",
#             "fieldtype": "Float",
#             "width": 120
#         }
#     ]

# def get_data(filters):
#     """Get and merge plan items with purchase order data"""
#     plan_items_data = get_plan_items_data(filters)
#     purchase_order_data = get_purchase_order_data(filters)
    
#     # Create dictionary to group by plan_items and item_code
#     merged_data = {}
    
#     # Process plan items first
#     for item in plan_items_data:
#         key = (item['plan_items'], item['item_code'])
#         merged_data[key] = {
#             'item_code': item['item_code'],
#             'posting_date': item['posting_date'],
#             'commercial_name': item['commercial_name'],
#             'color': item['color'],
#             'qty': item['qty'],
#             'uom': item['uom'],
#             'planned_qty': item['planned_qty'],
#             'need_to_plan_qty': item['need_to_plan_qty'],
#             'plan_items': item['plan_items'],
#             'item_name': item['item_name'],
#             'source_doc_type': 'Plan Item',
#             'purchase_order_count': 0,
#             'total_ordered': 0,
#             'total_received': 0,
#             'total_pending': 0
#         }
    
#     # Process purchase orders and merge with plan items
#     for po in purchase_order_data:
#         key = (po['plan_items'], po['item_code'])
#         if key in merged_data:
#             merged_data[key]['purchase_order_count'] += 1
#             merged_data[key]['total_ordered'] += po['qty']
#             merged_data[key]['total_received'] += po['received_qty']
#             merged_data[key]['total_pending'] += po['pending_qty']
#         else:
#             # Handle case where PO exists without plan item
#             merged_data[key] = {
#                 'item_code': po['item_code'],
#                 'posting_date': po['posting_date'],
#                 'commercial_name': po['commercial_name'],
#                 'color': None,
#                 'qty': 0,
#                 'uom': po['uom'],
#                 'planned_qty': 0,
#                 'need_to_plan_qty': 0,
#                 'plan_items': po['plan_items'],
#                 'item_name': po['item_name'],
#                 'source_doc_type': 'Purchase Order',
#                 'purchase_order_count': 1,
#                 'total_ordered': po['qty'],
#                 'total_received': po['received_qty'],
#                 'total_pending': po['pending_qty']
#             }
    
#     return list(merged_data.values())

# def get_plan_items_data(filters):
#     """Get data from Plan Items Summary table"""
#     query = """
#         SELECT 
#             plans.name as plans,
#             plans.item_code,
#             plans.posting_date, 
#             item.commercial_name,  
#             item.color,
#             plans.plan_qty as qty, 
#             item.stock_uom as uom,
#             plans.plan_qty as planned_qty,
#             plans.plan_qty as need_to_plan_qty, 
#             plans.plan_items as plan_items,
#             item.item_name
#         FROM `tabPlans` AS plans
#         JOIN `tabItem` AS item ON item.name = plans.item_code
#         JOIN `tabPlan Items` AS pi ON plans.plan_items = pi.name
#         WHERE plans.docstatus = 1
#     """

#     conditions = []
#     filter_values = {}

#     if filters.get("from_date"):
#         conditions.append("pi.posting_date >= %(from_date)s")
#         filter_values["from_date"] = filters.get("from_date")
#     if filters.get("to_date"):
#         conditions.append("pi.posting_date <= %(to_date)s")
#         filter_values["to_date"] = filters.get("to_date")
#     if filters.get("plan_items"):
#         conditions.append("pis.parent = %(plan_items)s")
#         filter_values["plan_items"] = filters.get("plan_items")
#     # if filters.get("plans"):
#     #     conditions.append("pis.parent = %(plans)s")
#     #     filter_values["plans"] = filters.get("plans")    
#     if filters.get("item_code"):
#         conditions.append("pis.item_code = %(item_code)s")
#         filter_values["item_code"] = filters.get("item_code")
#     if filters.get("commercial_name"):
#         conditions.append("pis.custom_commercial_name = %(commercial_name)s")
#         filter_values["commercial_name"] = filters.get("commercial_name")
#     if filters.get("color"):
#         conditions.append("pis.custom_color = %(color)s")
#         filter_values["color"] = filters.get("color")
#     if filters.get("docstatus") is not None:
#         conditions.append("pi.docstatus = %(docstatus)s")
#         filter_values["docstatus"] = int(filters.get("docstatus"))

#     if conditions:
#         query += " AND " + " AND ".join(conditions) if "WHERE" in query else " WHERE " + " AND ".join(conditions)

#     return frappe.db.sql(query, filter_values, as_dict=1)

# def get_purchase_order_data(filters):
#     """Get purchase order data with proper pending quantity calculation"""
#     query = """
#         SELECT 
#             poi.item_code,
#             po.transaction_date as posting_date,
#             poi.item_name as commercial_name,
#             poi.qty,
#             poi.uom,
#             poi.custom_plans as plans,
#             po.custom_plan_items as plan_items,
#             poi.item_name,
#             po.name as purchase_order,
#             (poi.qty - IFNULL(poi.received_qty, 0)) as pending_qty,
#             IFNULL(poi.received_qty, 0) as received_qty
#         FROM `tabPurchase Order Item` poi
#         JOIN `tabPurchase Order` po ON po.name = poi.parent
#         JOIN `tabItem` item ON item.name = poi.item_code
#         WHERE po.docstatus = 1
#         AND po.custom_plan_items IS NOT NULL
#         AND po.custom_plan_items != ''
#         AND poi.qty > 0
#     """

#     conditions = []
#     filter_values = {}

#     if filters.get("from_date"):
#         conditions.append("po.transaction_date >= %(from_date)s")
#         filter_values["from_date"] = filters.get("from_date")
#     if filters.get("to_date"):
#         conditions.append("po.transaction_date <= %(to_date)s")
#         filter_values["to_date"] = filters.get("to_date")
#     if filters.get("item_code"):
#         conditions.append("poi.item_code = %(item_code)s")
#         filter_values["item_code"] = filters.get("item_code")
#     if filters.get("commercial_name"):
#         conditions.append("poi.item_name = %(commercial_name)s")
#         filter_values["commercial_name"] = filters.get("commercial_name")
#     if filters.get("plan_items"):
#         conditions.append("po.custom_plan_items = %(plan_items)s")
#         filter_values["plan_items"] = filters.get("plan_items")
#     if filters.get("plans"):
#         conditions.append("poi.custom_plans = %(plans)s")
#         filter_values["plans"] = filters.get("plans")    

#     if conditions:
#         query += " AND " + " AND ".join(conditions) if "WHERE" in query else " WHERE " + " AND ".join(conditions)

#     return frappe.db.sql(query, filter_values, as_dict=1)


# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

from collections import defaultdict
import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today

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
            "label": _("Plans"),
            "fieldname": "plans",
            "fieldtype": "Link",
            "options": "Plans",
            "width": 120
        },
        {
            "label": _("Purchase Order"),
            "fieldname": "purchase_order",
            "fieldtype": "Link",
            "options": "Purchase Order",
            "width": 150
        },
        {
            "label": _("PO Status"),
            "fieldname": "po_status",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("PO Date"),
            "fieldname": "po_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Supplier"),
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 150
        },
        {
            "label": _("Ordered Qty"),
            "fieldname": "ordered_qty",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Received Qty"),
            "fieldname": "received_qty",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Pending Qty"),
            "fieldname": "pending_qty",
            "fieldtype": "Float",
            "width": 100
        }
    ]

def get_data(filters):
    """Get and merge plan items with purchase order data - one row per PO"""
    plan_items_data = get_plan_items_data(filters)
    purchase_order_data = get_purchase_order_data(filters)
    
    # Create a dictionary of plan items for quick lookup
    plan_items_lookup = {}
    for item in plan_items_data:
        key = (item['plan_items'], item['plans'], item['item_code'])
        plan_items_lookup[key] = item
    
    # Create detailed data with one row per purchase order
    detailed_data = []
    
    # Process all purchase orders
    for po in purchase_order_data:
        # Create key using plan_items, plans, and fg_item (which should match plans.item_code)
        key = (po['plan_items'], po['plans'], po['fg_item'])
        
        # Create base data structure
        row_data = {
            'item_code': po['fg_item'],  # Use fg_item as the main item code to match plans
            'item_name': po.get('fg_item_name', ''),
            'commercial_name': po.get('commercial_name', ''),
            'color': None,  # Will be filled from plan items if available
            'uom': po.get('uom', ''),
            'plan_items': po['plan_items'],
            'plans': po['plans'],
            'purchase_order': po['purchase_order'],
            'po_status': po.get('status', ''),
            'po_date': po['posting_date'],
            'supplier': po.get('supplier', ''),
            'ordered_qty': po['qty'],
            'received_qty': po['received_qty'],
            'pending_qty': po['pending_qty'],
            'po_qty_against_plans': po['qty'],
            'source_doc_type': 'Purchase Order'
        }
        
        # If there's a matching plan item, fill in the plan-related fields
        if key in plan_items_lookup:
            plan_item = plan_items_lookup[key]
            row_data.update({
                'item_name': plan_item['item_name'],  # Use plan item name for consistency
                'commercial_name': plan_item['commercial_name'],
                'color': plan_item['color'],
                'qty': plan_item['qty'],
                'uom': plan_item['uom'],  # Use plan item UOM
                'planned_qty': plan_item['planned_qty'],
                'need_to_plan_qty': plan_item['need_to_plan_qty']
            })
        else:
            # If no plan item found, set plan-related fields to 0 or None
            row_data.update({
                'color': None,
                'qty': 0,
                'planned_qty': 0,
                'need_to_plan_qty': 0
            })
        
        detailed_data.append(row_data)
    
    # Also include plan items that don't have any purchase orders
    for key, plan_item in plan_items_lookup.items():
        # Check if this plan item has any purchase orders by matching fg_item with plans.item_code
        has_po = any(
            (po['plan_items'], po['plans'], po['fg_item']) == key 
            for po in purchase_order_data
        )
        
        if not has_po:
            detailed_data.append({
                'item_code': plan_item['item_code'],
                'item_name': plan_item['item_name'],
                'commercial_name': plan_item['commercial_name'],
                'color': plan_item['color'],
                'qty': plan_item['qty'],
                'uom': plan_item['uom'],
                'planned_qty': plan_item['planned_qty'],
                'need_to_plan_qty': plan_item['need_to_plan_qty'],
                'plan_items': plan_item['plan_items'],
                'plans': plan_item['plans'],
                'purchase_order': None,
                'po_status': None,
                'po_date': None,
                'supplier': None,
                'ordered_qty': 0,
                'received_qty': 0,
                'pending_qty': 0,
                'po_qty_against_plans': 0,
                'source_doc_type': 'Plan Item'
            })
    
    return detailed_data

def get_plan_items_data(filters):
    """Get data from Plan Items Summary table"""
    query = """
        SELECT 
            plans.name as plans,
            plans.item_code,
            plans.posting_date, 
            item.commercial_name,  
            item.color,
            plans.plan_qty as qty, 
            item.stock_uom as uom,
            plans.plan_qty as planned_qty,
            plans.plan_qty as need_to_plan_qty, 
            plans.plan_items as plan_items,
            item.item_name
        FROM `tabPlans` AS plans
        JOIN `tabItem` AS item ON item.name = plans.item_code
        JOIN `tabPlan Items` AS pi ON plans.plan_items = pi.name
        WHERE plans.docstatus = 1
    """

    conditions = []
    filter_values = {}

    if filters.get("from_date"):
        conditions.append("pi.posting_date >= %(from_date)s")
        filter_values["from_date"] = filters.get("from_date")
    if filters.get("to_date"):
        conditions.append("pi.posting_date <= %(to_date)s")
        filter_values["to_date"] = filters.get("to_date")
    if filters.get("plan_items"):
        conditions.append("plans.plan_items = %(plan_items)s")
        filter_values["plan_items"] = filters.get("plan_items")
    if filters.get("plans"):
        conditions.append("plans.name = %(plans)s")
        filter_values["plans"] = filters.get("plans")    
    if filters.get("item_code"):
        conditions.append("plans.item_code = %(item_code)s")
        filter_values["item_code"] = filters.get("item_code")
    if filters.get("commercial_name"):
        conditions.append("item.commercial_name = %(commercial_name)s")
        filter_values["commercial_name"] = filters.get("commercial_name")
    if filters.get("color"):
        conditions.append("item.color = %(color)s")
        filter_values["color"] = filters.get("color")
    if filters.get("docstatus") is not None:
        conditions.append("pi.docstatus = %(docstatus)s")
        filter_values["docstatus"] = int(filters.get("docstatus"))

    if conditions:
        query += " AND " + " AND ".join(conditions) if "WHERE" in query else " WHERE " + " AND ".join(conditions)

    return frappe.db.sql(query, filter_values, as_dict=1)

def get_purchase_order_data(filters):
    """Get purchase order data matching plans.item_code with purchase_order_item.fg_item"""
    query = """
        SELECT 
            poi.fg_item,
            po.transaction_date as posting_date,
            fg_item_item.commercial_name,
            fg_item_item.item_name as fg_item_name,
            poi.qty,
            poi.uom,
            poi.custom_plans as plans,
            po.custom_plan_items as plan_items,
            po.name as purchase_order,
            po.status,
            po.supplier,
            (poi.qty - IFNULL(poi.received_qty, 0)) as pending_qty,
            IFNULL(poi.received_qty, 0) as received_qty
        FROM `tabPurchase Order Item` poi
        JOIN `tabPurchase Order` po ON po.name = poi.parent
        JOIN `tabItem` fg_item_item ON fg_item_item.name = poi.fg_item
        WHERE po.docstatus = 1
        AND po.custom_plan_items IS NOT NULL
        AND po.custom_plan_items != ''
        AND poi.custom_plans IS NOT NULL
        AND poi.custom_plans != ''
        AND poi.fg_item IS NOT NULL
        AND poi.fg_item != ''
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
        conditions.append("poi.fg_item = %(item_code)s")
        filter_values["item_code"] = filters.get("item_code")
    if filters.get("commercial_name"):
        conditions.append("fg_item_item.commercial_name = %(commercial_name)s")
        filter_values["commercial_name"] = filters.get("commercial_name")
    if filters.get("plan_items"):
        conditions.append("po.custom_plan_items = %(plan_items)s")
        filter_values["plan_items"] = filters.get("plan_items")
    if filters.get("plans"):
        conditions.append("poi.custom_plans = %(plans)s")
        filter_values["plans"] = filters.get("plans")
    if filters.get("purchase_order"):
        conditions.append("po.name = %(purchase_order)s")
        filter_values["purchase_order"] = filters.get("purchase_order")
    if filters.get("supplier"):
        conditions.append("po.supplier = %(supplier)s")
        filter_values["supplier"] = filters.get("supplier")

    if conditions:
        query += " AND " + " AND ".join(conditions) if "WHERE" in query else " WHERE " + " AND ".join(conditions)

    return frappe.db.sql(query, filter_values, as_dict=1)



