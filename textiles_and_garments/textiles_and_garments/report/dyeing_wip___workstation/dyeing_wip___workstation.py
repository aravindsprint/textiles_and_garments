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
    
    # Get stock entry data with ste_qty
    # stock_entry_data = get_stock_entry_detail_data_from_stock_entry(filters)
    # print("\n\n\nstock_entry_data\n\n\n", stock_entry_data)

    job_card_data = get_job_card_data_from_stock_entry(filters)
    print("\n\n\njob_card_data\n\n\n", job_card_data)
    
    # # Get batch-wise stock data
    # batchwise_data = get_batchwise_data_from_stock_ledger(filters)
    # batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)

    # # Parse batch-wise data to include only 'Work In Progress - PSS' warehouse
    # stock_data = parse_batchwise_data(batchwise_data)
    
    # # Combine stock entry data with balance_qty
    # final_data = combine_stock_and_batchwise_data(stock_entry_data, stock_data)

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



def get_batchwise_data_from_stock_ledger(filters):
    batchwise_data = frappe._dict({})

    table = frappe.qb.DocType("Stock Ledger Entry")
    batch = frappe.qb.DocType("Batch")

    query = (
        frappe.qb.from_(table)
        .inner_join(batch)
        .on(table.batch_no == batch.name)
        .select(
            table.item_code,
            table.batch_no,
            table.warehouse,
            Sum(table.actual_qty).as_("balance_qty"),
        )
        .where(table.is_cancelled == 0)
        .groupby(table.batch_no, table.item_code, table.warehouse)
    )

    query = get_query_based_on_filters(query, batch, table, filters)

    for d in query.run(as_dict=True):
        key = (d.item_code, d.warehouse, d.batch_no)
        batchwise_data.setdefault(key, d)

    return batchwise_data

def get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters):
    table = frappe.qb.DocType("Stock Ledger Entry")
    ch_table = frappe.qb.DocType("Serial and Batch Entry")
    batch = frappe.qb.DocType("Batch")

    query = (
        frappe.qb.from_(table)
        .inner_join(ch_table)
        .on(table.serial_and_batch_bundle == ch_table.parent)
        .inner_join(batch)
        .on(ch_table.batch_no == batch.name)
        .select(
            table.item_code,
            ch_table.batch_no,
            table.warehouse,
            Sum(ch_table.qty).as_("balance_qty"),
        )
        .where((table.is_cancelled == 0) & (table.docstatus == 1))
        .groupby(ch_table.batch_no, table.item_code, ch_table.warehouse)
    )

    query = get_query_based_on_filters(query, batch, table, filters)

    for d in query.run(as_dict=True):
        key = (d.item_code, d.warehouse, d.batch_no)
        if key in batchwise_data:
            batchwise_data[key].balance_qty += flt(d.balance_qty)
        else:
            batchwise_data.setdefault(key, d)

    return batchwise_data

def get_query_based_on_filters(query, batch, table, filters):
    if filters.item_code:
        query = query.where(table.item_code == filters.item_code)

    if filters.batch_no:
        query = query.where(batch.name == filters.batch_no)

    if not filters.include_expired_batches:
        query = query.where((batch.expiry_date >= today()) | (batch.expiry_date.isnull()))
        if filters.to_date == today():
            query = query.where(batch.batch_qty > 0)

    if filters.warehouse:
        lft, rgt = frappe.db.get_value("Warehouse", filters.warehouse, ["lft", "rgt"])
        warehouses = frappe.get_all(
            "Warehouse", filters={"lft": (">=", lft), "rgt": ("<=", rgt), "is_group": 0}, pluck="name"
        )

        query = query.where(table.warehouse.isin(warehouses))

    elif filters.warehouse_type:
        warehouses = frappe.get_all(
            "Warehouse", filters={"warehouse_type": filters.warehouse_type, "is_group": 0}, pluck="name"
        )

        query = query.where(table.warehouse.isin(warehouses))

    if filters.show_item_name:
        query = query.select(batch.item_name)

    return query

def parse_batchwise_data(batchwise_data):
    data = []
    for key in batchwise_data:
        # Check if the second element in the tuple matches 'Work In Progress - PSS'
        if key[1] == "Work In Progress - PSS":
            d = batchwise_data[key]
            # Continue only if balance_qty is not 0
            if d.balance_qty != 0:
                data.append(d)

    return data

def combine_stock_and_batchwise_data(stock_entry_data, batchwise_data):
    final_data = []
    
    for ste in stock_entry_data:
        # Find matching batchwise data by item_code and batch_no
        for batch in batchwise_data:
            if ste['item_code'] == batch['item_code'] and ste['batch_no'] == batch['batch_no']:
                # Add ste_qty and balance_qty together
                ste['balance_qty'] = batch['balance_qty']
                final_data.append(ste)
    
    return final_data    
