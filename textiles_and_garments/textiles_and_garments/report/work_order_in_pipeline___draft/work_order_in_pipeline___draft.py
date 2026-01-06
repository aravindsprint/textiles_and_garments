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
            "label": _("Work Order"),
            "fieldname": "work_order",
            "fieldtype": "Link",
            "options": "Work Order",
            "width": 150
        },
        {
            "label": _("Production Item"),
            "fieldname": "production_item",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Qty To Manufacture"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("Stock UOM"),
            "fieldname": "stock_uom",
            "fieldtype": "Link",
            "options": "UOM",
            "width": 80
        },
        # {
        #     "label": _("BOM No"),
        #     "fieldname": "bom_no",
        #     "fieldtype": "Link",
        #     "options": "BOM",
        #     "width": 120
        # },
        # {
        #     "label": _("Company"),
        #     "fieldname": "company",
        #     "fieldtype": "Link",
        #     "options": "Company",
        #     "width": 120
        # },
        {
            "label": _("Planned Start Date"),
            "fieldname": "planned_start_date",
            "fieldtype": "Datetime",
            "width": 150
        },
        # {
        #     "label": _("Planned End Date"),
        #     "fieldname": "planned_end_date",
        #     "fieldtype": "Datetime",
        #     "width": 150
        # },
        # {
        #     "label": _("FG Warehouse"),
        #     "fieldname": "fg_warehouse",
        #     "fieldtype": "Link",
        #     "options": "Warehouse",
        #     "width": 120
        # },
        {
            "label": _("WIP Warehouse"),
            "fieldname": "wip_warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 120
        },
        # {
        #     "label": _("Source Warehouse"),
        #     "fieldname": "source_warehouse",
        #     "fieldtype": "Link",
        #     "options": "Warehouse",
        #     "width": 120
        # }
    ]

def get_data(filters):
    """Get Work Orders in Draft state with production_item like GKF%"""
    conditions, filter_values = get_conditions(filters)
    
    query = """
        SELECT 
            wo.name as work_order,
            wo.production_item,
            wo.item_name,
            wo.status,
            wo.qty,
            wo.stock_uom,
            wo.bom_no,
            wo.company,
            wo.planned_start_date,
            wo.planned_end_date,
            wo.fg_warehouse,
            wo.wip_warehouse,
            wo.source_warehouse
        FROM `tabWork Order` wo
        WHERE wo.docstatus = 0
        AND wo.production_item LIKE 'GKF%%'
        {conditions}
        ORDER BY wo.planned_start_date DESC
    """.format(conditions=conditions)
    
    data = frappe.db.sql(query, filter_values, as_dict=1)
    
    return data

def get_conditions(filters):
    """Build filter conditions and return both conditions and filter values"""
    conditions = []
    filter_values = {}
    
    if filters.get("work_order"):
        conditions.append("AND wo.name = %(work_order)s")
        filter_values["work_order"] = filters.get("work_order")
    
    if filters.get("production_item"):
        conditions.append("AND wo.production_item = %(production_item)s")
        filter_values["production_item"] = filters.get("production_item")
    
    if filters.get("company"):
        conditions.append("AND wo.company = %(company)s")
        filter_values["company"] = filters.get("company")
    
    if filters.get("bom_no"):
        conditions.append("AND wo.bom_no = %(bom_no)s")
        filter_values["bom_no"] = filters.get("bom_no")
    
    if filters.get("from_date"):
        conditions.append("AND wo.planned_start_date >= %(from_date)s")
        filter_values["from_date"] = filters.get("from_date")
    
    if filters.get("to_date"):
        conditions.append("AND wo.planned_start_date <= %(to_date)s")
        filter_values["to_date"] = filters.get("to_date")
    
    if filters.get("fg_warehouse"):
        conditions.append("AND wo.fg_warehouse = %(fg_warehouse)s")
        filter_values["fg_warehouse"] = filters.get("fg_warehouse")
    
    if filters.get("wip_warehouse"):
        conditions.append("AND wo.wip_warehouse = %(wip_warehouse)s")
        filter_values["wip_warehouse"] = filters.get("wip_warehouse")
    
    conditions_str = " ".join(conditions) if conditions else ""
    
    return conditions_str, filter_values