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
        # {
        #     "label": _("Item Code"),
        #     "fieldname": "item_code",
        #     "fieldtype": "Link",
        #     "options": "Item",
        #     "width": 200,
        # }
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
                "label": _("Job Card Created Date"),
                "fieldname": "posting_date",
                "fieldtype": "Date",
                "width": 150,
            },
            # {
            #     "label": _("Job Card Start Date"),
            #     "fieldname": "actual_start_date",
            #     "fieldtype": "Date",
            #     "width": 150
            # },
            {
                "label": _("UOM"),
                "fieldname": "stock_uom",
                "fieldtype": "Data",
                "width": 150
            },
            # {"label": _("Balance Qty"), "fieldname": "balance_qty", "fieldtype": "Float", "width": 150},
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
    job_card_data = frappe.db.sql("""
        SELECT 
            job_card.production_item AS item_code,
            job_card.work_order AS work_order,
            job_card.name AS job_card,
            job_card.wip_warehouse AS wip_warehouse,
            job_card.for_quantity AS for_qty,
            job_card.total_completed_qty AS total_completed_qty,
            job_card.workstation AS workstation,
            job_card.stock_uom AS stock_uom,
            job_card.posting_date AS posting_date,
            job_card.custom_add_on_qty AS custom_add_on_qty
        FROM 
            `tabJob Card` AS job_card
        LEFT JOIN 
            `tabWork Order` AS wo
        ON 
            job_card.work_order = wo.name
        WHERE 
            job_card.status = "Work In Progress" 
            AND job_card.docstatus != 2
            AND job_card.production_item LIKE '%KF%/%'
            AND job_card.workstation LIKE "HTHP Softflow%"
    """, as_dict=1)

    return job_card_data






  
