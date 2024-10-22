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
    
    # Get data for both tables
    work_order_data = get_work_order_data(filters)
    stock_entry_data = get_stock_entry_data(filters)
    
    # Combine both sets of data with labels
    data = []
    
    # Insert a label row for "Work Orders"
    data.append({'section_label': 'Work Orders'})
    data.extend(work_order_data)  # Add work order data

    # Insert a label row for "Stock Entries"
    data.append({'section_label': 'Stock Entries'})
    data.extend(stock_entry_data)  # Add stock entry data
    
    # Define columns for both tables
    columns = get_columns()

    return columns, data

def get_columns():
    return [
        # Columns for the first table (Work Orders)
        {'fieldname': 'work_order', 'label': 'Work Order', 'fieldtype': 'Link', 'options': 'Work Order'},
        {'fieldname': 'finished_goods', 'label': 'Finished Goods', 'fieldtype': 'Data'},
        {'fieldname': 'requested_qty', 'label': 'Requested Qty', 'fieldtype': 'Float'},
        {'fieldname': 'transferred_qty', 'label': 'Transferred Qty', 'fieldtype': 'Data'},
        {'fieldname': 'fabric_completed_qty', 'label': 'Completed Qty', 'fieldtype': 'Float'},
        {'fieldname': 'fg_stock_uom', 'label': 'UOM', 'fieldtype': 'Data'},
        {'fieldname': 'from_date', 'label': 'From Date', 'fieldtype': 'Date'},
        {'fieldname': 'to_date', 'label': 'To Date', 'fieldtype': 'Date'},

        # Columns for the second table (Stock Entries)
        {'fieldname': 'stock_entry', 'label': 'Stock Entry', 'fieldtype': 'Link', 'options': 'Stock Entry'},
        {'fieldname': 'stock_entry_type', 'label': 'Stock Entry Type', 'fieldtype': 'Data'},
        {'fieldname': 'from_date', 'label': 'From Date', 'fieldtype': 'Date'},
        {'fieldname': 'to_date', 'label': 'To Date', 'fieldtype': 'Date'}
    ]

def get_work_order_data(filters):
    query = """
        SELECT 
            wo.production_item AS finished_goods,
            wo.qty AS requested_qty,
            wo.material_transferred_for_manufacturing AS transferred_qty,
            wo.produced_qty AS fabric_completed_qty,
            wo.name AS work_order,
            wo.stock_uom AS fg_stock_uom,
            wo.expected_delivery_date AS from_date,
            wo.expected_delivery_date AS to_date
        FROM 
            `tabWork Order` AS wo
        WHERE 
            wo.status = 'Completed'
    """
    return frappe.db.sql(query, filters, as_dict=1)

def get_stock_entry_data(filters):
    query = """
        SELECT 
            wo.name AS stock_entry,
            wo.stock_entry_type AS stock_entry_type,
            wo.posting_date AS from_date,
            wo.posting_date AS to_date
        FROM 
            `tabStock Entry` AS wo
        WHERE 
            wo.docstatus = 'Submitted'
    """
    return frappe.db.sql(query, filters, as_dict=1)

