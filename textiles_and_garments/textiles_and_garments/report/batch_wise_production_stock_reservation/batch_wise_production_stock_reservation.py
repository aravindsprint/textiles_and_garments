# Copyright (c) 2025, Aravind and contributors
# For license information,please see license.txt

# from collections import defaultdict
# import frappe
# from frappe import _
# from frappe.query_builder.functions import Sum
# from frappe.utils import flt, today

# def execute(filters=None):
#     columns, data = [], []
#     data = get_data(filters)
#     columns = get_columns(filters)
#     return columns, data

# def get_columns(filters):
#     columns = [
#         {
#             "label": _("Date"),
#             "fieldname": "posting_date",
#             "fieldtype": "Date",
#             "width": 150,
#         },
#         {
#             "label": _("Item Code"),
#             "fieldname": "item_code",
#             "fieldtype": "Link",
#             "options": "Item",
#             "width": 400,
#         },
#         {
#             "label": _("Warehouse"),
#             "fieldname": "warehouse",
#             "fieldtype": "Link",
#             "options": "Warehouse",
#             "width": 200,
#         },
#         {
#             "label": _("Batch"),
#             "fieldname": "batch_no",
#             "fieldtype": "Link",
#             "options": "Batch",
#             "width": 240,
#         },
#         {
#             "label": _("Plan no"),
#             "fieldname": "plans_no",
#             "fieldtype": "Link",
#             "options": "Plans",
#             "width": 100,
#         },
#         {
#             "label": _("Reserved Qty"),
#             "fieldname": "qty",
#             "fieldtype": "Float",
#             "width": 90,
#         },
#         {
#             "label": _("Delivered Qty"),
#             "fieldname": "delivered_qty",
#             "fieldtype": "Float",
#             "width": 90,
#         },
#         {
#             "label": _("UOM"),
#             "fieldname": "uom",
#             "fieldtype": "Data",
#             "width": 70,
#         },
#         {
#             "label": _("Docstatus"),
#             "fieldname": "docstatus",
#             "fieldtype": "Data",
#             "width": 50,
#         }
#     ]

#     return columns

# def get_data(filters):
#     data = []
#     production_stock_reservation_data = get_production_stock_reservation_data(filters)
#     data.extend(production_stock_reservation_data)
#     return data

# def get_production_stock_reservation_data(filters):
#     query = """
#         SELECT 
#             psr.item_code,
#             psr.posting_date as posting_date,
#             item.item_name,
#             psr.plans_no as plans_no,
#             psr.voucher_qty as qty, 
#             psr.stock_uom as uom,
#             psri.warehouse,
#             psri.batch_no,
#             psri.qty,
#             psri.delivered_qty,
#             psr.docstatus
#         FROM `tabProduction Stock Reservation` AS psr
#         JOIN `tabSerial and Batch Entry Plans` AS psri ON psri.parent = psr.name
#         JOIN `tabItem` AS item ON item.item_code = psr.item_code
#     """

#     conditions = []

#     if filters.get("from_date"):
#         conditions.append("psr.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions.append("psr.posting_date <= %(to_date)s")
#     if filters.get("item_code"):
#         conditions.append("psr.item_code = %(item_code)s")
#     if filters.get("warehouse"):
#         conditions.append("psri.warehouse = %(warehouse)s")
#     if filters.get("batch_no"):
#         conditions.append("psri.batch_no = %(batch_no)s")
#     if filters.get("plans_no"):
#         conditions.append("psr.plans_no = %(plans_no)s")
#     if filters.get("docstatus") is not None:
#         conditions.append("psr.docstatus = %(docstatus)s")


#     # Only add WHERE clause if there are conditions
#     if conditions:
#         query += " WHERE " + " AND ".join(conditions)



