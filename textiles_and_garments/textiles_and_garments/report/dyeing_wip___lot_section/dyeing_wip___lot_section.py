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
            # {
            #     "label": _("Warehouse"),
            #     "fieldname": "warehouse",
            #     "fieldtype": "Link",
            #     "options": "Warehouse",
            #     "width": 200,
            # },
            {
                "label": _("Stock Entry Date"),
                "fieldname": "posting_date",
                "fieldtype": "Date",
                "width": 200,
            },
            {
                "label": _("Stock Entry"),
                "fieldname": "stock_entry",
                "fieldtype": "Link",
                "options": "Stock Entry",
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
            "label": _("WO Item Code"),
            "fieldname": "production_item",
            "fieldtype": "Link",
            "options": "Item",
            "width": 200,
            },
            {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
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
                "label": _("Work Order Qty"),
                "fieldname": "wo_qty",
                "fieldtype": "Float",
                "width": 150,
            },
            {
                "label": _("Stock Entry Qty"),
                "fieldname": "ste_qty",
                "fieldtype": "Float",
                "width": 150
            },
            {
                "label": _("Consumed Qty"),
                "fieldname": "consumed_qty",
                "fieldtype": "Float",
                "width": 150
            },
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
    stock_entry_data = get_stock_entry_detail_data_from_stock_entry(filters)
    print("\n\n\nstock_entry_data\n\n\n", stock_entry_data)
    
    # Get batch-wise stock data
    # batchwise_data = get_batchwise_data_from_stock_ledger(filters)
    # batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)

    # # # Parse batch-wise data to include only 'Work In Progress - PSS' warehouse
    # stock_data = parse_batchwise_data(batchwise_data)
    
    # Combine stock entry data with balance_qty
    final_data = combine_stock_and_batchwise_data(stock_entry_data,)
    data.extend(final_data)
    
    return data

# def get_stock_entry_detail_data_from_stock_entry(filters):
#     stock_entry_detail_data = frappe.db.sql("""
#         SELECT 
#             ste_entry_item.item_code AS item_code,
#             ste_entry_item.parent AS stock_entry,
#             ste_entry_item.qty AS ste_qty,
#             ste_entry_item.stock_uom AS stock_uom,
#             ste_entry_item.batch_no AS batch_no,
#             ste.posting_date AS posting_date,
#             ste.work_order AS work_order,
#             wo.production_item AS production_item  -- Fetching production item from work order
#         FROM 
#             `tabStock Entry Detail` AS ste_entry_item
#         INNER JOIN 
#             `tabStock Entry` AS ste
#         ON 
#             ste_entry_item.parent = ste.name
#         LEFT JOIN 
#             `tabWork Order` AS wo
#         ON 
#             ste.work_order = wo.name
#         WHERE 
#             ste_entry_item.docstatus = 1
#             AND ste_entry_item.t_warehouse = 'Work In Progress - PSS'
#     """, as_dict=1)

#     return stock_entry_detail_data 

def get_stock_entry_detail_data_from_stock_entry(filters):
    stock_entry_detail_data = frappe.db.sql("""
        SELECT 
            ste_entry_item.item_code AS item_code,
            ste_entry_item.parent AS stock_entry,
            ste_entry_item.qty AS ste_qty,
            ste_entry_item.stock_uom AS stock_uom,
            ste_entry_item.batch_no AS batch_no,
            ste.posting_date AS posting_date,
            ste.work_order AS work_order,
            wo.production_item AS production_item,
            wo.qty AS wo_qty,  -- Fetching production item from work order
            wori.item_code AS required_item_code,    -- Fetching item code from Work Order Required Items
            wori.consumed_qty AS consumed_qty        -- Fetching consumed quantity from Work Order Required Items
        FROM 
            `tabStock Entry Detail` AS ste_entry_item
        INNER JOIN 
            `tabStock Entry` AS ste
        ON 
            ste_entry_item.parent = ste.name
        LEFT JOIN 
            `tabWork Order` AS wo
        ON 
            ste.work_order = wo.name
        LEFT JOIN 
            `tabWork Order Item` AS wori
        ON 
            wo.name = wori.parent  -- Join Work Order with Work Order Required Items
            AND wori.item_code = ste_entry_item.item_code  -- Match based on item_code
        WHERE 
            ste_entry_item.docstatus = 1
            AND ste_entry_item.item_code LIKE '%KF%/%'
            AND ste_entry_item.t_warehouse = 'DYE/LOT SECTION - PSS'
    """, as_dict=1)

    return stock_entry_detail_data



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

