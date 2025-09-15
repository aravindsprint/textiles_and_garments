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
            "label": _("Sales Person"),
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 100,
        },
        {
            "label": _("Team"),
            "fieldname": "parent_sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 100,
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Data",
            "width": 100,
        },
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
            "label": _("UOM"),
            "fieldname": "stock_uom",
            "fieldtype": "Data",
            "width": 70,
        },
        # {
        #     "label": _("Delivered Qty"),
        #     "fieldname": "delivered_qty",
        #     "fieldtype": "Float",
        #     "width": 90,
        # },
        # {
        #     "label": _("Pending Qty"),
        #     "fieldname": "pending_qty",
        #     "fieldtype": "Float",
        #     "width": 90,
        # },
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
        
        
        # {
        #     "label": _("Delivery status"),
        #     "fieldname": "delivery_status",
        #     "fieldtype": "Data",
        #     "width": 70,
        # }
    ]

    return columns

def get_data(filters):
    data = []
    sales_data = get_sales_order_data(filters)
    data.extend(sales_data)
    return data

def get_sales_order_data(filters):
	# uncomment below for the pranera erpnext
    # query = """
    #     SELECT
    #         soi.item_code AS item_code,
    #         soi.commercial_name AS commercial_name,
    #         soi.color AS color,
    #         soi.width AS width,
    #         soi.custom_item_status AS custom_item_status,
    #         soi.qty AS qty,
    #         soi.rate AS rate,
    #         soi.amount AS original_amount,
    #         COALESCE(soi.delivered_qty, 0) AS delivered_qty,
    #         (soi.qty - COALESCE(soi.delivered_qty, 0)) AS pending_qty,
    #         ((soi.qty - COALESCE(soi.delivered_qty, 0)) * soi.rate) AS amount,
    #         soi.stock_uom AS stock_uom,
    #         so.transaction_date AS posting_date,
    #         so.customer AS customer,
    #         st.sales_person,
    #         so.name AS name,
    #         so.delivery_date AS delivery_date,
    #         so.delivery_status AS delivery_status
    #     FROM 
    #         `tabSales Order Item` AS soi
    #     LEFT JOIN 
    #         `tabSales Order` AS so
    #     ON 
    #         so.name = soi.parent
    #     LEFT JOIN `tabSales Team` st on st.parent = so.customer    
    #     WHERE 
    #         so.docstatus = 1 AND
    #         (so.name LIKE 'PTMTO%%' OR
    #         so.name LIKE 'SOJV%%' OR
    #         so.name LIKE 'SOHO%%')
    # """

    # uncomment below for the local erpnext
    query = """
        SELECT
            soi.item_code AS item_code,
            soi.custom_commercial_name AS commercial_name,
            soi.custom_color AS color,
            soi.custom_width AS width,
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
            st.sales_person,
            sp.parent_sales_person,
            so.name AS name,
            so.delivery_date AS delivery_date,
            so.delivery_status AS delivery_status
        FROM 
            `tabSales Order Item` AS soi
        LEFT JOIN 
            `tabSales Order` AS so
        ON 
            so.name = soi.parent
        LEFT JOIN `tabSales Team` st on st.parent = so.customer
        LEFT JOIN `tabSales Person` sp on st.sales_person = sp.name    
        WHERE 
            so.docstatus = 1
    """


    # query = """
    #     SELECT
    #         soi.item_code AS item_code,
    #         soi.qty AS qty,
    #         COALESCE(soi.delivered_qty, 0) AS delivered_qty,
    #         (soi.qty - COALESCE(soi.delivered_qty, 0)) AS pending_qty,
    #         soi.stock_uom AS stock_uom,
    #         so.transaction_date AS posting_date,
    #         soi.custom_item_status AS custom_item_status,
    #         so.customer AS customer,
    #         st.sales_person,
    #         so.name AS name,
    #         so.status AS status
    #     FROM 
    #         `tabSales Order Item` AS soi
    #     LEFT JOIN 
    #         `tabSales Order` AS so
    #     ON 
    #         so.name = soi.parent
    #     LEFT JOIN `tabSales Team` st on st.parent = so.customer     
    #     WHERE 
    #         so.docstatus = 1 
    # """

    conditions = []

    if filters.get("sales_person"):
        conditions.append("st.sales_person = %(sales_person)s")
    
    if filters.get("parent_sales_person"):
        conditions.append("sp.parent_sales_person = %(parent_sales_person)s")

    if filters.get("item_code"):
        conditions.append("soi.item_code = %(item_code)s")
    
    if filters.get("commercial_name"):
        conditions.append("soi.commercial_name = %(commercial_name)s")
    
    if filters.get("color"):
        conditions.append("soi.color = %(color)s")

    if filters.get("custom_item_status"):
        conditions.append("soi.custom_item_status = %(custom_item_status)s")
    
    if filters.get("from_date"):
        conditions.append("so.transaction_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("so.transaction_date <= %(to_date)s")
    
    if filters.get("delivery_status"):
        conditions.append("so.delivery_status = %(delivery_status)s")
    
    if conditions:
        query += " AND " + " AND ".join(conditions)

    filter_values = {
        "sales_person": filters.get("sales_person"),
        "parent_sales_person": filters.get("parent_sales_person"),
        "item_code": filters.get("item_code"),
        "commercial_name": filters.get("commercial_name"),
        "custom_item_status": filters.get("custom_item_status"),
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "delivery_status": filters.get("delivery_status"),
    }
    
    return frappe.db.sql(query, filter_values, as_dict=1)
