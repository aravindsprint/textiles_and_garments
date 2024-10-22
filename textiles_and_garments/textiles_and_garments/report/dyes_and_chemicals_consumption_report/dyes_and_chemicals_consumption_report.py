# Copyright (c) 2024, Aravind and contributors
# For license information, please see license.txt

# import frappe

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
    columns = []

    columns.extend(
        [
            {
                "label": _("Date"),
                "fieldname": "posting_date",
                "fieldtype": "Date",
                "width": 120,
            },
            {
                "label": _("Stock Entry"),
                "fieldname": "stock_entry",
                "fieldtype": "Link",
                "options": "Stock Entry",
                "width": 120,
            },
            {
                "label": _("Work Order"),
                "fieldname": "work_order",
                "fieldtype": "Link",
                "options": "Work Order",
                "width": 120,
            },
            {
                "label": _("Item Code"),
                "fieldname": "item_code",
                "fieldtype": "Link",
                "options": "Item",
                "width": 220,
            },
            {
            "label": _("Warehouse No"),
            "fieldname": "warehouse",
            "fieldtype": "Data",
            "width": 220,
            },
            {
            "label": _("Batch No"),
            "fieldname": "batch_no",
            "fieldtype": "Link",
            "options": "Batch",
            "width": 220,
            },
            {
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 100,
            },
            {
            "label": _("Stock UOM"),
            "fieldname": "stock_uom",
            "fieldtype": "Data",
            "width": 70,
            },
            {
                "label": _("Amount"),
                "fieldname": "amount",
                "fieldtype": "Float",
                "width": 150,
            },
        ]
    )

    return columns

def get_data(filters):
    data = []
    stock_entry_data = get_stock_entry_data_from_stock_entry(filters)
    data.extend(stock_entry_data)
    return data

def get_stock_entry_data_from_stock_entry(filters):
    print("\n\n\nfilters\n\n\n",filters)
    # Base query to fetch data from Stock Entry and Stock Entry Detail
    query = """
        SELECT 
            ste_detail.item_code AS item_code,
            ste.work_order AS work_order,
            ste.name AS stock_entry,
            ste_detail.s_warehouse AS warehouse,
            ste_detail.qty AS qty,
            ste_detail.batch_no AS batch_no,
            ste_detail.stock_uom AS stock_uom,
            ste_detail.amount AS amount,
            ste.posting_date AS posting_date,
            ste_detail.s_warehouse
        FROM 
            `tabStock Entry Detail` AS ste_detail
        LEFT JOIN 
            `tabStock Entry` AS ste
        ON 
            ste_detail.parent = ste.name
        WHERE 
            ste.docstatus = 1
            AND ste.purpose = 'Manufacture'
            AND ste_detail.item_code NOT LIKE %(item_code_pattern)s
            AND ste_detail.s_warehouse LIKE %(warehouse_pattern)s
    """
    print("\n\n\nquery\n\n",query)
    
    # Dynamically append additional filter conditions
    conditions = []
    
    if filters.get("item_code"):
        conditions.append("ste_detail.item_code = %(item_code)s")
    
    if filters.get("batch_no"):
        conditions.append("ste_detail.batch_no = %(batch_no)s")
    
    if filters.get("work_order"):
        conditions.append("ste.work_order = %(work_order)s")
    
    if filters.get("from_date"):
        conditions.append("ste.posting_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("ste.posting_date <= %(to_date)s")
    
    # If conditions were added, append them to the query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Define filter values and ensure pattern wildcards are included in the filter values
    filter_values = {
        "item_code_pattern": '%KF%/%',  # Adding the % wildcards directly in the value
        "warehouse_pattern": '%KGS%',   # Adding the % wildcards directly in the value
        "item_code": filters.get("item_code"),
        "batch_no": filters.get("batch_no"),
        "work_order": filters.get("work_order"),
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date")
    }
    
    # Execute the query with filters
    return frappe.db.sql(query, filter_values, as_dict=1)






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
#     ]


#     columns.extend(
#         [
#             {
#                 "label": _("Date"),
#                 "fieldname": "posting_date",
#                 "fieldtype": "Date",
#                 "width": 120,
#             },
#             {
#                 "label": _("Stock Entry"),
#                 "fieldname": "stock_entry",
#                 "fieldtype": "Link",
#                 "options": "Stock Entry",
#                 "width": 120,
#             },
#             {
#                 "label": _("Work Order"),
#                 "fieldname": "work_order",
#                 "fieldtype": "Link",
#                 "options": "Work Order",
#                 "width": 120,
#             },
#             {
#                 "label": _("Item Code"),
#                 "fieldname": "item_code",
#                 "fieldtype": "Link",
#                 "options": "Item",
#                 "width": 220,
#             },
#             {
#             "label": _("Batch No"),
#             "fieldname": "batch_no",
#             "fieldtype": "link",
#             "options": "Batch",
#             "width": 220,
#             },
#             {
#             "label": _("Qty"),
#             "fieldname": "qty",
#             "fieldtype": "Float",
#             "width": 100,
#             },
#             {
#             "label": _("Stock UOM"),
#             "fieldname": "stock_uom",
#             "fieldtype": "Data",
#             "width": 70,
#             },
#             {
#                 "label": _("Amount"),
#                 "fieldname": "amount",
#                 "fieldtype": "Float",
#                 "width": 150,
#             },
#         ]
#     )

#     return columns

# def get_data(filters):
#     data = []
#     stock_entry_data = get_stock_entry_data_from_stock_entry(filters)
#     print("\n\n\nstock_entry_data\n\n\n", stock_entry_data)
#     data.extend(stock_entry_data)
#     return data

# def get_stock_entry_data_from_stock_entry(filters):
#     stock_entry_data = frappe.db.sql("""
#         SELECT 
#             ste_detail.item_code AS item_code,
#             ste.work_order AS work_order,
#             ste.name AS stock_entry,
#             ste_detail.s_warehouse AS s_warehouse,
#             ste_detail.qty AS qty,
#             ste_detail.batch_no AS batch_no,
#             ste_detail.stock_uom AS stock_uom,
#             ste_detail.amount AS amount,
#             ste.posting_date AS posting_date
#         FROM 
#             `tabStock Entry Detail` AS ste_detail
#         LEFT JOIN 
#             `tabStock Entry` AS ste
#         ON 
#             ste_detail.parent = ste.name
#         WHERE 
#             ste.docstatus = "Submitted"
#             AND ste_detail.item_code LIKE '%KF%/%'
#             AND ste_detail.s_warehouse LIKE '%KGS%'
#     """, as_dict=1)
#     return stock_entry_data







  
