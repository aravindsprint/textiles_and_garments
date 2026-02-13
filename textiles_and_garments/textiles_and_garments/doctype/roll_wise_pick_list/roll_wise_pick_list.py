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
# def get_filtered_rolls(warehouse,batch):
#     print("\n\nbatch\n\n", batch)
#     if not warehouse:
#         return []

#     filters = frappe._dict({
#         "warehouse": warehouse,
#     })

#     batchwise_data = get_batchwise_data_from_stock_ledger(filters)
#     batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)
#     data = parse_batchwise_data(batchwise_data)

#     print("\n\ndata\n\n",data )

#     unique_batches = list({d.get("batch_no") for d in data if d.get("batch_no")})
#     print("\n\nunique_batches\n\n", unique_batches)

#     # Fetch Rolls with batch in unique_batches
#     rolls = frappe.get_all(
#         "Roll",
#         # filters={
#         #     "batch": ["in", unique_batches],
#         #     # "warehouse": warehouse
#         # },
#         filters={
#             "batch": ["in", batch],
#             # "warehouse": warehouse
#         },
#         fields=["name", "item_code", "batch", "roll_weight", "stock_uom"]
#     )
#     print("\n\nrolls\n\n", rolls)

#     return rolls

# def parse_batchwise_data(batchwise_data):
#     data = []
#     for key in batchwise_data:
#         d = batchwise_data[key]
#         if flt(d.balance_qty) == 0:
#             continue
#         data.append(d)
#     return data


# def get_batchwise_data_from_stock_ledger(filters):
#     batchwise_data = frappe._dict()
#     table = frappe.qb.DocType("Stock Ledger Entry")
#     batch = frappe.qb.DocType("Batch")
#     item = frappe.qb.DocType("Item")

#     query = (
#         frappe.qb.from_(table)
#         .inner_join(batch).on(table.batch_no == batch.name)
#         .inner_join(item).on(table.item_code == item.name)
#         .select(
#             table.item_code,
#             table.warehouse,
#             table.batch_no,
#             item.stock_uom,
#             Sum(table.actual_qty).as_("balance_qty"),
#         )
#         .where(table.is_cancelled == 0)
#         .groupby(table.item_code, table.warehouse, table.batch_no, item.stock_uom)
#     )

#     print("\n\nfilters\n\n", filters)

#     # Apply item_code filter if present
#     if filters.get("item_codes"):
#         query = query.where(table.item_code.isin(filters.item_codes))

#     # ✅ Apply warehouse filter if present
#     if filters.get("warehouse"):
#         query = query.where(table.warehouse == filters.warehouse)

#     for d in query.run(as_dict=True):
#         key = (d.item_code, d.warehouse, d.batch_no)
#         batchwise_data.setdefault(key, d)
    
#     print("\n\nbatchwise_data\n\n",batchwise_data)
#     return batchwise_data



# def get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters):
#     table = frappe.qb.DocType("Stock Ledger Entry")
#     ch_table = frappe.qb.DocType("Serial and Batch Entry")
#     batch = frappe.qb.DocType("Batch")
#     item = frappe.qb.DocType("Item")

#     query = (
#         frappe.qb.from_(table)
#         .inner_join(ch_table).on(table.serial_and_batch_bundle == ch_table.parent)
#         .inner_join(batch).on(ch_table.batch_no == batch.name)
#         .inner_join(item).on(table.item_code == item.name)
#         .select(
#             table.item_code,
#             ch_table.warehouse,
#             ch_table.batch_no,
#             item.stock_uom,
#             Sum(ch_table.qty).as_("balance_qty"),
#         )
#         .where((table.is_cancelled == 0) & (table.docstatus == 1))
#         .groupby(table.item_code, ch_table.warehouse, ch_table.batch_no, item.stock_uom)
#     )

#     # ✅ Apply item_code filter if present
#     if filters.get("item_codes"):
#         query = query.where(table.item_code.isin(filters.item_codes))

#     # ✅ Apply warehouse filter if present
#     if filters.get("warehouse"):
#         query = query.where(ch_table.warehouse == filters.warehouse)

