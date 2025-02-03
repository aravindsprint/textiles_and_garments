from collections import defaultdict
import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today

from datetime import date
from frappe import _

# def execute(filters=None):
#     columns, data = [], []
#     data = get_data(filters)
#     columns = get_columns(filters)
#     return columns, data


# def get_columns(filters):
#     columns = []

#     columns.extend(
#         [
#             {
#                 "label": _("Date"),
#                 "fieldname": "posting_date",
#                 "fieldtype": "Date",
#                 "width": 150,
#             },
#             {
#                 "label": _("Stock Entry"),
#                 "fieldname": "stock_entry",
#                 "fieldtype": "Link",
#                 "options": "Stock Entry",
#                 "width": 200,
#             },
#             {
#                 "label": _("Work Order"),
#                 "fieldname": "work_order",
#                 "fieldtype": "Link",
#                 "options": "Work Order",
#                 "width": 200,
#             },
#             {
#                 "label": _("Ageing"),
#                 "fieldname": "days",
#                 "fieldtype": "Data",
#                 "width": 150
#             },
#             {
#                 "label": _("Status"),
#                 "fieldname": "status",
#                 "fieldtype": "Data",
#                 "width": 150,
#             }
#         ]
#     )

#     return columns


# def get_data(filters):
#     data = []
#     sales_data = get_data_from_stock_entry(filters)
#     data.extend(sales_data)
#     return data


# def get_data_from_stock_entry(filters):
#     # Base query to fetch data from Sales Invoice and Sales Invoice Item
#     query = """
#         SELECT 
#             stock_entry.name AS stock_entry,
#             stock_entry.custom_reference_dyeing_work_order AS work_order,
#             stock_entry.posting_date AS posting_date,
#             wo.status AS status
#         FROM 
#             `tabStock Entry` AS stock_entry
#         LEFT JOIN 
#             `tabWork Order` AS wo
#         ON 
#             stock_entry.custom_reference_dyeing_work_order = wo.name
#         WHERE 
#             stock_entry.docstatus = 1
#             AND stock_entry.name LIKE %(item_code_pattern)s
#     """

    

    
#     # Dynamically append additional filter conditions
#     conditions = []
    
#     if filters.get("item_code"):
#         conditions.append("stock_entry.item_code = %(item_code)s")
    
#     if filters.get("batch_no"):
#         conditions.append("stock_entry.batch_no = %(batch_no)s")
    
#     if filters.get("work_order"):
#         conditions.append("wo.custom_work_order = %(work_order)s")
    
#     if filters.get("from_date"):
#         conditions.append("wo.posting_date >= %(from_date)s")

#     if filters.get("to_date"):
#         conditions.append("wo.posting_date <= %(to_date)s")
    
#     if filters.get("status"):
#         conditions.append("wo.status = %(status)s")
    
#     # If conditions were added, append them to the query
#     if conditions:
#         query += " AND " + " AND ".join(conditions)

#     # Define filter values to pass as parameters
#     filter_values = {
#         # "item_code_pattern": 'JDI%/%',  # Passing the pattern as a parameter
#         "item_code_pattern": 'MAT%',  # Passing the pattern as a parameter
#         "from_date": filters.get("from_date"),
#         "to_date": filters.get("to_date"),
#         "status": filters.get("status")
#     }
    
#     # Execute the query with filters
#     return frappe.db.sql(query, filter_values, as_dict=1)


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
                "width": 150,
            },
            {
                "label": _("Stock Entry"),
                "fieldname": "stock_entry",
                "fieldtype": "Link",
                "options": "Stock Entry",
                "width": 200,
            },
            {
                "label": _("Work Order"),
                "fieldname": "work_order",
                "fieldtype": "Link",
                "options": "Work Order",
                "width": 200,
            },
            {
                "label": _("Ageing"),
                "fieldname": "ageing_days",
                "fieldtype": "Int",
                "width": 150
            },
            {
                "label": _("WO Status"),
                "fieldname": "wo_status",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": _("Sales Invoice"),
                "fieldname": "sales_invoice",
                "fieldtype": "Link",
                "options": "Sales Invoice",
                "width": 200,
            },
            {
                "label": _("SI Status"),
                "fieldname": "si_status",
                "fieldtype": "Data",
                "width": 150,
            },
        ]
    )

    return columns

def get_data(filters):
    data = []
    sales_data = get_data_from_stock_entry(filters)
    data.extend(sales_data)
    return data

def get_data_from_stock_entry(filters):
    today = date.today()

    # Base query to fetch data from Stock Entry and Work Order
    query = """
        SELECT 
            stock_entry.name AS stock_entry,
            stock_entry.custom_reference_dyeing_work_order AS work_order,
            stock_entry.posting_date AS posting_date,
            wo.status AS wo_status,
            si.name AS sales_invoice,
            si.status AS si_status
        FROM 
            `tabStock Entry` AS stock_entry
        LEFT JOIN 
            `tabWork Order` AS wo
        ON 
            stock_entry.custom_reference_dyeing_work_order = wo.name
        LEFT JOIN 
            `tabSales Invoice` AS si
        ON 
            stock_entry.custom_reference_dyeing_work_order = si.custom_work_order    
        WHERE 
            stock_entry.docstatus = 1
            AND stock_entry.name LIKE %(item_code_pattern)s
    """

    # Dynamically append additional filter conditions
    conditions = []
    
    if filters.get("item_code"):
        conditions.append("stock_entry.item_code = %(item_code)s")
    
    if filters.get("batch_no"):
        conditions.append("stock_entry.batch_no = %(batch_no)s")
    
    if filters.get("work_order"):
        conditions.append("wo.custom_work_order = %(work_order)s")
    
    if filters.get("from_date"):
        conditions.append("stock_entry.posting_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("stock_entry.posting_date <= %(to_date)s")
    
    if filters.get("wo_status"):
        conditions.append("wo.status = %(wo_status)s")

    if filters.get("si_status"):
        conditions.append("si.status = %(si_status)s")     
    
    # If conditions were added, append them to the query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Define filter values to pass as parameters
    filter_values = {
        "item_code_pattern": 'JDI%/%',  # Passing the pattern as a parameter
        # "item_code_pattern": 'MAT%',  # Adjust pattern as needed
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "wo_status": filters.get("wo_status"),
        "si_status": filters.get("si_status")
    }
    
    # Execute the query with filters
    results = frappe.db.sql(query, filter_values, as_dict=1)

    # Calculate Ageing Days
    for row in results:
        if row.get("posting_date"):
            row["ageing_days"] = (today - row["posting_date"]).days
        else:
            row["ageing_days"] = None  # Handle missing dates

    return results