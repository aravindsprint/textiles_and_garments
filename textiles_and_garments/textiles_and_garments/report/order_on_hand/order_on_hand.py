# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt


from collections import defaultdict
import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today

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
#             "fieldname": "original_amount",
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
#             "label": _("Document status"),
#             "fieldname": "status",
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
# 	# uncomment below for the local instance
#     query = """
#         SELECT
#             soi.item_code AS item_code,
#             soi.custom_commercial_name AS commercial_name,
#             soi.custom_color AS color,
#             soi.custom_width AS width,
#             soi.custom_item_status AS custom_item_status,
#             soi.qty AS qty,
#             soi.rate AS rate,
#             soi.amount AS original_amount,
#             COALESCE(soi.delivered_qty, 0) AS delivered_qty,
#             (soi.qty - COALESCE(soi.delivered_qty, 0)) AS pending_qty,
#             ROUND(
#                 CASE 
#                     WHEN soi.qty > 0 THEN 
#                         (COALESCE(soi.delivered_qty, 0) / soi.qty) * 100 
#                     ELSE 0 
#                 END, 2
#             ) AS delivered_qty_percent,
#             ROUND(
#                 CASE 
#                     WHEN soi.qty > 0 THEN 
#                         ((soi.qty - COALESCE(soi.delivered_qty, 0)) / soi.qty) * 100 
#                     ELSE 0 
#                 END, 2
#             ) AS pending_qty_percent,
#             (COALESCE(soi.delivered_qty, 0) * soi.rate) AS delivered_amount,
#             ((soi.qty - COALESCE(soi.delivered_qty, 0)) * soi.rate) AS pending_amount,
#             ROUND(
#                 CASE 
#                     WHEN soi.amount > 0 THEN 
#                         (COALESCE(soi.delivered_qty, 0) * soi.rate / soi.amount) * 100 
#                     ELSE 0 
#                 END, 2
#             ) AS amount_billed_percent,
#             soi.stock_uom AS stock_uom,
#             so.transaction_date AS posting_date,
#             so.customer AS customer,
#             st.sales_person,
#             sp.parent_sales_person,
#             so.name AS name,
#             so.naming_series AS series,
#             so.delivery_date AS delivery_date,
#             so.delivery_status AS delivery_status,
#             so.status AS status
#         FROM 
#             `tabSales Order Item` AS soi
#         LEFT JOIN 
#             `tabSales Order` AS so
#         ON 
#             so.name = soi.parent
#         LEFT JOIN `tabSales Team` st on st.parent = so.customer
#         LEFT JOIN `tabSales Person` sp on st.sales_person = sp.name    
#         WHERE 
#             so.docstatus = 1
#     """

#     # uncomment below for the pranera instance
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
#     #         ROUND(
#     #             CASE 
#     #                 WHEN soi.qty > 0 THEN 
#     #                     (COALESCE(soi.delivered_qty, 0) / soi.qty) * 100 
#     #                 ELSE 0 
#     #             END, 2
#     #         ) AS delivered_qty_percent,
#     #         ROUND(
#     #             CASE 
#     #                 WHEN soi.qty > 0 THEN 
#     #                     ((soi.qty - COALESCE(soi.delivered_qty, 0)) / soi.qty) * 100 
#     #                 ELSE 0 
#     #             END, 2
#     #         ) AS pending_qty_percent,
#     #         (COALESCE(soi.delivered_qty, 0) * soi.rate) AS delivered_amount,
#     #         ((soi.qty - COALESCE(soi.delivered_qty, 0)) * soi.rate) AS pending_amount,
#     #         ROUND(
#     #             CASE 
#     #                 WHEN soi.amount > 0 THEN 
#     #                     (COALESCE(soi.delivered_qty, 0) * soi.rate / soi.amount) * 100 
#     #                 ELSE 0 
#     #             END, 2
#     #         ) AS amount_billed_percent,
#     #         soi.stock_uom AS stock_uom,
#     #         so.transaction_date AS posting_date,
#     #         so.customer AS customer,
#     #         st.sales_person,
#     #         sp.parent_sales_person,
#     #         so.name AS name,
#     #         so.naming_series AS series,
#     #         so.delivery_date AS delivery_date,
#     #         so.delivery_status AS delivery_status
#     #     FROM 
#     #         `tabSales Order Item` AS soi
#     #     LEFT JOIN 
#     #         `tabSales Order` AS so
#     #     ON 
#     #         so.name = soi.parent
#     #     LEFT JOIN `tabSales Team` st on st.parent = so.customer
#     #     LEFT JOIN `tabSales Person` sp on st.sales_person = sp.name    
#     #     WHERE 
#     #         so.docstatus = 1
#     # """


