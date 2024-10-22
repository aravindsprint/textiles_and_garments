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
                "label": _("Batch No"),
                "fieldname": "batch_no",
                "fieldtype": "Link",
                "options": "Batch",
                "width": 200,
            },
            {
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 200,
            },
            {
                "label": _("UOM"),
                "fieldname": "stock_uom",
                "fieldtype": "Data",
                "width": 150
            },
            {
            "label": _("Grand Total"),
            "fieldname": "grand_total",
            "fieldtype": "Float",
            "width": 200,
            },
            {
                "label": _("Status"),
                "fieldname": "status",
                "fieldtype": "Data",
                "width": 150,
            }
        ]
    )

    return columns


def get_data(filters):
    data = []
    sales_data = get_sales_data_from_stock_entry(filters)
    data.extend(sales_data)
    return data


def get_sales_data_from_stock_entry(filters):
    # Base query to fetch data from Sales Invoice and Sales Invoice Item
    query = """
        SELECT 
            sales_invoice_item.item_code AS item_code,
            si.custom_work_order AS work_order,
            si.name AS sales_invoice,
            sales_invoice_item.batch_no AS batch_no,
            sales_invoice_item.qty AS qty,
            sales_invoice_item.stock_uom AS stock_uom,
            si.posting_date AS posting_date,
            si.grand_total AS grand_total,
            si.status AS status
        FROM 
            `tabSales Invoice Item` AS sales_invoice_item
        LEFT JOIN 
            `tabSales Invoice` AS si
        ON 
            sales_invoice_item.parent = si.name
        WHERE 
            si.docstatus = 1
            AND sales_invoice_item.item_code LIKE %(item_code_pattern)s
            AND sales_invoice_item.warehouse LIKE %(warehouse_pattern)s
    """

    

    
    # Dynamically append additional filter conditions
    conditions = []
    
    if filters.get("item_code"):
        conditions.append("sales_invoice_item.item_code = %(item_code)s")
    
    if filters.get("batch_no"):
        conditions.append("sales_invoice_item.batch_no = %(batch_no)s")
    
    if filters.get("work_order"):
        conditions.append("si.custom_work_order = %(work_order)s")
    
    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
    
    if filters.get("status"):
        conditions.append("si.status = %(status)s")
    
    # If conditions were added, append them to the query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Define filter values to pass as parameters
    filter_values = {
        "item_code_pattern": 'JOBWORK%/%',  # Passing the pattern as a parameter
        "warehouse_pattern": 'DYE/LOT%',
        "item_code": filters.get("item_code"),
        "batch_no": filters.get("batch_no"),
        "custom_work_order": filters.get("work_order"),
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "status": filters.get("status")
    }
    
    # Execute the query with filters
    return frappe.db.sql(query, filter_values, as_dict=1)


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
#                 "label": _("Sales Invoice"),
#                 "fieldname": "sales_invoice",
#                 "fieldtype": "Link",
#                 "options": "Sales Invoice",
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
#                 "label": _("Item Code"),
#                 "fieldname": "item_code",
#                 "fieldtype": "Link",
#                 "options": "Item",
#                 "width": 200,
#             },
#             {
#                 "label": _("Batch No"),
#                 "fieldname": "batch_no",
#                 "fieldtype": "Link",
#                 "options": "Batch",
#                 "width": 200,
#             },
#             {
#             "label": _("qty"),
#             "fieldname": "qty",
#             "fieldtype": "Float",
#             "width": 200,
#             },
#             {
#                 "label": _("UOM"),
#                 "fieldname": "stock_uom",
#                 "fieldtype": "Data",
#                 "width": 150
#             },
#             {
#             "label": _("Grand Total"),
#             "fieldname": "grand_total",
#             "fieldtype": "Float",
#             "width": 200,
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
#     sales_data = get_sales_data_from_stock_entry(filters)
#     print("\n\n\nsales_data\n\n\n", sales_data)
#     data.extend(sales_data)
#     return data

# def get_sales_data_from_stock_entry(filters):
#     sales_data = frappe.db.sql("""
#         SELECT 
#             sales_invoice_item.item_code AS item_code,
#             si.work_order AS work_order,
#             si.name AS sales_invoice,
#             sales_invoice_item.batch_no AS batch_no,
#             sales_invoice_item.qty AS qty,
#             sales_invoice_item.stock_uom AS stock_uom,
#             si.posting_date AS posting_date,
#             si.grand_total AS grand_total,
#             si.status AS status
#         FROM 
#             `tabSales Invoice Item` AS sales_invoice_item
#         LEFT JOIN 
#             `tabSales Invoice` AS si
#         ON 
#             sales_invoice_item.parent = si.name
#         WHERE 
#             si.docstatus = 1
#             AND sales_invoice_item.item_code LIKE 'JOBWORK%/%'
#             AND sales_invoice_item.warehouse LIKE "DYE/LOT%"
#     """, as_dict=1)

#     return sales_data