#     filter_values = {
#         "item_code": filters.get("item_code") or None,
#         "warehouse": filters.get("warehouse") or None,
#         "batch_no": filters.get("batch_no") or None,
#         "plans_no": filters.get("plans_no") or None,
#         "from_date": filters.get("from_date"),
#         "to_date": filters.get("to_date"),
#         "docstatus": int(filters.get("docstatus")) if filters.get("docstatus") else None,
#     }

    
#     return frappe.db.sql(query, filter_values, as_dict=1)



# from collections import defaultdict
# import frappe
# from frappe import _
# from frappe.query_builder.functions import Sum
# from frappe.utils import flt, today


# def execute(filters=None):
#     columns, data = [], []
#     data = get_data(filters)
#     columns = get_columns(filters)
#     return columns, data


# def get_columns(filters):
#     columns = [
#         {
#             "label": _("Date"),
#             "fieldname": "posting_date",
#             "fieldtype": "Date",
#             "width": 150,
#         },
#         {
#             "label": _("Item Code"),
#             "fieldname": "item_code",
#             "fieldtype": "Link",
#             "options": "Item",
#             "width": 400,
#         },
#         {
#             "label": _("Warehouse"),
#             "fieldname": "warehouse",
#             "fieldtype": "Link",
#             "options": "Warehouse",
#             "width": 200,
#         },
#         {
#             "label": _("Batch"),
#             "fieldname": "batch_no",
#             "fieldtype": "Link",
#             "options": "Batch",
#             "width": 240,
#         },
#         {
#             "label": _("Plan no"),
#             "fieldname": "plans_no",
#             "fieldtype": "Link",
#             "options": "Plans",
#             "width": 100,
#         },
#         {
#             "label": _("Stock Qty"),
#             "fieldname": "balance_qty",
#             "fieldtype": "Float",
#             "width": 110,
#         },
#         {
#             "label": _("Reserved Qty"),
#             "fieldname": "qty",
#             "fieldtype": "Float",
#             "width": 90,
#         },
#         {
#             "label": _("Consumed Qty"),
#             "fieldname": "delivered_qty",
#             "fieldtype": "Float",
#             "width": 90,
#         },
#         {
#             "label": _("UOM"),
#             "fieldname": "uom",
#             "fieldtype": "Data",
#             "width": 70,
#         },
#         {
#             "label": _("Docstatus"),
#             "fieldname": "docstatus",
#             "fieldtype": "Data",
#             "width": 50,
#         }
        
#     ]
#     return columns


# def get_data(filters):
#     # Get combined batch-wise stock
#     batchwise_stock = get_combined_batchwise_stock(filters)

#     # Fetch Production Stock Reservation entries
#     psr_data = get_production_stock_reservation_data(filters, batchwise_stock)

#     return psr_data


# def get_production_stock_reservation_data(filters, batchwise_stock):
#     query = """
#         SELECT 
#             psr.item_code,
#             psr.posting_date,
#             item.item_name,
#             psr.plans_no,
#             psr.voucher_qty as qty,
#             psr.stock_uom as uom,
#             psri.warehouse,
#             psri.batch_no,
#             psri.qty,
#             psri.delivered_qty,
#             psr.docstatus
#         FROM `tabProduction Stock Reservation` AS psr
#         JOIN `tabSerial and Batch Entry Plans` AS psri ON psri.parent = psr.name
#         JOIN `tabItem` AS item ON item.item_code = psr.item_code
#     """

#     conditions = []
#     if filters.get("from_date"):
#         conditions.append("psr.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions.append("psr.posting_date <= %(to_date)s")
#     if filters.get("item_code"):
#         conditions.append("psr.item_code = %(item_code)s")
#     if filters.get("warehouse"):
#         conditions.append("psri.warehouse = %(warehouse)s")
#     if filters.get("batch_no"):
#         conditions.append("psri.batch_no = %(batch_no)s")
#     if filters.get("plans_no"):
#         conditions.append("psr.plans_no = %(plans_no)s")
#     if filters.get("docstatus") is not None:
#         conditions.append("psr.docstatus = %(docstatus)s")

#     if conditions:
#         query += " WHERE " + " AND ".join(conditions)

