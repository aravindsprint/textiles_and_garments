# Copyright (c) 2024, Aravind and contributors
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
        {'fieldname': 'work_order', 'label': 'Work Order', 'fieldtype': 'Link', 'options': 'Work Order'},
        {'fieldname': 'finished_goods', 'label': 'Finished Goods', 'fieldtype': 'Data'},
        {'fieldname': 'requested_qty', 'label': 'Requested Qty', 'fieldtype': 'Float'},
        {'fieldname': 'transferred_qty', 'label': 'Transferred Qty', 'fieldtype': 'Data'},
        {'fieldname': 'fabric_completed_qty', 'label': 'Completed Qty', 'fieldtype': 'Float'},
        {'fieldname': 'fg_stock_uom', 'label': 'UOM', 'fieldtype': 'Data'},
        {'fieldname': 'custom_planned_cost_per_kg', 'label': 'Planned Cost Per Kg', 'fieldtype': 'Float'},
        {'fieldname': 'custom_actual_cost_per_kg', 'label': 'Actual Cost Per Kg', 'fieldtype': 'Float'},
        {'fieldname': 'custom_profit_and_loss', 'label': 'Profit', 'fieldtype': 'Float'},
        # {'fieldname': 'from_date', 'label': 'From Date', 'fieldtype': 'Date'},
        # {'fieldname': 'to_date', 'label': 'To Date', 'fieldtype': 'Date'}
    ]
    return columns


def get_data(filters):
    data = []
    work_order_data = get_work_order_data(filters)
    # Add work order data to the list
    data.extend(work_order_data)
    # Calculate totals for requested_qty, transferred_qty, and fabric_completed_qty
    totals = calculate_totals(work_order_data)
    # Append the totals as a summary row
    # data.append(totals)
    return data


def get_work_order_data(filters):
    # Base query to fetch data from the Work Order
    query = """
        SELECT 
            wo.production_item AS finished_goods,
            wo.qty AS requested_qty,
            wo.material_transferred_for_manufacturing AS transferred_qty,
            wo.produced_qty AS fabric_completed_qty,
            wo.name AS work_order,
            wo.stock_uom AS fg_stock_uom,
            wo.custom_planned_cost_per_kg AS custom_planned_cost_per_kg,
            wo.custom_actual_cost_per_kg AS custom_actual_cost_per_kg,
            wo.custom_profit_and_loss AS custom_profit_and_loss,
            wo.expected_delivery_date AS from_date,
            wo.expected_delivery_date AS to_date
        FROM 
            `tabWork Order` AS wo
        WHERE 
            wo.status = 'Completed'
    """
    
    # Dynamically append additional filter conditions
    conditions = []
    
    if filters.get("finished_goods"):
        conditions.append("wo.production_item LIKE %(finished_goods)s")
    
    if filters.get("work_order"):
        conditions.append("wo.name = %(work_order)s")
    
    if filters.get("stock_uom"):
        conditions.append("wo.stock_uom = %(stock_uom)s")

    if filters.get("to_date"):
        conditions.append("wo.expected_delivery_date <= %(to_date)s")

    if filters.get("from_date"):
        conditions.append("wo.expected_delivery_date >= %(from_date)s")        
    
    # If any conditions were added, append them to the query
    if conditions:
        query += " AND " + " AND ".join(conditions)
        print("\n\n\nquery\n\n\n",query)
    
    # Add filter values to pass as parameters
    filter_values = {
        "finished_goods": filters.get("finished_goods", "%DKF%"),  # Defaults to 'DKF%' if not provided
        "work_order": filters.get("work_order"),
        "stock_uom": filters.get("stock_uom"),
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
    }
    
    # Execute the query with filters
    return frappe.db.sql(query, filter_values, as_dict=1)


def calculate_totals(work_order_data):
    # Initialize total counters
    total_requested_qty = 0
    total_transferred_qty = 0
    total_completed_qty = 0

    # Iterate over the work order data to calculate totals
    for row in work_order_data:
        total_requested_qty += row.get('requested_qty', 0)
        total_transferred_qty += row.get('transferred_qty', 0)
        total_completed_qty += row.get('fabric_completed_qty', 0)

    # Return a summary row with totals (no work_order, finished_goods, or uom in the totals row)
    return {
        'work_order': 'Total',  # Label row as "Total"
        'finished_goods': '',
        'requested_qty': total_requested_qty,
        'transferred_qty': total_transferred_qty,
        'fabric_completed_qty': total_completed_qty,
        'fg_stock_uom': '',
        'expected_delivery_date': ''
    }

    







# def execute(filters=None):
#     # Define the columns for the report
#     columns = [
#         {'fieldname': 'work_order', 'label': 'Work Order', 'fieldtype': 'Link', 'options': 'Work Order'},
#         {'fieldname': 'finished_goods', 'label': 'Finished Goods', 'fieldtype': 'Data'},
#         {'fieldname': 'requested_qty', 'label': 'Requested Qty', 'fieldtype': 'Float'},
#         {'fieldname': 'transferred_qty', 'label': 'Transferred Qty', 'fieldtype': 'Data'},
#         {'fieldname': 'fabric_completed_qty', 'label': 'Completed Qty', 'fieldtype': 'Float'},
#          # New column for required quantity
#         {'fieldname': 'fg_stock_uom', 'label': 'UOM', 'fieldtype': 'Data'}
#     ]

#     # Initialize data list
#     data = []

#     # SQL query to fetch Work Order Items and related Dye Recipe Items
#     parent = frappe.db.sql("""
#     SELECT 
#         wo.production_item AS finished_goods,
#         wo.qty AS requested_qty,
#         wo.material_transferred_for_manufacturing AS transferred_qty,
#         wo.produced_qty AS fabric_completed_qty,
#         wo.name AS work_order,
#         wo.stock_uom AS fg_stock_uom
#     FROM 
#         `tabWork Order` AS wo
#     WHERE 
#         wo.status = 'Completed'
#         AND wo.production_item LIKE 'DKF%'
#     """, as_dict=1)


#     data.extend(parent)

#     return columns, data