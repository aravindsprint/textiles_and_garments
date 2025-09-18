# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

# from collections import defaultdict
# import frappe
# from frappe import _
# from frappe.query_builder.functions import Sum
# from frappe.utils import flt, today

# def execute(filters=None):
#     columns, data = [], []
#     data = get_data(filters)
#     columns = get_columns(filters)
#     return columns, data

# def get_columns(filters):
#     columns = [
#         {
#             "label": _("Date"),
#             "fieldname": "posting_date",
#             "fieldtype": "Date",
#             "width": 150,
#         },
#         {
#             "label": _("Delivery Date"),
#             "fieldname": "delivery_date",
#             "fieldtype": "Date",
#             "width": 150,
#         },
#         {
#             "label": _("Sales Order"),
#             "fieldname": "name",
#             "fieldtype": "Link",
#             "options": "Sales Order",
#             "width": 150,
#         },
#         {
#             "label": _("Item Code"),
#             "fieldname": "item_code",
#             "fieldtype": "Link",
#             "options": "Item",
#             "width": 200,
#         },
#         {
#             "label": _("Commercial Name"),
#             "fieldname": "commercial_name",
#             "fieldtype": "Data",
#             "width": 100,
#         },
#         {
#             "label": _("Color"),
#             "fieldname": "color",
#             "fieldtype": "Data",
#             "width": 200,
#         },
#         {
#             "label": _("Width"),
#             "fieldname": "width",
#             "fieldtype": "Data",
#             "width": 100,
#         },
#         {
#             "label": _("Qty"),
#             "fieldname": "qty",
#             "fieldtype": "Float",
#             "width": 90,
#         },
#         {
#             "label": _("Delivered Qty"),
#             "fieldname": "delivered_qty",
#             "fieldtype": "Float",
#             "width": 90,
#         },
#         {
#             "label": _("Pending Qty"),
#             "fieldname": "pending_qty",
#             "fieldtype": "Float",
#             "width": 90,
#         },
#         {
#             "label": _("Amount"),
#             "fieldname": "amount",
#             "fieldtype": "Float",
#             "width": 90,
#         },
#         {
#             "label": _("Item Status"),
#             "fieldname": "custom_item_status",
#             "fieldtype": "Data",
#             "width": 70,
#         },
#         {
#             "label": _("UOM"),
#             "fieldname": "stock_uom",
#             "fieldtype": "Data",
#             "width": 70,
#         },
#         {
#             "label": _("Customer"),
#             "fieldname": "customer",
#             "fieldtype": "Data",
#             "width": 100,
#         },
#         {
#             "label": _("Sales Person"),
#             "fieldname": "sales_person",
#             "fieldtype": "Data",
#             "width": 100,
#         },
#         {
#             "label": _("Delivery status"),
#             "fieldname": "delivery_status",
#             "fieldtype": "Data",
#             "width": 70,
#         }
#     ]

#     return columns

# def get_data(filters):
#     data = []
#     sales_data = get_sales_order_data(filters)
#     data.extend(sales_data)
#     return data

# def get_sales_order_data(filters):
#     # pranera instance
#     # query = """
#     #     SELECT
#     #         soi.item_code AS item_code,
#     #         soi.commercial_name AS commercial_name,
#     #         soi.color AS color,
#     #         soi.width AS width,
#     #         soi.custom_item_status AS custom_item_status,
#     #         soi.qty AS qty,
#     #         soi.rate AS rate,
#     #         soi.amount AS original_amount,
#     #         COALESCE(soi.delivered_qty, 0) AS delivered_qty,
#     #         (soi.qty - COALESCE(soi.delivered_qty, 0)) AS pending_qty,
#     #         ((soi.qty - COALESCE(soi.delivered_qty, 0)) * soi.rate) AS amount,
#     #         soi.stock_uom AS stock_uom,
#     #         so.transaction_date AS posting_date,
#     #         so.customer AS customer,
#     #         st.sales_person,
#     #         so.name AS name,
#     #         so.delivery_date AS delivery_date,
#     #         so.delivery_status AS delivery_status
#     #     FROM 
#     #         `tabSales Order Item` AS soi
#     #     LEFT JOIN 
#     #         `tabSales Order` AS so
#     #     ON 
#     #         so.name = soi.parent
#     #     LEFT JOIN `tabSales Team` st on st.parent = so.customer    
#     #     WHERE 
#     #         so.docstatus = 1 AND
#     #         (so.name LIKE 'PTMTO%%' OR
#     #         so.name LIKE 'SOJV%%' OR
#     #         so.name LIKE 'SOHO%%')
#     # """