#     values = {
#         "from_date": filters.get("from_date"),
#         "to_date": filters.get("to_date"),
#         "item_code": filters.get("item_code"),
#         "warehouse": filters.get("warehouse"),
#         "batch_no": filters.get("batch_no"),
#         "plans_no": filters.get("plans_no"),
#         "docstatus": int(filters.get("docstatus")) if filters.get("docstatus") is not None else None,
#     }

#     results = frappe.db.sql(query, values, as_dict=True)

#     for row in results:
#         key = (row.item_code, row.warehouse, row.batch_no)
#         row.balance_qty = flt(batchwise_stock.get(key, 0.0))

#     return results


# def get_combined_batchwise_stock(filters):
#     batchwise_data = get_batchwise_data_from_stock_ledger(filters)
#     batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)

#     # Convert to simple map: {(item_code, warehouse, batch_no): balance_qty}
#     stock_map = {}
#     for key, value in batchwise_data.items():
#         stock_map[key] = flt(value.balance_qty)

#     return stock_map


# def get_batchwise_data_from_stock_ledger(filters):
#     batchwise_data = frappe._dict({})
#     table = frappe.qb.DocType("Stock Ledger Entry")
#     batch = frappe.qb.DocType("Batch")

#     query = (
#         frappe.qb.from_(table)
#         .inner_join(batch)
#         .on(table.batch_no == batch.name)
#         .select(
#             table.item_code,
#             table.batch_no,
#             table.warehouse,
#             Sum(table.actual_qty).as_("balance_qty"),
#         )
#         .where(table.is_cancelled == 0)
#         .groupby(table.batch_no, table.item_code, table.warehouse)
#     )

#     query = apply_filters(query, batch, table, filters)

#     for d in query.run(as_dict=True):
#         key = (d.item_code, d.warehouse, d.batch_no)
#         batchwise_data.setdefault(key, d)

#     return batchwise_data


# def get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters):
#     table = frappe.qb.DocType("Stock Ledger Entry")
#     ch_table = frappe.qb.DocType("Serial and Batch Entry")
#     batch = frappe.qb.DocType("Batch")

#     query = (
#         frappe.qb.from_(table)
#         .inner_join(ch_table)
#         .on(table.serial_and_batch_bundle == ch_table.parent)
#         .inner_join(batch)
#         .on(ch_table.batch_no == batch.name)
#         .select(
#             table.item_code,
#             ch_table.batch_no,
#             table.warehouse,
#             Sum(ch_table.qty).as_("balance_qty"),
#         )
#         .where((table.is_cancelled == 0) & (table.docstatus == 1))
#         .groupby(ch_table.batch_no, table.item_code, ch_table.warehouse)
#     )

#     query = apply_filters(query, batch, table, filters)

#     for d in query.run(as_dict=True):
#         key = (d.item_code, d.warehouse, d.batch_no)
#         if key in batchwise_data:
#             batchwise_data[key].balance_qty += flt(d.balance_qty)
#         else:
#             batchwise_data.setdefault(key, d)

#     return batchwise_data


# def apply_filters(query, batch, table, filters):
#     if filters.get("item_code"):
#         query = query.where(table.item_code == filters.item_code)
#     if filters.get("batch_no"):
#         query = query.where(batch.name == filters.batch_no)
#     if not filters.get("include_expired_batches"):
#         query = query.where((batch.expiry_date >= today()) | (batch.expiry_date.isnull()))
#         if filters.get("to_date") == today():
#             query = query.where(batch.batch_qty > 0)
#     if filters.get("warehouse"):
#         lft, rgt = frappe.db.get_value("Warehouse", filters.warehouse, ["lft", "rgt"])
#         warehouses = frappe.get_all(
#             "Warehouse",
#             filters={"lft": (">=", lft), "rgt": ("<=", rgt), "is_group": 0},
#             pluck="name"
#         )
#         query = query.where(table.warehouse.isin(warehouses))
#     elif filters.get("warehouse_type"):
#         warehouses = frappe.get_all(
#             "Warehouse",
#             filters={"warehouse_type": filters.warehouse_type, "is_group": 0},
#             pluck="name"
#         )
#         query = query.where(table.warehouse.isin(warehouses))
#     return query


