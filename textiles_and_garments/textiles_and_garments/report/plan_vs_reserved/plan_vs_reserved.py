# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt


from collections import defaultdict
import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today

def execute(filters=None):
    columns, data = [], []
    data = get_data(filters)
    columns = get_columns(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {
            "label": _("Plan Items"),
            "fieldname": "plans_no",
            "fieldtype": "Link",
            "options": "Plan Items",
            "width": 150,
        },
        {
            "label": _("Process"),
            "fieldname": "operation",
            "fieldtype": "Link",
            "options": "Operation",
            "width": 100,
        },
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 350,
        },
        {
            "label": _("Commercial Name"),
            "fieldname": "commercial_name",
            "fieldtype": "Data",
            "width": 300,
        },
        {
            "label": _("Plan Qty"),
            "fieldname": "plan_qty",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Planned Qty"),
            "fieldname": "planned_qty",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("To Plan Qty"),
            "fieldname": "to_plan_qty",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("UOM"),
            "fieldname": "uom",
            "fieldtype": "Data",
            "width": 70,
        },
        {
            "label": _("Docstatus"),
            "fieldname": "docstatus",
            "fieldtype": "Data",
            "width": 20,
        }
    ]

    return columns

def get_data(filters):
    data = []
    plan_items_data = get_plan_items_data(filters)
    data.extend(plan_items_data)
    return data

def get_plan_items_data(filters):
    query = """
        SELECT 
            pis.parent as plans_no,
            item.custom_operation as operation,
            pis.item_code,
            pis.commercial_name,
            pis.qty as plan_qty,
            pis.planned_qty as planned_qty,
            pis.need_to_plan_qty as to_plan_qty, 
            pis.uom as uom,
            pis.docstatus
        FROM `tabPlan Items Summary` AS pis
        JOIN `tabItem` AS item ON item.item_code = pis.item_code
        WHERE pis.docstatus = 0 or pis.docstatus = 1
    """

    conditions = []

    
    if filters.get("item_code"):
        conditions.append("pis.item_code = %(item_code)s")
    if filters.get("commercial_name"):
        conditions.append("pis.custom_commercial_name = %(commercial_name)s")
    # if filters.get("color"):
    #     conditions.append("pis.custom_color = %(color)s")
    if filters.get("docstatus") is not None:
        conditions.append("mr.docstatus = %(docstatus)s")


    # Only add WHERE clause if there are conditions
    if conditions:
        query += " WHERE " + " AND ".join(conditions)



    filter_values = {
        "item_code": filters.get("item_code") or None,
        "commercial_name": filters.get("commercial_name") or None,
        "docstatus": int(filters.get("docstatus")) if filters.get("docstatus") else None,
    }

    
    return frappe.db.sql(query, filter_values, as_dict=1)