#     for d in query.run(as_dict=True):
#         key = (d.item_code, d.warehouse, d.batch_no)
#         if key in batchwise_data:
#             batchwise_data[key].balance_qty += flt(d.balance_qty)
#         else:
#             batchwise_data.setdefault(key, d)
    
#     print("\n\nbatchwise_data\n\n",batchwise_data)
#     return batchwise_data


# @frappe.whitelist()
# def get_sales_invoice_items(sales_invoice):
#     """Fetch all items from the given sales invoice."""
#     if not sales_invoice:
#         return []

#     items = frappe.get_all(
#         "Sales Invoice Item",
#         filters={"parent": sales_invoice},
#         fields=["item_code", "warehouse", "qty", "rate", "amount"]
#     )
#     return items


@frappe.whitelist()
def get_filtered_rolls(warehouse, batch):
    if not warehouse:
        return []

    filters = frappe._dict({
        "warehouse": warehouse,
    })

    batchwise_data = get_batchwise_data_from_stock_ledger(filters)
    batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)
    data = parse_batchwise_data(batchwise_data)

    # Get unique batch numbers from available stock data
    unique_batches = list({d.get("batch_no") for d in data if d.get("batch_no")})

    # Get all roll names used in submitted QI Report Details > roll_details
    used_rolls = frappe.get_all(
        "Roll Details",
        filters={"parenttype": "QI Report Details", "docstatus": 1},
        fields=["roll_no"]
    )
    used_roll_names = [d.roll_no for d in used_rolls if d.roll_no]

    print("\n\nused_rolls\n\n", used_rolls)
    print("\n\nused_roll_names\n\n",used_roll_names)

    # Filter Rolls
    roll_filters = {
        "batch": ["in", batch if isinstance(batch, list) else [batch]],
        "name": ["in", used_roll_names]
    }

    rolls = frappe.get_all(
        "Roll",
        filters=roll_filters,
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

    print("\n\nfilters\n\n", filters)

    # Apply item_code filter if present
    if filters.get("item_codes"):
        query = query.where(table.item_code.isin(filters.item_codes))

    # ✅ Apply warehouse filter if present
    if filters.get("warehouse"):
        query = query.where(table.warehouse == filters.warehouse)

    for d in query.run(as_dict=True):
        key = (d.item_code, d.warehouse, d.batch_no)
        batchwise_data.setdefault(key, d)
    
    print("\n\nbatchwise_data\n\n",batchwise_data)
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

    # ✅ Apply item_code filter if present
    if filters.get("item_codes"):
        query = query.where(table.item_code.isin(filters.item_codes))

    # ✅ Apply warehouse filter if present
    if filters.get("warehouse"):
        query = query.where(ch_table.warehouse == filters.warehouse)

    for d in query.run(as_dict=True):
        key = (d.item_code, d.warehouse, d.batch_no)
        if key in batchwise_data:
            batchwise_data[key].balance_qty += flt(d.balance_qty)
        else:
            batchwise_data.setdefault(key, d)
    
    print("\n\nbatchwise_data\n\n",batchwise_data)
    return batchwise_data    


# @frappe.whitelist()
# def get_filtered_rolls(warehouse, parent_warehouse):
#     print("\n\nwarehouse\n\n", warehouse)
#     print("\n\nparent_warehouse\n\n", parent_warehouse)
#     if not warehouse and not parent_warehouse:
#         return []

#     filters = frappe._dict({
#         "warehouse": warehouse,
#         "parent_warehouse": parent_warehouse
#     })

#     batchwise_data = get_batchwise_data_from_stock_ledger(filters)
#     batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)
#     print("\n\nbatchwise_data\n\n", batchwise_data)
#     data = parse_batchwise_data(batchwise_data)

#     # Create a mapping from (item_code, batch_no) to parent_warehouse and warehouse
#     warehouse_map = {
#         (d.get("item_code"), d.get("batch_no")): {
#             "parent_warehouse": d.get("parent_warehouse"),
#             "warehouse": d.get("warehouse")  # assuming "warehouse" field exists in d
#         }
#         for d in data if d.get("batch_no")
#     }

#     unique_batches = list(warehouse_map.keys())

#     print("\n\nunique_batches\n\n", unique_batches)

#     rolls = frappe.get_all(
#         "Roll",
#         filters={
#             "batch": ["in", [b for _, b in unique_batches]],
#         },
#         fields=["name", "item_code", "batch", "roll_weight", "stock_uom"]
#     )

#     # Append parent_warehouse and warehouse to each roll
#     for roll in rolls:
#         key = (roll.item_code, roll.batch)
#         mapped = warehouse_map.get(key, {})
#         roll["parent_warehouse"] = mapped.get("parent_warehouse")
#         roll["warehouse"] = mapped.get("warehouse")

#     return rolls




# def parse_batchwise_data(batchwise_data):
#     data = []
#     for key in batchwise_data:
#         d = batchwise_data[key]
#         if flt(d.balance_qty) == 0:
#             continue
#         data.append(d)
#     print("\n\ndata\n\n", data)    
#     return data


# def get_batchwise_data_from_stock_ledger(filters):
#     batchwise_data = frappe._dict()
#     sle = frappe.qb.DocType("Stock Ledger Entry")
#     batch = frappe.qb.DocType("Batch")
#     item = frappe.qb.DocType("Item")
#     warehouse = frappe.qb.DocType("Warehouse")

#     query = (
#         frappe.qb.from_(sle)
#         .inner_join(batch).on(sle.batch_no == batch.name)
#         .inner_join(item).on(sle.item_code == item.name)
#         .left_join(warehouse).on(sle.warehouse == warehouse.name)
#         .select(
#             sle.item_code,
#             sle.warehouse,
#             sle.batch_no,
#             item.stock_uom,
#             Sum(sle.actual_qty).as_("balance_qty"),
#             warehouse.parent_warehouse
#         )
#         .where(sle.is_cancelled == 0)
#         .groupby(sle.item_code, sle.warehouse, sle.batch_no, item.stock_uom, warehouse.parent_warehouse)
#     )

#     if filters.get("item_codes"):
#         query = query.where(sle.item_code.isin(filters.item_codes))

#     for d in query.run(as_dict=True):
#         key = (d.item_code, d.warehouse, d.batch_no)
#         batchwise_data.setdefault(key, d)

#     print("\n\nbatchwise_data\n\n", batchwise_data)
#     return batchwise_data


# def get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters):
#     sle = frappe.qb.DocType("Stock Ledger Entry")
#     ch_table = frappe.qb.DocType("Serial and Batch Entry")
#     batch = frappe.qb.DocType("Batch")
#     item = frappe.qb.DocType("Item")
#     warehouse = frappe.qb.DocType("Warehouse")

#     query = (
#         frappe.qb.from_(sle)
#         .inner_join(ch_table).on(sle.serial_and_batch_bundle == ch_table.parent)
#         .inner_join(batch).on(ch_table.batch_no == batch.name)
#         .inner_join(item).on(sle.item_code == item.name)
#         .left_join(warehouse).on(ch_table.warehouse == warehouse.name)
#         .select(
#             sle.item_code,
#             ch_table.warehouse,
#             ch_table.batch_no,
#             item.stock_uom,
#             Sum(ch_table.qty).as_("balance_qty"),
#             warehouse.parent_warehouse
#         )
#         .where((sle.is_cancelled == 0) & (sle.docstatus == 1))
#         .groupby(
#             sle.item_code,
#             ch_table.warehouse,
#             ch_table.batch_no,
#             item.stock_uom,
#             warehouse.parent_warehouse
#         )
#     )

#     if filters.get("item_codes"):
#         query = query.where(sle.item_code.isin(filters.item_codes))

#     for d in query.run(as_dict=True):
#         key = (d.item_code, d.warehouse, d.batch_no)
#         if key in batchwise_data:
#             batchwise_data[key].balance_qty += flt(d.balance_qty)
#         else:
#             batchwise_data.setdefault(key, d)

#     return batchwise_data