# from collections import defaultdict
# import frappe
# from frappe import _
# from frappe.query_builder.functions import Sum
# from frappe.utils import flt, today


# def execute(filters=None):
#     columns, data = [], []
#     data = get_data(filters)
#     columns = get_columns(filters)
#     return columns, data


# def get_columns(filters):
#     columns = [
#         {
#             "label": _("Date"),
#             "fieldname": "posting_date",
#             "fieldtype": "Date",
#             "width": 150,
#         },
#         {
#             "label": _("Item Code"),
#             "fieldname": "item_code",
#             "fieldtype": "Link",
#             "options": "Item",
#             "width": 400,
#         },
#         {
#             "label": _("Warehouse"),
#             "fieldname": "warehouse",
#             "fieldtype": "Link",
#             "options": "Warehouse",
#             "width": 200,
#         },
#         {
#             "label": _("Batch"),
#             "fieldname": "batch_no",
#             "fieldtype": "Link",
#             "options": "Batch",
#             "width": 240,
#         },
#         {
#             "label": _("Plan no"),
#             "fieldname": "plans_no",
#             "fieldtype": "Link",
#             "options": "Plans",
#             "width": 100,
#         },
#         {
#             "label": _("Stock Qty"),
#             "fieldname": "balance_qty",
#             "fieldtype": "Float",
#             "width": 110,
#         },
#         {
#             "label": _("Reserved Qty"),
#             "fieldname": "qty",
#             "fieldtype": "Float",
#             "width": 90,
#         },
#         {
#             "label": _("Consumed Qty"),
#             "fieldname": "delivered_qty",
#             "fieldtype": "Float",
#             "width": 90,
#         },
#         {
#             "label": _("Avail Qty After Reserve"),
#             "fieldname": "avail_qty_after_reserve",
#             "fieldtype": "Float",
#             "width": 130,
#         },
#         {
#             "label": _("UOM"),
#             "fieldname": "uom",
#             "fieldtype": "Data",
#             "width": 70,
#         },
#         {
#             "label": _("Docstatus"),
#             "fieldname": "docstatus",
#             "fieldtype": "Data",
#             "width": 50,
#         }
#     ]
#     return columns


# def get_data(filters):
#     batchwise_stock = get_combined_batchwise_stock(filters)
#     psr_data = get_production_stock_reservation_data(filters, batchwise_stock)
#     return psr_data


# def get_production_stock_reservation_data(filters, batchwise_stock):
#     query = """
#         SELECT 
#             psr.item_code,
#             psr.posting_date,
#             item.item_name,
#             psr.plans_no,
#             psr.voucher_qty as qty,
#             psr.stock_uom as uom,
#             psri.warehouse,
#             psri.batch_no,
#             psri.qty,
#             psri.delivered_qty,
#             psr.docstatus
#         FROM `tabProduction Stock Reservation` AS psr
#         JOIN `tabSerial and Batch Entry Plans` AS psri ON psri.parent = psr.name
#         JOIN `tabItem` AS item ON item.item_code = psr.item_code
#     """

#     conditions = []
#     if filters.get("from_date"):
#         conditions.append("psr.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions.append("psr.posting_date <= %(to_date)s")
#     if filters.get("item_code"):
#         conditions.append("psr.item_code = %(item_code)s")
#     if filters.get("warehouse"):
#         conditions.append("psri.warehouse = %(warehouse)s")
#     if filters.get("batch_no"):
#         conditions.append("psri.batch_no = %(batch_no)s")
#     if filters.get("plans_no"):
#         conditions.append("psr.plans_no = %(plans_no)s")
#     if filters.get("docstatus") is not None:
#         conditions.append("psr.docstatus = %(docstatus)s")

#     if conditions:
#         query += " WHERE " + " AND ".join(conditions)

