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
                "width": 150,
            },
            {
                "label": _("QI Report Details"),
                "fieldname": "qi_report_details",
                "fieldtype": "Link",
                "options": "QI Report Details",
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
                "label": _("Fabric"),
                "fieldname": "fabric",
                "fieldtype": "Data",
                "width": 100
            },
            {
                "label": _("Batch No"),
                "fieldname": "batch_no",
                "fieldtype": "Link",
                "options": "Batch",
                "width": 200,
            },
            {
                "label": _("Lot No"),
                "fieldname": "lot_no",
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
                "width": 50
            },
            {
                "label": _("Work Order"),
                "fieldname": "work_order",
                "fieldtype": "Data",
                "width": 70
            },
            {
                "label": _("Supplier1"),
                "fieldname": "supplier1",
                "fieldtype": "Data",
                "width": 70
            },
            {
                "label": _("Supplier2"),
                "fieldname": "supplier2",
                "fieldtype": "Data",
                "width": 70
            },
            {
                "label": _("Supplier3"),
                "fieldname": "supplier3",
                "fieldtype": "Data",
                "width": 70
            },
            {
                "label": _("Fabric Required Width"),
                "fieldname": "fabric_required_width",
                "fieldtype": "Data",
                "width": 70
            },
            {
                "label": _("Total Qty"),
                "fieldname": "total_qty",
                "fieldtype": "Data",
                "width": 70
            },
            {
                "label": _("Total Accepted Qty"),
                "fieldname": "total_accepted_qty",
                "fieldtype": "Data",
                "width": 70
            },
            {
                "label": _("Total Rejected Qty"),
                "fieldname": "total_rejected_qty",
                "fieldtype": "Data",
                "width": 70
            },
            {
                "label": _("Knitting Mac No"),
                "fieldname": "knitting_machine_no",
                "fieldtype": "Data",
                "width": 50
            },
            {
                "label": _("Mistake Name"),
                "fieldname": "mistake_name",
                "fieldtype": "Data",
                "width": 100
            },
            {
                "label": _("Total Rolls"),
                "fieldname": "total_rolls",
                "fieldtype": "Data",
                "width": 80
            },
            {
                "label": _("Shade"),
                "fieldname": "shade",
                "fieldtype": "Data",
                "width": 80
            },
            {
                "label": _("Completed Date"),
                "fieldname": "completed_date",
                "fieldtype": "Data",
                "width": 80
            },
            {
                "label": _("Roll No"),
                "fieldname": "roll_no",
                "fieldtype": "Data",
                "width": 80
            },
            {
                "label": _("Greige Roll No"),
                "fieldname": "greige_roll_no",
                "fieldtype": "Data",
                "width": 80
            },
            {
                "label": _("Width"),
                "fieldname": "width",
                "fieldtype": "Data",
                "width": 80
            },
            {
                "label": _("Roll Weight"),
                "fieldname": "roll_weight",
                "fieldtype": "Data",
                "width": 80
            },
            {
                "label": _("Accepted Qty"),
                "fieldname": "accepted_qty",
                "fieldtype": "Data",
                "width": 80
            },
            {
                "label": _("Rejected Qty"),
                "fieldname": "rejected_qty",
                "fieldtype": "Data",
                "width": 80
            },
            {
                "label": _("Status"),
                "fieldname": "status",
                "fieldtype": "Data",
                "width": 30,
            }
        ]
    )

    return columns




def get_data(filters):
    data = []
    sales_data = get_sales_data_from_stock_entry(filters)
    data.extend(sales_data)
    print("\n\n\ndata\n\n\n",data)
    return data



