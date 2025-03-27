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
            "label": _("Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "label": _("Process"),
            "fieldname": "process",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Main Indent"),
            "fieldname": "for_project",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Sub Indent"),
            "fieldname": "parent",
            "fieldtype": "Link",
            "options": "Material Request",
            "width": 150,
        },
        {
            "label": _("Commercial Name"),
            "fieldname": "commercial_name",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Color"),
            "fieldname": "color",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": _("Customer"),
            "fieldname": "requested_by",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Customer Group"),
            "fieldname": "customer_group",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Qty"),
            "fieldname": "qty",
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
            "label": _("Item Code"),
            "fieldname": "finished_item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 200,
        },
        {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 250,
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
    sales_data = get_sales_order_data(filters)
    data.extend(sales_data)
    return data

def get_sales_order_data(filters):
    # query = """
    #     SELECT 
    #         mr.date as posting_date,    
    #         CASE 
    #             WHEN mri.finished_item_code LIKE 'G%%' THEN 'Knitting'
    #             WHEN mri.finished_item_code LIKE 'D%%' THEN 'Dyeing'
    #             WHEN mri.finished_item_code LIKE 'S%%' THEN 'Stenter'
    #             WHEN mri.finished_item_code LIKE 'PF%%' THEN 'Peach finish'
    #             WHEN mri.finished_item_code LIKE 'H%%' THEN 'Heat setting'
    #             WHEN mri.finished_item_code LIKE 'WH%%' THEN 'OW Heat setting'
    #             WHEN mri.finished_item_code LIKE 'PK%%' THEN 'Printing'
    #             ELSE 'Unknown' 
    #         END AS process,
    #         mri.for_project, 
    #         mri.parent,  
    #         item.commercial_name, 
    #         item.color, 
    #         mr.requested_by, 
    #         CASE 
    #             WHEN mr.requested_by = 'For Stock' THEN 'STOCK'
    #             ELSE 'MTO' 
    #         END AS customer_group,
    #         mri.qty, 
    #         mri.uom, 
    #         mri.finished_item_code,
    #         item.item_name,
    #         mr.docstatus
    #     FROM `tabMaterial Request` AS mr
    #     JOIN `tabMaterial Request Item` AS mri ON mri.parent = mr.name
    #     JOIN `tabItem` AS item ON item.name = mri.finished_item_code
    # """

    query = """
        SELECT 
            mr.date as posting_date,
            CASE 
                WHEN mri.finished_item_code LIKE 'G%%' THEN 'Knitting'
                WHEN mri.finished_item_code LIKE 'D%%' THEN 'Dyeing'
                WHEN mri.finished_item_code LIKE 'S%%' THEN 'Stenter'
                WHEN mri.finished_item_code LIKE 'PF%%' THEN 'Peach finish'
                WHEN mri.finished_item_code LIKE 'H%%' THEN 'Heat setting'
                WHEN mri.finished_item_code LIKE 'WH%%' THEN 'OW Heat setting'
                WHEN mri.finished_item_code LIKE 'PK%%' THEN 'Printing'
                ELSE 'Unknown' 
            END AS process,
            mri.for_project,
            mri.parent,
            mri.custom_commercial_name as commercial_name, 
            mri.custom_color as color, 
            mr.requested_by, 
            CASE 
                WHEN mr.requested_by = 'For Stock' THEN 'STOCK'
                ELSE 'MTO' 
            END AS customer_group,
            mri.qty, 
            mri.stock_uom,
            mri.finished_item_code,
            item.item_name,
            mr.docstatus
        FROM `tabMaterial Request` AS mr
        JOIN `tabMaterial Request Item` AS mri ON mri.parent = mr.name
        JOIN `tabItem` AS item ON item.name = mri.item_code
    """

    conditions = []

    if filters.get("from_date"):
        conditions.append("mr.date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("mr.date <= %(to_date)s")
    if filters.get("finished_item_code"):
        conditions.append("mri.finished_item_code = %(finished_item_code)s")
    if filters.get("commercial_name"):
        conditions.append("mri.custom_commercial_name = %(commercial_name)s")
    if filters.get("color"):
        conditions.append("mri.custom_color = %(color)s")
    if filters.get("docstatus") is not None:
        conditions.append("mr.docstatus = %(docstatus)s")


    # Only add WHERE clause if there are conditions
    if conditions:
        query += " WHERE " + " AND ".join(conditions)



    filter_values = {
        "finished_item_code": filters.get("finished_item_code") or None,
        "commercial_name": filters.get("commercial_name") or None,
        "color": filters.get("color") or None,
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "docstatus": int(filters.get("docstatus")) if filters.get("docstatus") else None,
    }

    
    return frappe.db.sql(query, filter_values, as_dict=1)