#     values = {
#         "from_date": filters.get("from_date"),
#         "to_date": filters.get("to_date"),
#         "item_code": filters.get("item_code"),
#         "warehouse": filters.get("warehouse"),
#         "batch_no": filters.get("batch_no"),
#         "plans_no": filters.get("plans_no"),
#         "docstatus": int(filters.get("docstatus")) if filters.get("docstatus") is not None else None,
#     }

#     results = frappe.db.sql(query, values, as_dict=True)

#     # Sort by key to maintain group processing
#     results.sort(key=lambda x: (x["item_code"], x["warehouse"], x["batch_no"], x["posting_date"]))

#     previous_avail_map = {}

#     for row in results:
#         key = (row.item_code, row.warehouse, row.batch_no)

#         # Get initial balance
#         if key not in previous_avail_map:
#             balance_qty = flt(batchwise_stock.get(key, 0.0))
#             avail_qty = balance_qty - flt(row.qty)
#             previous_avail_map[key] = avail_qty
#             row.balance_qty = balance_qty
#         else:
#             avail_qty = previous_avail_map[key] - flt(row.qty)
#             row.balance_qty = flt(batchwise_stock.get(key, 0.0))  # Optional: show original stock always
#             previous_avail_map[key] = avail_qty

#         row.avail_qty_after_reserve = avail_qty

#     return results


# def get_combined_batchwise_stock(filters):
#     batchwise_data = get_batchwise_data_from_stock_ledger(filters)
#     batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)

#     stock_map = {}
#     for key, value in batchwise_data.items():
#         stock_map[key] = flt(value.balance_qty)

#     return stock_map


# def get_batchwise_data_from_stock_ledger(filters):
#     batchwise_data = frappe._dict({})
#     table = frappe.qb.DocType("Stock Ledger Entry")
#     batch = frappe.qb.DocType("Batch")

#     query = (
#         frappe.qb.from_(table)
#         .inner_join(batch)
#         .on(table.batch_no == batch.name)
#         .select(
#             table.item_code,
#             table.batch_no,
#             table.warehouse,
#             Sum(table.actual_qty).as_("balance_qty"),
#         )
#         .where(table.is_cancelled == 0)
#         .groupby(table.batch_no, table.item_code, table.warehouse)
#     )

#     query = apply_filters(query, batch, table, filters)

#     for d in query.run(as_dict=True):
#         key = (d.item_code, d.warehouse, d.batch_no)
#         batchwise_data.setdefault(key, d)

#     return batchwise_data


# def get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters):
#     table = frappe.qb.DocType("Stock Ledger Entry")
#     ch_table = frappe.qb.DocType("Serial and Batch Entry")
#     batch = frappe.qb.DocType("Batch")

#     query = (
#         frappe.qb.from_(table)
#         .inner_join(ch_table)
#         .on(table.serial_and_batch_bundle == ch_table.parent)
#         .inner_join(batch)
#         .on(ch_table.batch_no == batch.name)
#         .select(
#             table.item_code,
#             ch_table.batch_no,
#             table.warehouse,
#             Sum(ch_table.qty).as_("balance_qty"),
#         )
#         .where((table.is_cancelled == 0) & (table.docstatus == 1))
#         .groupby(ch_table.batch_no, table.item_code, ch_table.warehouse)
#     )

#     query = apply_filters(query, batch, table, filters)

#     for d in query.run(as_dict=True):
#         key = (d.item_code, d.warehouse, d.batch_no)
#         if key in batchwise_data:
#             batchwise_data[key].balance_qty += flt(d.balance_qty)
#         else:
#             batchwise_data.setdefault(key, d)

#     return batchwise_data


