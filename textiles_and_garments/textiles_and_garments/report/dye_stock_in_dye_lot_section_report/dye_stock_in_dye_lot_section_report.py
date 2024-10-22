# Copyright (c) 2024, Aravind and contributors
# For license information, please see license.txt

# import frappe


# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
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
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 200,
        },
        {
            "label": _("Commercial Name"),
            "fieldname": "custom_commercial_name",
            "fieldtype": "Data",
            "width": 200,
        }
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
                "label": _("Warehouse"),
                "fieldname": "warehouse",
                "fieldtype": "Link",
                "options": "Warehouse",
                "width": 200,
            },
            {
                "label": _("Batch No"),
                "fieldname": "batch_no",
                "fieldtype": "Link",
                "width": 150,
                "options": "Batch",
            },
            {
                "label": _("UOM"),
                "fieldname": "stock_uom",
                "fieldtype": "Link",
                "width": 150,
                "options": "UOM",
            },
            {"label": _("Balance Qty"), "fieldname": "balance_qty", "fieldtype": "Float", "width": 150},
        ]
    )

    return columns


def get_data(filters):
    data = []
    batchwise_data = get_batchwise_data_from_stock_ledger(filters)
    print("\n\n\nbatchwise_data\n\n\n", batchwise_data)
    batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)

    data = parse_batchwise_data(batchwise_data)
    print("\n\n\ndata\n\n\n", data)

    return data


def parse_batchwise_data(batchwise_data):
    data = []
    for key in batchwise_data:
        d = batchwise_data[key]
        if d.balance_qty == 0:
            continue

        data.append(d)

    return data




def get_batchwise_data_from_stock_ledger(filters):
    batchwise_data = frappe._dict({})

    table = frappe.qb.DocType("Stock Ledger Entry")
    batch = frappe.qb.DocType("Batch")
    item = frappe.qb.DocType("Item")  # Reference to the Item table

    query = (
        frappe.qb.from_(table)
        .inner_join(batch)
        .on(table.batch_no == batch.name)
        .inner_join(item)  # Join the Item table
        .on(table.item_code == item.item_code)  # Match item_code
        .select(
            table.item_code,
            item.custom_commercial_name,  # Include commercial_name from the Item table
            table.batch_no,
            table.stock_uom,
            table.warehouse,
            Sum(table.actual_qty).as_("balance_qty"),
        )
        .where(table.is_cancelled == 0)
        .where(table.item_code.like('DKF%'))  # Ensure item_code starts with GKF
        .where(table.warehouse.like("DYE/LOT%"))  # Filter for "DYE/LOT SECTION"
        .groupby(table.batch_no, table.item_code, table.warehouse)
    )

    # Pass the `item` argument here
    query = get_query_based_on_filters(query, batch, table, filters, item)

    for d in query.run(as_dict=True):
        key = (d.item_code, d.warehouse, d.batch_no, d.stock_uom)
        batchwise_data.setdefault(key, d)

    return batchwise_data


def get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters):
    table = frappe.qb.DocType("Stock Ledger Entry")
    ch_table = frappe.qb.DocType("Serial and Batch Entry")
    batch = frappe.qb.DocType("Batch")
    item = frappe.qb.DocType("Item")  # Join the Item table

    query = (
        frappe.qb.from_(table)
        .inner_join(ch_table)
        .on(table.serial_and_batch_bundle == ch_table.parent)
        .inner_join(batch)
        .on(ch_table.batch_no == batch.name)
        .inner_join(item)  # Join the Item table
        .on(table.item_code == item.item_code)  # Match item_code
        .select(
            table.item_code,
            item.custom_commercial_name,  # Fetch commercial_name from Item table
            ch_table.batch_no,
            table.warehouse,
            table.stock_uom,
            Sum(ch_table.qty).as_("balance_qty"),
        )
        .where((table.is_cancelled == 0) & (table.docstatus == 1))
        .where(table.item_code.like('DKF%'))  # Ensure item_code starts with GKF
        .where(table.warehouse.like("DYE/LOT%"))  # Filter for "DYE/LOT SECTION"
        .groupby(ch_table.batch_no, table.item_code, ch_table.warehouse)
    )

    query = get_query_based_on_filters(query, batch, table, filters, item)

    for d in query.run(as_dict=True):
        key = (d.item_code, d.warehouse, d.batch_no, d.stock_uom)
        if key in batchwise_data:
            batchwise_data[key].balance_qty += flt(d.balance_qty)
        else:
            batchwise_data.setdefault(key, d)

    return batchwise_data


