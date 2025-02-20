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
            "label": _("Delivery Date"),
            "fieldname": "delivery_date",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "label": _("Sales Order"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Sales Order",
            "width": 150,
        },
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 200,
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
            "label": _("Width"),
            "fieldname": "width",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("Delivered Qty"),
            "fieldname": "delivered_qty",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("Pending Qty"),
            "fieldname": "pending_qty",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("Amount"),
            "fieldname": "amount",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("Item Status"),
            "fieldname": "custom_item_status",
            "fieldtype": "Data",
            "width": 70,
        },
        {
            "label": _("UOM"),
            "fieldname": "stock_uom",
            "fieldtype": "Data",
            "width": 70,
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Docstatus"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 70,
        }
    ]

    return columns

def get_data(filters):
    data = []
    sales_data = get_sales_order_data(filters)
    data.extend(sales_data)
    return data

def get_sales_order_data(filters):
    query = """
        SELECT
            soi.item_code AS item_code,
            soi.commercial_name AS commercial_name,
            soi.color AS color,
            soi.width AS width,
            soi.custom_item_status AS custom_item_status,
            soi.qty AS qty,
            soi.rate AS rate,
            soi.amount AS original_amount,
            COALESCE(soi.delivered_qty, 0) AS delivered_qty,
            (soi.qty - COALESCE(soi.delivered_qty, 0)) AS pending_qty,
            ((soi.qty - COALESCE(soi.delivered_qty, 0)) * soi.rate) AS amount,
            soi.stock_uom AS stock_uom,
            so.transaction_date AS posting_date,
            so.customer AS customer,
            so.name AS name,
            so.delivery_date AS delivery_date,
            so.docstatus AS status
        FROM 
            `tabSales Order Item` AS soi
        LEFT JOIN 
            `tabSales Order` AS so
        ON 
            so.name = soi.parent
        WHERE 
            so.docstatus = 1 AND
            (so.name LIKE 'PTMTO%%' OR
            so.name LIKE 'SOJV%%' OR
            so.name LIKE 'SOHO%%')
    """

    # query = """
    #     SELECT
    #         soi.item_code AS item_code,
    #         soi.qty AS qty,
    #         COALESCE(soi.delivered_qty, 0) AS delivered_qty,
    #         (soi.qty - COALESCE(soi.delivered_qty, 0)) AS pending_qty,
    #         soi.stock_uom AS stock_uom,
    #         so.transaction_date AS posting_date,
    #         so.customer AS customer,
    #         so.name AS name,
    #         so.status AS status
    #     FROM 
    #         `tabSales Order Item` AS soi
    #     LEFT JOIN 
    #         `tabSales Order` AS so
    #     ON 
    #         so.name = soi.parent
    #     WHERE 
    #         so.docstatus = 1 AND
    #         (so.name LIKE 'PTMTO%%' OR
    #          so.name LIKE 'SOJV%%' OR
    #          so.name LIKE 'SOHO%%')
    # """

    conditions = []
    
    if filters.get("item_code"):
        conditions.append("soi.item_code = %(item_code)s")
    
    if filters.get("commercial_name"):
        conditions.append("soi.commercial_name = %(commercial_name)s")
    
    if filters.get("color"):
        conditions.append("soi.color = %(color)s")
    
    if filters.get("from_date"):
        conditions.append("so.transaction_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("so.transaction_date <= %(to_date)s")
    
    if filters.get("status"):
        conditions.append("so.status = %(status)s")
    
    if conditions:
        query += " AND " + " AND ".join(conditions)

    filter_values = {
        "item_code": filters.get("item_code"),
        "commercial_name": filters.get("commercial_name"),
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "status": filters.get("status"),
    }
    
    return frappe.db.sql(query, filter_values, as_dict=1)