#     conditions = []
#     params = {}
    
#     if filters.get("sales_person"):
#         conditions.append("st.sales_person = %(sales_person)s")
#         params["sales_person"] = filters.get("sales_person")
    
#     if filters.get("parent_sales_person"):
#         conditions.append("sp.parent_sales_person = %(parent_sales_person)s")
#         params["parent_sales_person"] = filters.get("parent_sales_person")

#     if filters.get("item_code"):
#         conditions.append("soi.item_code = %(item_code)s")
#         params["item_code"] = filters.get("item_code")
    
#     if filters.get("commercial_name"):
#         conditions.append("soi.custom_commercial_name = %(commercial_name)s")
#         params["commercial_name"] = filters.get("commercial_name")
    
#     if filters.get("color"):
#         conditions.append("soi.custom_color = %(color)s")
#         params["color"] = filters.get("color")

#     if filters.get("custom_item_status"):
#         custom_item_status = filters.get("custom_item_status")
#         if isinstance(custom_item_status, list):
#             conditions.append("soi.custom_item_status IN %(custom_item_status)s")
#             params["custom_item_status"] = custom_item_status
#         else:
#             conditions.append("soi.custom_item_status = %(custom_item_status)s")
#             params["custom_item_status"] = custom_item_status
    
#     if filters.get("from_date"):
#         conditions.append("so.transaction_date >= %(from_date)s")
#         params["from_date"] = filters.get("from_date")

#     if filters.get("to_date"):
#         conditions.append("so.transaction_date <= %(to_date)s")
#         params["to_date"] = filters.get("to_date")
    
#     if filters.get("delivery_status"):
#         conditions.append("so.delivery_status = %(delivery_status)s")
#         params["delivery_status"] = filters.get("delivery_status")
    
#     # Handle series filter (multiselect)
#     if filters.get("series"):
#         series = filters.get("series")
#         if isinstance(series, list):
#             conditions.append("so.naming_series IN %(series)s")
#             params["series"] = series
#         else:
#             conditions.append("so.naming_series = %(series)s")
#             params["series"] = series

#     if conditions:
#         query += " AND " + " AND ".join(conditions)

