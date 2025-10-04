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
    columns = [
    ]

    if filters.show_item_name:
        columns.append(
            {
                "label": _("Item Name"),
                "fieldname": "item_name",
                "fieldtype": "Link",
                "options": "Item",
                "width": 200,
            }
        )

    columns.extend(
        [
            {
                "label": _("Workstation"),
                "fieldname": "workstation",
                "fieldtype": "Link",
                "options": "Workstation",
                "width": 200,
            },
            {
                "label": _("Item Code"),
                "fieldname": "item_code",
                "fieldtype": "Data",
                "width": 200,
            },
            {
                "label": _("Job Card"),
                "fieldname": "job_card",
                "fieldtype": "Link",
                "options": "Job Card",
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
            "label": _("JobCard Fabric qty"),
            "fieldname": "for_qty",
            "fieldtype": "Float",
            "width": 200,
            },
            {
            "label": _("JobCard Trims qty"),
            "fieldname": "custom_add_on_qty",
            "fieldtype": "Float",
            "width": 200,
            },
            {
            "label": _("Completed Qty"),
            "fieldname": "total_completed_qty",
            "fieldtype": "Float",
            "width": 200,
            },
            {
                "label": _("Job Card Completed Date"),
                "fieldname": "completed_date",
                "fieldtype": "Date",
                "width": 150,
            },
            {
                "label": _("UOM"),
                "fieldname": "stock_uom",
                "fieldtype": "Data",
                "width": 150
            },
       ]
    )

    return columns

def get_data(filters):
    data = []
    job_card_data = get_job_card_data_from_stock_entry(filters)
    print("\n\n\njob_card_data\n\n\n", job_card_data)
    data.extend(job_card_data)
    return data


def get_job_card_data_from_stock_entry(filters):
    # Base query to fetch data from Job Card and related tables
    query = """
        SELECT 
            job_card.production_item AS item_code,
            job_card.work_order AS work_order,
            job_card.name AS job_card,
            job_card.wip_warehouse AS wip_warehouse,
            job_card.for_quantity AS for_qty,
            job_card.total_completed_qty AS total_completed_qty,
            job_card.workstation AS workstation,
            job_card.custom_completed_date AS completed_date,
            job_card.custom_add_on_qty AS custom_add_on_qty
        FROM 
            `tabJob Card` AS job_card
        LEFT JOIN 
            `tabWork Order` AS wo
        ON 
            job_card.work_order = wo.name
        WHERE 
            job_card.status = "Completed"
            AND job_card.workstation LIKE "HTHP Soft Flow(SP)%%" 
            AND job_card.docstatus = 1
    """

    # Dynamically append additional filter conditions
    conditions = []
    filter_values = {}

    if filters.get("item_code"):
        conditions.append("job_card.production_item = %(item_code)s")
        filter_values["item_code"] = filters.get("item_code")
    
    if filters.get("work_order"):
        conditions.append("job_card.work_order = %(work_order)s")
        filter_values["work_order"] = filters.get("work_order")
    
    if filters.get("workstation"):
        conditions.append("job_card.workstation LIKE %(workstation)s")
        filter_values["workstation"] = f"%{filters.get('workstation')}%"
    
    if filters.get("from_date"):
        conditions.append("job_card.custom_completed_date >= %(from_date)s")
        filter_values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("job_card.custom_completed_date <= %(to_date)s")
        filter_values["to_date"] = filters.get("to_date")

    if filters.get("item_name"):
        conditions.append("wo.production_item = %(item_name)s")
        filter_values["item_name"] = filters.get("item_name")

    # If conditions were added, append them to the query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Execute the query with filters
    return frappe.db.sql(query, filter_values, as_dict=1)
    

# def get_job_card_data_from_stock_entry(filters):
#     # Base query to fetch data from Job Card and related tables
#     query = """
#         SELECT 
#             job_card.production_item AS item_code,
#             job_card.work_order AS work_order,
#             job_card.name AS job_card,
#             job_card.wip_warehouse AS wip_warehouse,
#             job_card.for_quantity AS for_qty,
#             job_card.total_completed_qty AS total_completed_qty,
#             job_card.workstation AS workstation,
#             job_card.custom_completed_date AS completed_date,
#             job_card.custom_add_on_qty AS custom_add_on_qty
#         FROM 
#             `tabJob Card` AS job_card
#         LEFT JOIN 
#             `tabWork Order` AS wo
#         ON 
#             job_card.work_order = wo.name
#         WHERE 
#             job_card.status = "Completed"
#             AND job_card.workstation LIKE "HTHP Soft Flow(SP)%" 
#             AND job_card.docstatus = 1
#     """

#     # Dynamically append additional filter conditions
#     conditions = []

#     if filters.get("item_code"):
#         conditions.append("job_card.production_item = %(item_code)s")
    
#     if filters.get("work_order"):
#         conditions.append("job_card.work_order = %(work_order)s")
    
#     if filters.get("workstation"):
#         conditions.append("job_card.workstation LIKE %(workstation)s")
    
#     if filters.get("from_date"):
#         conditions.append("job_card.custom_completed_date >= %(from_date)s")

#     if filters.get("to_date"):
#         conditions.append("job_card.custom_completed_date <= %(to_date)s")

#     if filters.get("item_name"):
#         conditions.append("wo.production_item = %(item_name)s")  # Assuming a relationship with Work Order's production item

#     # If conditions were added, append them to the query
#     if conditions:
#         query += " AND " + " AND ".join(conditions)

#     # Define filter values to pass as parameters
#     filter_values = {
#         "item_code": filters.get("item_code"),
#         "work_order": filters.get("work_order"),
#         "workstation": '%' + filters.get("workstation", '') + '%',  # Supports partial matching
#         "from_date": filters.get("from_date"),
#         "to_date": filters.get("to_date"),
#         "item_name": filters.get("item_name"),
#     }
    
#     # Execute the query with filters
#     return frappe.db.sql(query, filter_values, as_dict=1)



# def get_job_card_data_from_stock_entry(filters):
#     # job_card.completed_date AS completed_date,
#     job_card_data = frappe.db.sql("""
#         SELECT 
#             job_card.production_item AS item_code,
#             job_card.work_order AS work_order,
#             job_card.name AS job_card,
#             job_card.wip_warehouse AS wip_warehouse,
#             job_card.for_quantity AS for_qty,
#             job_card.total_completed_qty AS total_completed_qty,
#             job_card.workstation AS workstation,
#             job_card.completed_date AS completed_date,
#             job_card.custom_add_on_qty AS custom_add_on_qty
#         FROM 
#             `tabJob Card` AS job_card
#         LEFT JOIN 
#             `tabWork Order` AS wo
#         ON 
#             job_card.work_order = wo.name
#         WHERE 
#             job_card.status = "Completed" 
#             AND job_card.docstatus = 1
#             AND job_card.production_item LIKE '%KF%/%'
#             AND job_card.workstation LIKE "HTHP Softflow%"
#     """, as_dict=1)

#     return job_card_data






  
