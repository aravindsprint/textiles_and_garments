# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today
import json


class RollWisePickList(Document):
	pass


# @frappe.whitelist()
# def get_stock_details(docname, warehouse):
#     if not warehouse:
#         return []
    

#     filters = frappe._dict({
#         "warehouse": warehouse,
#     })

#     batchwise_data = get_batchwise_data_from_stock_ledger(filters)
#     batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)
#     data = parse_batchwise_data(batchwise_data)

#     # Filter data based on search_batch if provided
#     # if search_batch:
#     #     search_batches = [b.strip() for b in search_batch.split(',')]
#     #     data = [row for row in data if row.get("batch_no") in search_batches]

#     print("\n\ndata\n\n", data)
#     # Extract only unique batch numbers
#     unique_batches = list({d.get("batch_no") for d in data if d.get("batch_no")})

#     print("\n\nunique_batches\n\n", unique_batches)

#     return unique_batches
#     # return data


@frappe.whitelist()
def get_filtered_rolls(warehouse):
    if not warehouse:
        return []

    filters = frappe._dict({
        "warehouse": warehouse,
    })

    batchwise_data = get_batchwise_data_from_stock_ledger(filters)
    batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)
    data = parse_batchwise_data(batchwise_data)

    unique_batches = list({d.get("batch_no") for d in data if d.get("batch_no")})

    # Fetch Rolls with batch in unique_batches
    rolls = frappe.get_all(
        "Roll",
        filters={
            "batch": ["in", unique_batches],
            # "warehouse": warehouse
        },
        fields=["name", "item_code", "batch", "roll_weight", "stock_uom"]
    )

    return rolls

def parse_batchwise_data(batchwise_data):
    data = []
    for key in batchwise_data:
        d = batchwise_data[key]
        if flt(d.balance_qty) == 0:
            continue
        data.append(d)
    return data


def get_batchwise_data_from_stock_ledger(filters):
    batchwise_data = frappe._dict()
    table = frappe.qb.DocType("Stock Ledger Entry")
    batch = frappe.qb.DocType("Batch")
    item = frappe.qb.DocType("Item")

    query = (
        frappe.qb.from_(table)
        .inner_join(batch).on(table.batch_no == batch.name)
        .inner_join(item).on(table.item_code == item.name)
        .select(
            table.item_code,
            table.warehouse,
            table.batch_no,
            item.stock_uom,
            Sum(table.actual_qty).as_("balance_qty"),
        )
        .where(table.is_cancelled == 0)
        .groupby(table.item_code, table.warehouse, table.batch_no, item.stock_uom)
    )

    if filters.get("item_codes"):
        query = query.where(table.item_code.isin(filters.item_codes))

    for d in query.run(as_dict=True):
        key = (d.item_code, d.warehouse, d.batch_no)
        batchwise_data.setdefault(key, d)

    return batchwise_data


def get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters):
    table = frappe.qb.DocType("Stock Ledger Entry")
    ch_table = frappe.qb.DocType("Serial and Batch Entry")
    batch = frappe.qb.DocType("Batch")
    item = frappe.qb.DocType("Item")

    query = (
        frappe.qb.from_(table)
        .inner_join(ch_table).on(table.serial_and_batch_bundle == ch_table.parent)
        .inner_join(batch).on(ch_table.batch_no == batch.name)
        .inner_join(item).on(table.item_code == item.name)
        .select(
            table.item_code,
            ch_table.warehouse,
            ch_table.batch_no,
            item.stock_uom,
            Sum(ch_table.qty).as_("balance_qty"),
        )
        .where((table.is_cancelled == 0) & (table.docstatus == 1))
        .groupby(table.item_code, ch_table.warehouse, ch_table.batch_no, item.stock_uom)
    )

    if filters.get("item_codes"):
        query = query.where(table.item_code.isin(filters.item_codes))

    for d in query.run(as_dict=True):
        key = (d.item_code, d.warehouse, d.batch_no)
        if key in batchwise_data:
            batchwise_data[key].balance_qty += flt(d.balance_qty)
        else:
            batchwise_data.setdefault(key, d)

    return batchwise_data