def combine_stock_and_batchwise_data(stock_entry_data):
    final_data = []
    
    for ste in stock_entry_data:
    	final_data.append(ste)
        # Find matching batchwise data by item_code and batch_no
        # for batch in batchwise_data:
        #     if ste['item_code'] == batch['item_code'] and ste['batch_no'] == batch['batch_no']:
        #         # Add ste_qty and balance_qty together
        #         ste['balance_qty'] = batch['balance_qty']
        #         final_data.append(ste)
    
    return final_data




# def get_data(filters):
#     data = []
#     batch_wise_stock_data = []
#     ste_data = []
#     stock_entry_data  = get_stock_entry_detail_data_from_stock_entry(filters)
#     print("\n\n\nstock_entry_data\n\n\n",stock_entry_data)
#     data.extend(stock_entry_data)
    

#     batchwise_data = get_batchwise_data_from_stock_ledger(filters)
#     batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)

#     stock_data = parse_batchwise_data(batchwise_data)
#     return data
#     # batch_wise_stock_data = parse_batchwise_data(batchwise_data)
#     # print("\n\n\nstock_data\n\n\n",batch_wise_stock_data)
#     # joined_data = get_stock_entry_data(batch_wise_stock_data, filters)
#     # combined_data = combine_data(batch_wise_stock_data, joined_data)

#     # return combined_data

   

# # def get_stock_entry_data(batch_wise_stock_data, filters):
# # 	print("get_stock_entry_data")
# # 	parent = frappe.db.sql("""
# #         SELECT 
# #             ste_entry_item.item_code AS item_code,
# #             ste_entry_item.batch_no AS batch_no,
# #             ste_entry_item.qty AS qty,
# #             ste_entry_item.name AS stock_entry,
# #             ste_entry_item.stock_uom AS fg_stock_uom
# #         FROM 
# #             `tabStock Entry Item` AS ste_entry_item
# #         WHERE 
# #             ste_entry_item.status = 'Submitted'
# #     """, as_dict=1)

# def get_stock_entry_data(batch_wise_stock_data, filters):
#     print("get_stock_entry_data")

#     # Convert batch_wise_stock_data to a list of batch numbers to use in SQL query
#     batch_nos = [batch['batch_no'] for batch in batch_wise_stock_data]
    
#     if not batch_nos:
#         return []  # Return empty list if there are no batches to join with

#     # Join `tabStock Entry Item` with `tabBin` (batch-wise stock data) using batch_no
#     joined_data = frappe.db.sql("""
#         SELECT 
#             ste_entry_item.item_code AS item_code,
#             ste_entry_item.batch_no AS batch_no,
#             ste_entry_item.parenttype AS stock_entry,
#             ste_entry_item.parenttype AS stock_entry,
#             ste_entry_item.qty AS qty,
#             ste_entry_item.name AS stock_entry,
#             ste_entry_item.stock_uom AS fg_stock_uom
            
#         FROM 
#             `tabStock Entry Detail` AS ste_entry_item
#         WHERE 
#             ste_entry_item.docstatus = 1 -- 'Submitted' is represented by docstatus=1
#     """, {}, as_dict=1)

#     return joined_data


# def combine_data(batch_wise_stock_data, joined_data):
#     # Dictionary to map batch_no to batch_wise_stock_data for fast lookup
#     batch_wise_dict = {item['batch_no']: item for item in batch_wise_stock_data}
    