# def apply_filters(query, batch, table, filters):
#     if filters.get("item_code"):
#         query = query.where(table.item_code == filters.item_code)
#     if filters.get("batch_no"):
#         query = query.where(batch.name == filters.batch_no)
#     if not filters.get("include_expired_batches"):
#         query = query.where((batch.expiry_date >= today()) | (batch.expiry_date.isnull()))
#         if filters.get("to_date") == today():
#             query = query.where(batch.batch_qty > 0)
#     if filters.get("warehouse"):
#         lft, rgt = frappe.db.get_value("Warehouse", filters.warehouse, ["lft", "rgt"])
#         warehouses = frappe.get_all(
#             "Warehouse",
#             filters={"lft": (">=", lft), "rgt": ("<=", rgt), "is_group": 0},
#             pluck="name"
#         )
#         query = query.where(table.warehouse.isin(warehouses))
#     elif filters.get("warehouse_type"):
#         warehouses = frappe.get_all(
#             "Warehouse",
#             filters={"warehouse_type": filters.warehouse_type, "is_group": 0},
#             pluck="name"
#         )
#         query = query.where(table.warehouse.isin(warehouses))
#     return query



from collections import defaultdict
import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today
import logging
import os
from frappe.utils import get_site_path

# Initialize logger at module level
logger = logging.getLogger("production_stock_report")

def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(get_site_path(), 'private', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'production_stock_report.log')
    
    # Configure logger
    logger.setLevel(logging.DEBUG)
    
    # Create file handler
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)

# Call this when module loads
setup_logging()


def execute(filters=None):
    columns, data = [], []
    data = get_data(filters)
    columns = get_columns(filters)
    return columns, data