#     return frappe.db.sql(query, params, as_dict=1)


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
            "fieldname": "original_amount",
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
            "label": _("Parent Sales Person"),
            "fieldname": "parent_sales_person",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Document status"),
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
    # uncomment below for the local instance
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
            ROUND(
                CASE 
                    WHEN soi.qty > 0 THEN 
                        (COALESCE(soi.delivered_qty, 0) / soi.qty) * 100 
                    ELSE 0 
                END, 2
            ) AS delivered_qty_percent,
            ROUND(
                CASE 
                    WHEN soi.qty > 0 THEN 
                        ((soi.qty - COALESCE(soi.delivered_qty, 0)) / soi.qty) * 100 
                    ELSE 0 
                END, 2
            ) AS pending_qty_percent,
            (COALESCE(soi.delivered_qty, 0) * soi.rate) AS delivered_amount,
            ((soi.qty - COALESCE(soi.delivered_qty, 0)) * soi.rate) AS pending_amount,
            ROUND(
                CASE 
                    WHEN soi.amount > 0 THEN 
                        (COALESCE(soi.delivered_qty, 0) * soi.rate / soi.amount) * 100 
                    ELSE 0 
                END, 2
            ) AS amount_billed_percent,
            soi.stock_uom AS stock_uom,
            so.transaction_date AS posting_date,
            so.customer AS customer,
            st.sales_person,
            sp.parent_sales_person,
            so.name AS name,
            so.naming_series AS series,
            so.delivery_date AS delivery_date,
            so.delivery_status AS delivery_status,
            so.status AS status
        FROM 
            `tabSales Order Item` AS soi
        LEFT JOIN 
            `tabSales Order` AS so
        ON 
            so.name = soi.parent
        LEFT JOIN `tabSales Team` st on st.parent = so.name
        LEFT JOIN `tabSales Person` sp on st.sales_person = sp.name    
        WHERE 
            so.docstatus = 1
    """

    conditions = []
    params = {}
    
    if filters.get("sales_person"):
        sales_person = filters.get("sales_person")
        # Check if the sales person is a parent sales person
        is_parent = frappe.db.get_value("Sales Person", sales_person, "is_group")
        
        if is_parent:
            # If it's a parent sales person, get all child sales persons
            child_sales_persons = get_child_sales_persons(sales_person)
            if child_sales_persons:
                conditions.append("(st.sales_person IN %(sales_persons)s OR sp.parent_sales_person = %(sales_person)s)")
                params["sales_persons"] = child_sales_persons
                params["sales_person"] = sales_person
            else:
                conditions.append("sp.parent_sales_person = %(sales_person)s")
                params["sales_person"] = sales_person
        else:
            # If it's a regular sales person, show their data directly
            conditions.append("(st.sales_person = %(sales_person)s OR sp.parent_sales_person = %(sales_person)s)")
            params["sales_person"] = sales_person
    
    if filters.get("parent_sales_person"):
        parent_sales_person = filters.get("parent_sales_person")
        # Get all child sales persons for the parent
        child_sales_persons = get_child_sales_persons(parent_sales_person)
        if child_sales_persons:
            conditions.append("(st.sales_person IN %(child_sales_persons)s OR sp.parent_sales_person = %(parent_sales_person)s)")
            params["child_sales_persons"] = child_sales_persons
            params["parent_sales_person"] = parent_sales_person
        else:
            conditions.append("sp.parent_sales_person = %(parent_sales_person)s")
            params["parent_sales_person"] = parent_sales_person

    if filters.get("item_code"):
        conditions.append("soi.item_code = %(item_code)s")
        params["item_code"] = filters.get("item_code")
    
    if filters.get("commercial_name"):
        conditions.append("soi.custom_commercial_name = %(commercial_name)s")
        params["commercial_name"] = filters.get("commercial_name")
    
    if filters.get("color"):
        conditions.append("soi.custom_color = %(color)s")
        params["color"] = filters.get("color")

    if filters.get("custom_item_status"):
        custom_item_status = filters.get("custom_item_status")
        if isinstance(custom_item_status, list):
            conditions.append("soi.custom_item_status IN %(custom_item_status)s")
            params["custom_item_status"] = custom_item_status
        else:
            conditions.append("soi.custom_item_status = %(custom_item_status)s")
            params["custom_item_status"] = custom_item_status
    
    if filters.get("from_date"):
        conditions.append("so.transaction_date >= %(from_date)s")
        params["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("so.transaction_date <= %(to_date)s")
        params["to_date"] = filters.get("to_date")
    
    if filters.get("delivery_status"):
        conditions.append("so.delivery_status = %(delivery_status)s")
        params["delivery_status"] = filters.get("delivery_status")
    
    # Handle series filter (multiselect)
    if filters.get("series"):
        series = filters.get("series")
        if isinstance(series, list):
            conditions.append("so.naming_series IN %(series)s")
            params["series"] = series
        else:
            conditions.append("so.naming_series = %(series)s")
            params["series"] = series

    if conditions:
        query += " AND " + " AND ".join(conditions)

    return frappe.db.sql(query, params, as_dict=1)

def get_child_sales_persons(parent_sales_person):
    """Get all child sales persons for a given parent sales person"""
    child_sales_persons = frappe.db.sql("""
        SELECT name 
        FROM `tabSales Person` 
        WHERE parent_sales_person = %s 
        OR name IN (
            SELECT name FROM `tabSales Person` 
            WHERE parent_sales_person IN (
                SELECT name FROM `tabSales Person` WHERE parent_sales_person = %s
            )
        )
    """, (parent_sales_person, parent_sales_person), as_list=True)
    
    # Flatten the list and include the parent itself
    result = [parent_sales_person]
    for child in child_sales_persons:
        result.append(child[0])
    
    return result