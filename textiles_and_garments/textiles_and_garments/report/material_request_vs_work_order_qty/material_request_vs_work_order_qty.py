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
            "label": _("Material Request"),
            "fieldname": "material_request",
            "fieldtype": "Link",
            "options": "Material Request",
            "width": 100,
        },
        {
            "label": _("Commercial Name"),
            "fieldname": "commercial_name",
            "fieldtype": "data",
            "width": 250,
        },
        {
            "label": _("Color"),
            "fieldname": "color",
            "fieldtype": "data",
            "width": 250,
        },
        {
            "label": _("Work Order"),
            "fieldname": "work_order",
            "fieldtype": "Link",
            "options": "Work Order",
            "width": 200,
        },
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 200,
        },
        {
            "label": _("MR Qty"),
            "fieldname": "material_request_qty",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("WO Qty"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("MR Pending Qty"),
            "fieldname": "mr_pending_qty",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("WO Pending Qty"),
            "fieldname": "wo_pending_qty",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("MTM Qty"),
            "fieldname": "material_transferred_for_manufacturing",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("MF Qty"),
            "fieldname": "produced_qty",
            "fieldtype": "Float",
            "width": 90,
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
            "width": 250,
        }
    ]

    return columns

def get_data(filters):
    data = []
    wo_data = get_work_order_data(filters)
    data.extend(wo_data)
    return data

def get_work_order_data(filters):
    query = """
        SELECT 
            mri.parent as material_request,
            wo.name as work_order,
            wo.production_item as item_code,
            wo.custom_commercial_name as commercial_name, 
            wo.custom_color as color, 
            mri.qty as material_request_qty,
            wo.qty, 
            wo.stock_uom as uom,
            wo.material_transferred_for_manufacturing,
            wo.produced_qty,
            (mri.qty - wo.qty) as mr_pending_qty,
            (wo.qty - wo.produced_qty) as wo_pending_qty,
            item.item_name,
            wo.docstatus
        FROM `tabWork Order` AS wo
        JOIN `tabItem` AS item ON item.item_code = wo.production_item
        JOIN `tabMaterial Request Item` AS mri ON mri.parent = wo.material_request
        WHERE wo.docstatus = 1
    """

    conditions = []

    
    if filters.get("item_code"):
        conditions.append("wo.production_item = %(item_code)s")
    if filters.get("commercial_name"):
        conditions.append("wo.custom_commercial_name = %(commercial_name)s")
    if filters.get("color"):
        conditions.append("wo.custom_color = %(color)s")
    if filters.get("docstatus") is not None:
        conditions.append("wo.docstatus = %(docstatus)s")


    # Only add WHERE clause if there are conditions
    if conditions:
        query += " AND " + " AND ".join(conditions)



    filter_values = {
        "item_code": filters.get("finished_item_code") or None,
        "commercial_name": filters.get("commercial_name") or None,
        "color": filters.get("color") or None,
        # "from_date": filters.get("from_date"),
        # "to_date": filters.get("to_date"),
        "docstatus": int(filters.get("docstatus")) if filters.get("docstatus") else None,
    }

    
    return frappe.db.sql(query, filter_values, as_dict=1)