def get_query_based_on_filters(query, batch, table, filters, item):
    if filters.item_code:
        query = query.where(table.item_code == filters.item_code)

    # Apply the like condition for custom_commercial_name filter
    if filters.custom_commercial_name:
        query = query.where(item.custom_commercial_name.like(f"%{filters.custom_commercial_name}%"))

    if filters.batch_no:
        query = query.where(batch.name == filters.batch_no)

    if filters.show_item_name:
        query = query.select(batch.item_name)

    return query


# def get_batchwise_data_from_stock_ledger(filters):
#     query = """
#         SELECT 
#             sle.item_code,
#             i.custom_commercial_name,
#             sle.batch_no,
#             sle.stock_uom,
#             sle.warehouse,
#             SUM(sle.actual_qty) AS balance_qty
#         FROM 
#             `tabStock Ledger Entry` sle
#         INNER JOIN 
#             `tabBatch` b ON sle.batch_no = b.name
#         INNER JOIN 
#             `tabItem` i ON sle.item_code = i.item_code
#         WHERE 
#             sle.is_cancelled = 0
#             AND sle.item_code LIKE 'DKF%'
#             AND sle.warehouse LIKE 'DYE/LOT%'
#         GROUP BY 
#             sle.batch_no, sle.item_code, sle.warehouse
#     """

#     # Apply filters if any
#     if filters:
#         # You might want to modify the query further based on your filters
#         query += get_query_based_on_filters_sql(filters)

#     # Execute the query and fetch results
#     batchwise_data = frappe.db.sql(query, as_dict=True)

#     # Create a structured dictionary for batchwise data
#     result_dict = frappe._dict({})
#     for d in batchwise_data:
#         key = (d.item_code, d.warehouse, d.batch_no, d.stock_uom)
#         result_dict.setdefault(key, d)

#     return result_dict


# def get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters):
#     query = """
#         SELECT 
#             sle.item_code,
#             i.custom_commercial_name,
#             c.batch_no,
#             sle.warehouse,
#             sle.stock_uom,
#             SUM(c.qty) AS balance_qty
#         FROM 
#             `tabStock Ledger Entry` sle
#         INNER JOIN 
#             `tabSerial and Batch Entry` c ON sle.serial_and_batch_bundle = c.parent
#         INNER JOIN 
#             `tabBatch` b ON c.batch_no = b.name
#         INNER JOIN 
#             `tabItem` i ON sle.item_code = i.item_code
#         WHERE 
#             sle.is_cancelled = 0
#             AND sle.docstatus = 1
#             AND sle.item_code LIKE 'DKF%'
#             AND sle.warehouse LIKE 'DYE/LOT%'
#         GROUP BY 
#             c.batch_no, sle.item_code, sle.warehouse
#     """

#     # Apply filters if any
#     if filters:
#         query += get_query_based_on_filters_sql(filters)

#     # Execute the query and fetch results
#     batchwise_data_sql = frappe.db.sql(query, as_dict=True)

#     # Update existing batchwise_data
#     for d in batchwise_data_sql:
#         key = (d.item_code, d.warehouse, d.batch_no, d.stock_uom)
#         if key in batchwise_data:
#             batchwise_data[key].balance_qty += flt(d.balance_qty)
#         else:
#             batchwise_data.setdefault(key, d)

#     return batchwise_data


# def get_query_based_on_filters_sql(filters):
#     conditions = []

#     if filters.item_code:
#         conditions.append(f"sle.item_code = '{filters.item_code}'")

#     if filters.custom_commercial_name:
#         conditions.append(f"i.custom_commercial_name LIKE '%{filters.custom_commercial_name}%'")

#     if filters.batch_no:
#         conditions.append(f"b.name = '{filters.batch_no}'")

#     if filters.show_item_name:
#         # Assuming you want to add item_name to the select statement if show_item_name is True
#         # You might need to modify the select statement accordingly in the main query
#         pass 

#     return " AND " + " AND ".join(conditions) if conditions else ""





