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
            "label": _("Planned Qty"),
            "fieldname": "planned_qty",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("UOM"),
            "fieldname": "uom",
            "width": 80
        },
        # {
        #     "label": _("Need to Plan Qty"),
        #     "fieldname": "need_to_plan_qty",
        #     "fieldtype": "Float",
        #     "width": 120
        # },
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
            "label": _("Work Order"),
            "fieldname": "work_order",
            "fieldtype": "Link",
            "options": "Work Order",
            "width": 150
        },
        {
            "label": _("WO Status"),
            "fieldname": "wo_status",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("WO Date"),
            "fieldname": "wo_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("BOM No"),
            "fieldname": "bom_no",
            "fieldtype": "Link",
            "options": "BOM",
            "width": 120
        },
        {
            "label": _("Company"),
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 120
        },
        {
            "label": _("Qty To Manufacture"),
            "fieldname": "qty_to_manufacture",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("Manufactured Qty"),
            "fieldname": "manufactured_qty",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("Pending Qty"),
            "fieldname": "pending_qty",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("Material Transferred"),
            "fieldname": "material_transferred",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("WO Count"),
            "fieldname": "work_order_count",
            "fieldtype": "Int",
            "width": 80
        },
        # {
        #     "label": _("Total Qty To Manufacture"),
        #     "fieldname": "total_qty_to_manufacture",
        #     "fieldtype": "Float",
        #     "width": 150
        # },
        # {
        #     "label": _("Total Manufactured Qty"),
        #     "fieldname": "total_manufactured_qty",
        #     "fieldtype": "Float",
        #     "width": 150
        # },
        # {
        #     "label": _("Total Pending Qty"),
        #     "fieldname": "total_pending_qty",
        #     "fieldtype": "Float",
        #     "width": 150
        # }
    ]