#     # local instance
#     query = """
#         SELECT
#             soi.item_code AS item_code,
#             soi.qty AS qty,
#             COALESCE(soi.delivered_qty, 0) AS delivered_qty,
#             (soi.qty - COALESCE(soi.delivered_qty, 0)) AS pending_qty,
#             soi.stock_uom AS stock_uom,
#             so.transaction_date AS posting_date,
#             soi.custom_item_status AS custom_item_status,
#             so.customer AS customer,
#             st.sales_person,
#             so.name AS name,
#             so.status AS status
#         FROM 
#             `tabSales Order Item` AS soi
#         LEFT JOIN 
#             `tabSales Order` AS so
#         ON 
#             so.name = soi.parent
#         LEFT JOIN `tabSales Team` st on st.parent = so.customer     
#         WHERE 
#             so.docstatus = 1 
#     """

#     conditions = []
    
#     if filters.get("item_code"):
#         conditions.append("soi.item_code = %(item_code)s")
    
#     if filters.get("commercial_name"):
#         conditions.append("soi.commercial_name = %(commercial_name)s")
    
#     if filters.get("color"):
#         conditions.append("soi.color = %(color)s")

#     if filters.get("custom_item_status"):
#         conditions.append("soi.custom_item_status = %(custom_item_status)s")
    
#     if filters.get("from_date"):
#         conditions.append("so.transaction_date >= %(from_date)s")

#     if filters.get("to_date"):
#         conditions.append("so.transaction_date <= %(to_date)s")
    
#     if filters.get("delivery_status"):
#         conditions.append("so.delivery_status = %(delivery_status)s")
    
#     if conditions:
#         query += " AND " + " AND ".join(conditions)

#     filter_values = {
#         "item_code": filters.get("item_code"),
#         "commercial_name": filters.get("commercial_name"),
#         "custom_item_status": filters.get("custom_item_status"),
#         "from_date": filters.get("from_date"),
#         "to_date": filters.get("to_date"),
#         "delivery_status": filters.get("delivery_status"),
#     }
    
#     return frappe.db.sql(query, filter_values, as_dict=1)


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
            "label": _("Sales Person"),
            "fieldname": "sales_person",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Delivery status"),
            "fieldname": "delivery_status",
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
            soi.qty AS qty,
            COALESCE(soi.delivered_qty, 0) AS delivered_qty,
            (soi.qty - COALESCE(soi.delivered_qty, 0)) AS pending_qty,
            soi.stock_uom AS stock_uom,
            so.transaction_date AS posting_date,
            soi.custom_item_status AS custom_item_status,
            so.customer AS customer,
            st.sales_person,
            so.name AS name,
            so.status AS status
        FROM 
            `tabSales Order Item` AS soi
        LEFT JOIN 
            `tabSales Order` AS so
        ON 
            so.name = soi.parent
        LEFT JOIN `tabSales Team` st on st.parent = so.customer     
        WHERE 
            so.docstatus = 1 
    """

    conditions = []
    params = []
    
    if filters.get("item_code"):
        conditions.append("soi.item_code = %s")
        params.append(filters.get("item_code"))
    
    if filters.get("commercial_name"):
        conditions.append("soi.commercial_name = %s")
        params.append(filters.get("commercial_name"))
    
    if filters.get("color"):
        conditions.append("soi.color = %s")
        params.append(filters.get("color"))

    # Handle multiple selection for custom_item_status
    if filters.get("custom_item_status"):
        custom_item_status = filters.get("custom_item_status")
        
        # Check if it's a string with comma-separated values
        if isinstance(custom_item_status, str) and ',' in custom_item_status:
            # Split the comma-separated string into a list and clean up
            custom_item_status_list = [status.strip() for status in custom_item_status.split(',') if status.strip()]
            if custom_item_status_list:
                placeholders = ", ".join(["%s"] * len(custom_item_status_list))
                conditions.append(f"soi.custom_item_status IN ({placeholders})")
                params.extend(custom_item_status_list)
        elif isinstance(custom_item_status, list) and custom_item_status:
            # If it's already a list
            placeholders = ", ".join(["%s"] * len(custom_item_status))
            conditions.append(f"soi.custom_item_status IN ({placeholders})")
            params.extend(custom_item_status)
        elif custom_item_status:
            # If it's a single value
            conditions.append("soi.custom_item_status = %s")
            params.append(custom_item_status)
    
    if filters.get("from_date"):
        conditions.append("so.transaction_date >= %s")
        params.append(filters.get("from_date"))

    if filters.get("to_date"):
        conditions.append("so.transaction_date <= %s")
        params.append(filters.get("to_date"))
    
    if filters.get("delivery_status"):
        conditions.append("so.delivery_status = %s")
        params.append(filters.get("delivery_status"))
    
    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Execute the query with positional parameters
    return frappe.db.sql(query, tuple(params), as_dict=1)