def get_sales_data_from_stock_entry(filters):
    # Base query to fetch data from Sales Invoice and Sales Invoice Item
    query = "\
        SELECT \
            qi_report_details.item_code AS item_code,\
            mistake_details.mistake_name AS mistake_name,\
            mistake_details.total_points AS total_points,\
            qi_report_details.fabric AS fabric,\
            qi_report_details.supplier1 AS supplier1,\
            qi_report_details.supplier2 AS supplier2,\
            qi_report_details.supplier3 AS supplier3,\
            qi_report_details.lot_no AS lot_no,\
            qi_report_details.total_qty AS total_qty,\
            qi_report_details.fabric_required_width AS fabric_required_width,\
            qi_report_details.total_accepted_qty AS total_accepted_qty,\
            qi_report_details.total_rejected_qty AS total_rejected_qty,\
            qi_report_details.shade AS shade,\
            qi_report_details.total_rolls AS total_rolls,\
            qi_report_details.completed_date AS completed_date,\
            mistake_details.roll_no AS roll_no,\
            roll_details.greige_roll_no AS greige_roll_no,\
            roll.work_order AS work_order,\
            roll.knitting_machine_no AS knitting_machine_no,\
            roll_details.roll_weight AS roll_weight,\
            roll_details.total_qty AS total_qty,\
            roll_details.accepted_qty AS accepted_qty,\
            roll_details.rejected_qty AS rejected_qty,\
            roll_details.width AS width,\
            qi_report_details.name AS qi_report_details,\
            qi_report_details.batch_no AS batch_no,\
            qi_report_details.lot_weight AS qty,\
            qi_report_details.stock_uom AS stock_uom,\
            qi_report_details.date AS posting_date,\
            qi_report_details.docstatus AS status\
        FROM \
            `tabQI CC Report Details` AS qi_report_details\
        LEFT JOIN \
            `tabCC Mistake Details` AS mistake_details\
        ON \
            qi_report_details.name = mistake_details.parent\
        LEFT JOIN \
            `tabCC Roll Details` AS roll_details\
        ON \
            mistake_details.roll_no = roll_details.roll_no\
        LEFT JOIN \
            `tabRoll` AS roll\
        ON \
            roll.name = roll_details.greige_roll_no \
        WHERE \
            qi_report_details.docstatus = 1 AND\
            qi_report_details.item_code NOT LIKE 'GKF%%'\
    "


    

    
    # Dynamically append additional filter conditions
    conditions = []
    
    if filters.get("item_code"):
        conditions.append("qi_report_details.item_code = %(item_code)s")
    
    if filters.get("batch_no"):
        conditions.append("qi_report_details.batch_no = %(batch_no)s")
    
    if filters.get("work_order"):
        conditions.append("mistake_details.custom_work_order = %(work_order)s")
    
    if filters.get("from_date"):
        conditions.append("qi_report_details.date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("qi_report_details.date <= %(to_date)s")
    
    if filters.get("status"):
        conditions.append("mistake_details.status = %(status)s")
    
    # If conditions were added, append them to the query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Define filter values to pass as parameters
    filter_values = {
        "item_code_pattern": 'GKF%/%',  # Passing the pattern as a parameter
        "item_code": filters.get("item_code"),
        "batch_no": filters.get("batch_no"),
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "status": filters.get("status")
    }
    
    # Execute the query with filters
    return frappe.db.sql(query, filter_values, as_dict=1)






# def get_sales_data_from_stock_entry(filters):
#     # Base query to fetch data from Sales Invoice and Sales Invoice Item
#     query = """
#         SELECT 
#             qi_report_details_item.item_code AS item_code,
#             si.mistake_name AS mistake_name,
#             si.total_points AS total_points,
#             si.roll_no AS roll_no,
#             ri.roll_weight AS roll_weight,
#             si.parent AS qi_report_details,
#             qi_report_details_item.batch_no AS batch_no,
#             qi_report_details_item.lot_weight AS qty,
#             qi_report_details_item.stock_uom AS stock_uom,
#             qi_report_details_item.date AS posting_date,
#             qi_report_details_item.docstatus AS status
#         FROM 
#             `tabQI Report Details` AS qi_report_details_item
#         LEFT JOIN 
#             `tabMistake Details` AS si
#         ON 
#             qi_report_details_item.name = si.parent
#         LEFT JOIN 
#             `tabRoll Details` AS ri
#         ON 
#             si.roll_no = ri.roll_no    
#         WHERE 
#             qi_report_details_item.docstatus = 1
#     """
    
#     # Dynamically append additional filter conditions
#     conditions = []
    
#     if filters.get("item_code"):
#         conditions.append("qi_report_details_item.item_code = %(item_code)s")
    
#     if filters.get("batch_no"):
#         conditions.append("qi_report_details_item.batch_no = %(batch_no)s")
    
#     if filters.get("from_date"):
#         conditions.append("qi_report_details_item.date >= %(from_date)s")

#     if filters.get("to_date"):
#         conditions.append("qi_report_details_item.date <= %(to_date)s")
    
#     if filters.get("status"):
#         conditions.append("qi_report_details_item.docstatus = %(status)s")
    
#     # If conditions were added, append them to the query
#     if conditions:
#         query += " AND " + " AND ".join(conditions)

#     # Define filter values to pass as parameters
#     filter_values = {
#         "item_code": filters.get("item_code"),
#         "batch_no": filters.get("batch_no"),
#         "from_date": filters.get("from_date"),
#         "to_date": filters.get("to_date"),
#         "status": filters.get("status")
#     }
    
#     # Execute the query with filters
#     results = frappe.db.sql(query, filter_values, as_dict=1)
    
#     # Post-process results for the desired format
#     formatted_data = []
#     previous_row = None
    
#     for row in results:
#         if previous_row and all(row[field] == previous_row[field] for field in ["posting_date", "qi_report_details", "item_code", "batch_no", "qty", "stock_uom"]):
#             formatted_data.append({
#                 "posting_date": "",
#                 "qi_report_details": "",
#                 "item_code": "",
#                 "batch_no": "",
#                 "qty": "",
#                 "stock_uom": "",
#                 "mistake_name": row["mistake_name"],
#                 "total_points": row["total_points"],
#                 "roll_no": "",
#                 "roll_weight": "",
#                 "status": ""
#             })
#         else:
#             formatted_data.append(row)
#             previous_row = row

#     return formatted_data