#     combined_data = []

#     # Loop through joined_data and merge with batch_wise_stock_data
#     for joined_item in joined_data:
#         batch_no = joined_item['batch_no']

#         # Find the corresponding batch data based on batch_no
#         if batch_no in batch_wise_dict:
#             batch_data = batch_wise_dict[batch_no]

#             # Combine the batch_wise_stock_data and joined_data
#             combined_entry = {
#                 'batch_no': batch_no,
#                 'item_code': joined_item['item_code'],  # From joined_data
#                 'qty': joined_item['qty'],  # From joined_data
#                 'stock_entry': joined_item['stock_entry'],  # From joined_data
#                 'fg_stock_uom': joined_item['fg_stock_uom'],  # From joined_data
#                 # 'stock_qty': joined_item['stock_qty'],  # From Bin
#                 # 'balance_qty': batch_data['balance_qty']  # From batch_wise_stock_data
#             }

#             combined_data.append(combined_entry)

#     return combined_data        
    

# def parse_batchwise_data(batchwise_data):
#     data = []
#     for key in batchwise_data:
#         # Check if the second element in the tuple matches 'Work In Progress - PSS'
#         if key[1] == "Work In Progress - PSS":
#             d = batchwise_data[key]
#             # Continue only if balance_qty is not 0
#             if d.balance_qty != 0:
#                 data.append(d)

#     return data



# # def parse_batchwise_data(batchwise_data):
# # 	data = []
# # 	for key in batchwise_data:
# # 		print("\n\n\nkey\n\n\n",key)
# # 		d = batchwise_data[key]
# # 		if d.balance_qty == 0:
# # 			continue

# # 		data.append(d)

# # 	return data

# # def get_stock_entry_detail_data_from_stock_entry(filters):
# #     stock_entry_detail_data = []
# #     stock_entry_detail_data = frappe.db.sql("""
# #         SELECT 
# #             ste_entry_item.item_code AS item_code,
# #             ste_entry_item.parent AS stock_entry,
# #             ste_entry_item.qty AS qty,
# #             ste_entry_item.batch_no AS batch_no,
# #             ste_entry_item.stock_uom AS stock_uom
# #         FROM 
# #             `tabStock Entry Detail` AS ste_entry_item
# #         WHERE 
# #             ste_entry_item.docstatus = 1
# #             AND ste_entry_item.t_warehouse = 'Work In Progress - PSS'
# #     """, as_dict=1)

# #     return stock_entry_detail_data

# def get_stock_entry_detail_data_from_stock_entry(filters):
#     stock_entry_detail_data = frappe.db.sql("""
#         SELECT 
#             ste_entry_item.item_code AS item_code,
#             ste_entry_item.parent AS stock_entry,
#             ste_entry_item.qty AS ste_qty,
#             ste_entry_item.stock_uom AS stock_uom,
#             ste_entry_item.batch_no AS batch_no,
#             ste.posting_date AS posting_date,
#             ste.work_order AS work_order,
#             wo.production_item AS production_item  -- Fetching production item from work order
#         FROM 
#             `tabStock Entry Detail` AS ste_entry_item
#         INNER JOIN 
#             `tabStock Entry` AS ste
#         ON 
#             ste_entry_item.parent = ste.name
#         LEFT JOIN 
#             `tabWork Order` AS wo
#         ON 
#             ste.work_order = wo.name
#         WHERE 
#             ste_entry_item.docstatus = 1
#             AND ste_entry_item.t_warehouse = 'Work In Progress - PSS'
#     """, as_dict=1)

#     return stock_entry_detail_data    

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

#     query = get_query_based_on_filters(query, batch, table, filters)

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

#     query = get_query_based_on_filters(query, batch, table, filters)

#     for d in query.run(as_dict=True):
#         key = (d.item_code, d.warehouse, d.batch_no)
#         if key in batchwise_data:
#             batchwise_data[key].balance_qty += flt(d.balance_qty)
#         else:
#             batchwise_data.setdefault(key, d)