def get_columns(filters):
    columns = [
        {
            "label": _("Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 250,
        },
        {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 200,
        },
        {
            "label": _("Batch"),
            "fieldname": "batch_no",
            "fieldtype": "Link",
            "options": "Batch",
            "width": 240,
        },
        {
            "label": _("Plan no"),
            "fieldname": "plans_no",
            "fieldtype": "Link",
            "options": "Plans",
            "width": 100,
        },
        # {
        #     "label": _("Indent"),
        #     "fieldname": "indent",
        #     "fieldtype": "Link",
        #     "options": "Material Request",
        #     "width": 100,
        # },
        # {
        #     "label": _("Stock Qty"),
        #     "fieldname": "balance_qty",
        #     "fieldtype": "Float",
        #     "width": 110,
        # },
        {
            "label": _("Reserved Qty"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("Consumed Qty"),
            "fieldname": "delivered_qty",
            "fieldtype": "Float",
            "width": 90,
        },
        # {
        #     "label": _("Avail Qty After Reserve"),
        #     "fieldname": "avail_qty_after_reserve",
        #     "fieldtype": "Float",
        #     "width": 130,
        # },
        {
            "label": _("UOM"),
            "fieldname": "uom",
            "fieldtype": "Data",
            "width": 70,
        },
        {
            "label": _("Docstatus"),
            "fieldname": "docstatus",
            "fieldtype": "Data",
            "width": 50,
        }
    ]
    return columns


def get_data(filters):
    batchwise_stock = get_combined_batchwise_stock(filters)
    psr_data = get_production_stock_reservation_data(filters, batchwise_stock)
    return psr_data

# def get_production_stock_reservation_data(filters, batchwise_stock):
#     query = """
#         SELECT 
#             psr.item_code,
#             psr.posting_date,
#             item.item_name,
#             psr.plans_no,
#             psr.indent,
#             psr.voucher_qty as qty,
#             psr.stock_uom as uom,
#             psri.warehouse,
#             psri.batch_no,
#             psri.qty,
#             psri.short_close_qty,
#             psri.delivered_qty,
#             psri.actual_delivered_qty,
#             psr.docstatus,
#             psr.creation
#         FROM `tabProduction Stock Reservation` AS psr
#         JOIN `tabSerial and Batch Entry Plans` AS psri ON psri.parent = psr.name
#         JOIN `tabItem` AS item ON item.item_code = psr.item_code
#         WHERE psr.docstatus = 1
#     """

#     conditions = []
#     if filters.get("from_date"):
#         conditions.append("psr.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions.append("psr.posting_date <= %(to_date)s")
#     if filters.get("item_code"):
#         conditions.append("psr.item_code = %(item_code)s")
#     if filters.get("warehouse"):
#         conditions.append("psri.warehouse = %(warehouse)s")
#     if filters.get("batch_no"):
#         conditions.append("psri.batch_no = %(batch_no)s")
#     if filters.get("plans_no"):
#         conditions.append("psr.plans_no = %(plans_no)s")
#     if filters.get("indent"):
#         conditions.append("psr.indent = %(indent)s")    

#     if conditions:
#         query += " AND " + " AND ".join(conditions)

#     query += " ORDER BY psr.creation"

#     values = {
#         "from_date": filters.get("from_date"),
#         "to_date": filters.get("to_date"),
#         "item_code": filters.get("item_code"),
#         "warehouse": filters.get("warehouse"),
#         "batch_no": filters.get("batch_no"),
#         "plans_no": filters.get("plans_no"),
#         "indent": filters.get("indent"),
#     }

    # results = frappe.db.sql(query, values, as_dict=True)

    # previous_avail_map = {}

#     for row in results:
#         print("\n\nrow\n\n",row)
#         key = (row.item_code, row.warehouse, row.batch_no)

#         if key not in previous_avail_map:
#             frappe.msgprint(_("if"))  # Fixed indentation
#             balance_qty = flt(batchwise_stock.get(key, 0.0))
#             print("\n\nbalance_qty\n\n",balance_qty)
#             print("\n\nshort_close_qty\n\n",row.short_close_qty)
#             print("\n\nrow.qty\n\n",row.qty)
#             row.qty = row.qty - row.short_close_qty
#             logger.debug("balance_qty %s", balance_qty)
#             avail_qty = balance_qty - flt(row.qty) 
#             previous_avail_map[key] = avail_qty
#             row.balance_qty = balance_qty
#         else:
#             # avail_qty = previous_avail_map[key] - flt(row.qty)
#             frappe.msgprint(_("else"))
#             # frappe.msgprint(_("Quotation creation local final_vehicle: {0}").format(final_vehicle))
#             print("\n\nprevious_avail_map[key]\n\n",previous_avail_map[key])
#             print("\n\nshort_close_qty\n\n",row.short_close_qty)
#             print("\n\nrow.qty\n\n",row.qty)
#             avail_qty = previous_avail_map[key] - flt(row.qty)
#             row.balance_qty = flt(batchwise_stock.get(key, 0.0))
#             previous_avail_map[key] = avail_qty

#         row.avail_qty_after_reserve = avail_qty

#     return results

def get_production_stock_reservation_data(filters, batchwise_stock):
    # Log the start of the function
    logger.info("Starting get_production_stock_reservation_data with filters: %s", filters)
    
    query = """
        SELECT 
            psr.item_code,
            psr.posting_date,
            item.item_name,
            psr.plans_no,
            psr.indent,
            psr.voucher_qty as qty,
            psr.stock_uom as uom,
            psri.warehouse,
            psri.batch_no,
            psri.qty,
            psri.short_close_qty,
            psri.delivered_qty,
            psri.actual_delivered_qty,
            psr.docstatus,
            psr.creation
        FROM `tabProduction Stock Reservation` AS psr
        JOIN `tabSerial and Batch Entry Plans` AS psri ON psri.parent = psr.name
        JOIN `tabItem` AS item ON item.item_code = psr.item_code
        WHERE psr.docstatus = 1
    """

    conditions = []
    if filters.get("from_date"):
        conditions.append("psr.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("psr.posting_date <= %(to_date)s")
    if filters.get("item_code"):
        conditions.append("psr.item_code = %(item_code)s")
    if filters.get("warehouse"):
        conditions.append("psri.warehouse = %(warehouse)s")
    if filters.get("batch_no"):
        conditions.append("psri.batch_no = %(batch_no)s")
    if filters.get("plans_no"):
        conditions.append("psr.plans_no = %(plans_no)s")
    if filters.get("indent"):
        conditions.append("psr.indent = %(indent)s")    

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " ORDER BY psr.creation"

    values = {
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "item_code": filters.get("item_code"),
        "warehouse": filters.get("warehouse"),
        "batch_no": filters.get("batch_no"),
        "plans_no": filters.get("plans_no"),
        "indent": filters.get("indent"),
    }


    results = frappe.db.sql(query, values, as_dict=True)
    logger.info("Query returned %d results", len(results))

    results = frappe.db.sql(query, values, as_dict=True)

    previous_avail_map = {}

    for row in results:
        key = (row.item_code, row.warehouse, row.batch_no)
        logger.debug("Processing row with key: %s", key)

        if key not in previous_avail_map:
            logger.debug("New key found in results")
            balance_qty = flt(batchwise_stock.get(key, 0.0))
            logger.debug("Balance qty: %f, Short close qty: %f, Row qty: %f", 
                        balance_qty, row.short_close_qty, row.qty)
            
            row.qty = row.qty - row.short_close_qty
            avail_qty = balance_qty - flt(row.qty)
            previous_avail_map[key] = avail_qty
            row.balance_qty = balance_qty
        else:
            logger.debug("Existing key being processed")
            # logger.debug("Balance qty: %f, actual_delivered_qty: %f, Row qty: %f", 
            #             balance_qty, row.actual_delivered_qty, row.qty)
            logger.debug("Row qty: %f, avail_qty : %f, previous_avail_map[key]: %f", 
                        row.qty, avail_qty, previous_avail_map[key])
            # avail_qty = previous_avail_map[key] - flt(row.qty)
            avail_qty = flt(row.balance_qty) - flt(row.qty)
            row.balance_qty = flt(batchwise_stock.get(key, 0.0))
            previous_avail_map[key] = avail_qty
            logger.debug("Balance qty: %f, actual_delivered_qty: %f, Row qty: %f, avail_qty : %f, previous_avail_map[key]: %f", 
                        row.balance_qty, row.actual_delivered_qty, row.qty, avail_qty, previous_avail_map[key])

        row.avail_qty_after_reserve = avail_qty
        logger.debug("Final avail_qty_after_reserve: %f", row.avail_qty_after_reserve)

    return results



def get_combined_batchwise_stock(filters):
    batchwise_data = get_batchwise_data_from_stock_ledger(filters)
    batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)

    stock_map = {}
    for key, value in batchwise_data.items():
        stock_map[key] = flt(value.balance_qty)

    return stock_map


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

    query = apply_filters(query, batch, table, filters)

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

    query = apply_filters(query, batch, table, filters)

    for d in query.run(as_dict=True):
        key = (d.item_code, d.warehouse, d.batch_no)
        if key in batchwise_data:
            batchwise_data[key].balance_qty += flt(d.balance_qty)
        else:
            batchwise_data.setdefault(key, d)

    return batchwise_data


def apply_filters(query, batch, table, filters):
    if filters.get("item_code"):
        query = query.where(table.item_code == filters.item_code)
    if filters.get("batch_no"):
        query = query.where(batch.name == filters.batch_no)
    if not filters.get("include_expired_batches"):
        query = query.where((batch.expiry_date >= today()) | (batch.expiry_date.isnull()))
        if filters.get("to_date") == today():
            query = query.where(batch.batch_qty > 0)
    if filters.get("warehouse"):
        lft, rgt = frappe.db.get_value("Warehouse", filters.warehouse, ["lft", "rgt"])
        warehouses = frappe.get_all(
            "Warehouse",
            filters={"lft": (">=", lft), "rgt": ("<=", rgt), "is_group": 0},
            pluck="name"
        )
        query = query.where(table.warehouse.isin(warehouses))
    elif filters.get("warehouse_type"):
        warehouses = frappe.get_all(
            "Warehouse",
            filters={"warehouse_type": filters.warehouse_type, "is_group": 0},
            pluck="name"
        )
        query = query.where(table.warehouse.isin(warehouses))
    return query