def get_data(filters):
    """Get and merge plan items with work order data - one row per WO"""
    plan_items_data = get_plan_items_data(filters)
    work_order_data = get_work_order_data(filters)
    
    # Create a dictionary of plan items for quick lookup
    plan_items_lookup = {}
    for item in plan_items_data:
        key = (item['plan_items'], item['plans'], item['item_code'])
        plan_items_lookup[key] = item
    
    # Create detailed data with one row per work order
    detailed_data = []
    
    # Process all work orders
    for wo in work_order_data:
        # Create key using plan_items, plans, and production_item (which should match plans.item_code)
        key = (wo['plan_items'], wo['plans'], wo['production_item'])
        
        # Create base data structure
        row_data = {
            'item_code': wo['production_item'],  # Use production_item as the main item code to match plans
            'item_name': wo.get('item_name', ''),
            'commercial_name': wo.get('commercial_name', ''),
            'color': None,  # Will be filled from plan items if available
            'uom': wo.get('stock_uom', ''),
            'plan_items': wo['plan_items'],
            'plans': wo['plans'],
            'work_order': wo['work_order'],
            'wo_status': wo.get('status', ''),
            'wo_date': wo['planned_start_date'],
            'bom_no': wo.get('bom_no', ''),
            'company': wo.get('company', ''),
            'qty_to_manufacture': wo['qty'],
            'manufactured_qty': wo.get('produced_qty', 0),
            'pending_qty': wo['qty'] - wo.get('produced_qty', 0),
            'material_transferred': wo.get('material_transferred_for_manufacturing', 0),
            'work_order_count': 1,
            'total_qty_to_manufacture': wo['qty'],
            'total_manufactured_qty': wo.get('produced_qty', 0),
            'total_pending_qty': wo['qty'] - wo.get('produced_qty', 0),
            'source_doc_type': 'Work Order'
        }
        
        # If there's a matching plan item, fill in the plan-related fields
        if key in plan_items_lookup:
            plan_item = plan_items_lookup[key]
            row_data.update({
                'item_name': plan_item['item_name'],  # Use plan item name for consistency
                'commercial_name': plan_item['commercial_name'],
                'color': plan_item['color'],
                'planned_qty': plan_item['planned_qty'],
                'need_to_plan_qty': plan_item['need_to_plan_qty'],
                'uom': plan_item['uom']  # Use plan item UOM
            })
        else:
            # If no plan item found, set plan-related fields to 0 or None
            row_data.update({
                'color': None,
                'planned_qty': 0,
                'need_to_plan_qty': 0
            })
        
        detailed_data.append(row_data)
    
    # Also include plan items that don't have any work orders
    for key, plan_item in plan_items_lookup.items():
        # Check if this plan item has any work orders by matching production_item with plans.item_code
        has_wo = any(
            (wo['plan_items'], wo['plans'], wo['production_item']) == key 
            for wo in work_order_data
        )
        
        if not has_wo:
            detailed_data.append({
                'item_code': plan_item['item_code'],
                'item_name': plan_item['item_name'],
                'commercial_name': plan_item['commercial_name'],
                'color': plan_item['color'],
                'planned_qty': plan_item['planned_qty'],
                'uom': plan_item['uom'],
                'need_to_plan_qty': plan_item['need_to_plan_qty'],
                'plan_items': plan_item['plan_items'],
                'plans': plan_item['plans'],
                'work_order': None,
                'wo_status': None,
                'wo_date': None,
                'bom_no': None,
                'company': None,
                'qty_to_manufacture': 0,
                'manufactured_qty': 0,
                'pending_qty': 0,
                'material_transferred': 0,
                'work_order_count': 0,
                'total_qty_to_manufacture': 0,
                'total_manufactured_qty': 0,
                'total_pending_qty': 0,
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
            plans.plan_qty as planned_qty, 
            item.stock_uom as uom,
            plans.plan_qty as need_to_plan_qty, 
            plans.plan_items as plan_items,
            item.item_name
        FROM `tabPlans` AS plans
        JOIN `tabItem` AS item ON item.name = plans.item_code
        JOIN `tabPlan Items` AS pi ON plans.plan_items = pi.name
        WHERE plans.docstatus = 1
        AND plans.purchase_or_manufacture = 'Manufacture'
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

def get_work_order_data(filters):
    """Get work order data matching plans.item_code with work_order.production_item"""
    query = """
        SELECT 
            wo.production_item,
            wo.planned_start_date,
            wo.production_item as item_code,
            item.commercial_name,
            item.item_name,
            wo.stock_uom,
            wo.custom_plans as plans,
            wo.custom_plan_items as plan_items,
            wo.name as work_order,
            wo.status,
            wo.bom_no,
            wo.company,
            wo.qty,
            wo.produced_qty,
            wo.material_transferred_for_manufacturing,
            (wo.qty - IFNULL(wo.produced_qty, 0)) as pending_qty
        FROM `tabWork Order` wo
        JOIN `tabItem` item ON item.name = wo.production_item
        WHERE wo.docstatus = 1
        AND wo.custom_plan_items IS NOT NULL
        AND wo.custom_plan_items != ''
        AND wo.custom_plans IS NOT NULL
        AND wo.custom_plans != ''
        AND wo.production_item IS NOT NULL
        AND wo.production_item != ''
        AND wo.qty > 0
    """

    conditions = []
    filter_values = {}

    if filters.get("from_date"):
        conditions.append("wo.planned_start_date >= %(from_date)s")
        filter_values["from_date"] = filters.get("from_date")
    if filters.get("to_date"):
        conditions.append("wo.planned_start_date <= %(to_date)s")
        filter_values["to_date"] = filters.get("to_date")
    if filters.get("item_code"):
        conditions.append("wo.production_item = %(item_code)s")
        filter_values["item_code"] = filters.get("item_code")
    if filters.get("commercial_name"):
        conditions.append("item.commercial_name = %(commercial_name)s")
        filter_values["commercial_name"] = filters.get("commercial_name")
    if filters.get("plan_items"):
        conditions.append("wo.custom_plan_items = %(plan_items)s")
        filter_values["plan_items"] = filters.get("plan_items")
    if filters.get("plans"):
        conditions.append("wo.custom_plans = %(plans)s")
        filter_values["plans"] = filters.get("plans")
    if filters.get("work_order"):
        conditions.append("wo.name = %(work_order)s")
        filter_values["work_order"] = filters.get("work_order")
    if filters.get("company"):
        conditions.append("wo.company = %(company)s")
        filter_values["company"] = filters.get("company")
    if filters.get("status"):
        conditions.append("wo.status = %(status)s")
        filter_values["status"] = filters.get("status")
    if filters.get("bom_no"):
        conditions.append("wo.bom_no = %(bom_no)s")
        filter_values["bom_no"] = filters.get("bom_no")

    if conditions:
        query += " AND " + " AND ".join(conditions) if "WHERE" in query else " WHERE " + " AND ".join(conditions)

    return frappe.db.sql(query, filter_values, as_dict=1)