#     return batchwise_data


# def get_query_based_on_filters(query, batch, table, filters):
#     if filters.item_code:
#         query = query.where(table.item_code == filters.item_code)

#     if filters.batch_no:
#         query = query.where(batch.name == filters.batch_no)

#     if not filters.include_expired_batches:
#         query = query.where((batch.expiry_date >= today()) | (batch.expiry_date.isnull()))
#         if filters.to_date == today():
#             query = query.where(batch.batch_qty > 0)

#     if filters.warehouse:
#         lft, rgt = frappe.db.get_value("Warehouse", filters.warehouse, ["lft", "rgt"])
#         warehouses = frappe.get_all(
#             "Warehouse", filters={"lft": (">=", lft), "rgt": ("<=", rgt), "is_group": 0}, pluck="name"
#         )

#         query = query.where(table.warehouse.isin(warehouses))

#     elif filters.warehouse_type:
#         warehouses = frappe.get_all(
#             "Warehouse", filters={"warehouse_type": filters.warehouse_type, "is_group": 0}, pluck="name"
#         )

#         query = query.where(table.warehouse.isin(warehouses))

#     if filters.show_item_name:
#         query = query.select(batch.item_name)

#     return query	



# def execute(filters=None):
#     # Define the columns for the report
#     columns = [
#         {'fieldname': 'date', 'label': 'Date Inward', 'fieldtype': 'Date'},
#         {'fieldname': 'mt_no', 'label': 'MT', 'fieldtype': 'Link', 'options': 'Stock Entry'},
#         {'fieldname': 'work_order_no', 'label': 'Work Order', 'fieldtype': 'Link', 'options': 'Work Order'},
#         {'fieldname': 'commercial_name', 'label': 'Commercial Name', 'fieldtype': 'Data'},
#         {'fieldname': 'fg_item', 'label': 'Finished Item Code', 'fieldtype': 'Data'},
#         {'fieldname': 'body_griege_fabric_recieved_qty', 'label': 'Body Griege Fabric Recieved Qty', 'fieldtype': 'Float'},
#         {'fieldname': 'trims_griege_fabric_recieved_qty', 'label': 'Trims Griege Fabric Recieved Qty', 'fieldtype': 'Float'},
#         {'fieldname': 'uom', 'label': 'UOM', 'fieldtype': 'Data'},
#         {'fieldname': 'project', 'label': 'Indent Number', 'fieldtype': 'Data'},
#         {'fieldname': 'rm_item', 'label': 'RM Item', 'fieldtype': 'Data'},
#         # {'fieldname': 'body_griege_fabric_item_code', 'label': 'Body Griege Fabric Item Code', 'fieldtype': 'Data'},
#         # {'fieldname': 'trims_griege_fabric_item_code', 'label': 'Trims Griege Fabric Item Code', 'fieldtype': 'Data'},  # New column for required quantity
#         {'fieldname': 'batch_no_for_body_fabric', 'label': 'Batch No for Body Fabric', 'fieldtype': 'Data'},
#         {'fieldname': 'batch_no_for_trims_fabric', 'label': 'Batch No for Trims Fabric', 'fieldtype': 'Data'}
#     ]

#     # Initialize data list
#     data = []

#     # SQL query to fetch Work Order Items and related Dye Recipe Items
  

#     stock_data = frappe.db.sql("""
# 	    SELECT 
# 	        bin.item_code AS rm_item,
# 	        bin.item_code AS rm_item
# 	        bin.actual_qty AS stock_qty,
# 	        bin.uom AS uom
# 	    FROM 
# 	        `tabBin` AS bin
# 	    WHERE 
# 	        bin.warehouse = 'DYE/LOT SECTION - PSS'
# 	""", {
# 	    'item_code': dic_c["raw_material"]
# 	}, as_dict=1)


# 	return columns, data
