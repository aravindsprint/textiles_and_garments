# Copyright (c) 2024, Aravind and contributors
# For license information, please see license.txt

from collections import defaultdict

import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today
import json
from datetime import date 

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
            # {
            #     "label": _("Item Name"),
            #     "fieldname": "item_name",
            #     "fieldtype": "Link",
            #     "options": "Item",
            #     "width": 200,
            # }
        )

    columns.extend(
        [
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
            "fieldname": "required_item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 200,
            },
            {
                "label": _("Warehouse"),
                "fieldname": "t_warehouse",
                "fieldtype": "Link",
                "width": 150,
                "options": "Warehouse",
            },
            {
                "label": _("Batch No"),
                "fieldname": "batch_no",
                "fieldtype": "Link",
                "width": 150,
                "options": "Batch",
            },
            # {
            #     "label": _("Work Order Qty"),
            #     "fieldname": "wo_qty",
            #     "fieldtype": "Float",
            #     "width": 150,
            # },
            {
                "label": _("Transferred Qty"),
                "fieldname": "transferred_qty",
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
                "label": _("Pending Qty"),
                "fieldname": "pending_qty",
                "fieldtype": "Float",
                "width": 150
            },
            {
                "label": _("stock_qty"),
                "fieldname": "stock_qty",
                "fieldtype": "Data",
                "width": 150
            },
            {
                "label": _("UOM"),
                "fieldname": "stock_uom",
                "fieldtype": "Data",
                "width": 150
            },
            


            # {
            #     "label": _("required_item_code"),
            #     "fieldname": "required_item_code",
            #     "fieldtype": "Data",
            #     "width": 150
            # },
            # {"label": _("Balance Qty"), "fieldname": "balance_qty", "fieldtype": "Float", "width": 150},
        ]
    )

    return columns


@frappe.whitelist()
def get_data(filters):
    data = []
    
    # Get stock entry data with ste_qty
    stock_entry_data = get_stock_entry_detail_data_from_stock_entry(filters)
    print("\n\n\nstock_entry_data\n\n\n", stock_entry_data)
    # frappe.msgprint(f"stock_entry_data :\n{json.dumps(stock_entry_data, indent=2)}")

    stock_data = get_stock_data(filters)
    frappe.msgprint(f"s Stock Data:\n{json.dumps(stock_data, indent=2)}")
    
    
    # Combine stock entry data with balance_qty
    final_data = combine_stock_and_batchwise_data(stock_entry_data, stock_data)
    data.extend(final_data)
    
    return data


def get_stock_entry_detail_data_from_stock_entry(filters):
    
    stock_entry_detail_data = frappe.db.sql("""
        SELECT 
            ste_entry_item.parent AS stock_entry,
            ste.posting_date AS posting_date,
            ste.stock_entry_type as stock_entry_type,
            ste.work_order AS work_order,
            ste_entry_item.item_code as stock_item_code,
            ste_entry_item.t_warehouse as t_warehouse,
            ste_entry_item.batch_no as batch_no,
            ste_entry_item.stock_uom as stock_uom,
            wo.production_item AS production_item,
            wori.item_code AS required_item_code,    -- Fetching item code from Work Order Required Items
            wori.transferred_qty AS transferred_qty, 
            wori.consumed_qty AS consumed_qty,        -- Fetching consumed quantity from Work Order Required Items
            (wori.transferred_qty - IFNULL(wori.consumed_qty, 0)) AS pending_qty -- Calculating pending quantity
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
            AND (ste_entry_item.t_warehouse = 'DYE/LOT SECTION - PSS'
            OR ste_entry_item.t_warehouse like 'HTHP%%')
            AND ste.stock_entry_type like 'Material Transfer%%'
    """, as_dict=1)

    print("\n\nstock_entry_detail_data\n\n", stock_entry_detail_data)
    return stock_entry_detail_data

@frappe.whitelist()
def get_stock_data(filters):
    stock_data = []
    batchwise_data = get_batchwise_data_from_stock_ledger(filters)
    batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)

    print("\n\n\nbatchwise_data\n\n\n",batchwise_data);

    # Custom JSON encoder to handle dates
    # def custom_json_encoder(obj):
    #     if isinstance(obj, date):
    #         return obj.strftime('%Y-%m-%d')  # Convert date to string format
    #     raise TypeError(f"Type {type(obj)} not serializable")
    
    # frappe.msgprint(f"s batchwise_data Data:\n{json.dumps(batchwise_data, indent=2, default=custom_json_encoder)}")

    stock_data = parse_batchwise_data(batchwise_data)
    print("\n\nstock_data\n\n\n", stock_data)
    return stock_data


# def parse_batchwise_data(batchwise_data):
#     data = []
#     for key, d in batchwise_data.items():
#         # Skip if balance_qty is 0
#         if d.balance_qty == 0:
#             continue
        
#         # Filter by warehouse name
#         if "HTHP" in d.warehouse or "Dye/Lot" in d.warehouse:
#             data.append(d)

#     return data

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

    # Get batch-wise balance quantity
    query = frappe.db.sql("""
        SELECT 
            sle.item_code,
            sle.batch_no,
            sle.warehouse,
            SUM(sle.actual_qty) AS balance_qty
        FROM 
            `tabStock Ledger Entry` AS sle
        INNER JOIN 
            `tabBatch` AS b ON sle.batch_no = b.name
        WHERE 
            sle.is_cancelled = 0
        GROUP BY 
            sle.batch_no, sle.item_code, sle.warehouse
    """, as_dict=True)

    for d in query:
        key = (d.item_code, d.warehouse, d.batch_no)
        batchwise_data.setdefault(key, d)

    return batchwise_data


def get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters):
    # Get batch-wise balance quantity from Serial and Batch Entry
    query = frappe.db.sql("""
        SELECT 
            sle.item_code,
            sbe.batch_no,
            sle.warehouse,
            SUM(sbe.qty) AS balance_qty
        FROM 
            `tabStock Ledger Entry` AS sle
        INNER JOIN 
            `tabSerial and Batch Entry` AS sbe ON sle.serial_and_batch_bundle = sbe.parent
        INNER JOIN 
            `tabBatch` AS b ON sbe.batch_no = b.name
        WHERE 
            sle.is_cancelled = 0 
            AND sle.docstatus = 1
        GROUP BY 
            sbe.batch_no, sle.item_code, sle.warehouse
    """, as_dict=True)

    for d in query:
        key = (d.item_code, d.warehouse, d.batch_no)
        if key in batchwise_data:
            batchwise_data[key].balance_qty += flt(d.balance_qty)
        else:
            batchwise_data.setdefault(key, d)

    return batchwise_data    


@frappe.whitelist()
def combine_stock_and_batchwise_data(stock_entry_data, stock_data):
    # Convert stock_data into a dictionary for quick lookup using (batch_no, warehouse) as key
    stock_data_dict = {(d.batch_no, d.warehouse): d.balance_qty for d in stock_data}
    print("\n\n\nstock_data_dict\n\n\n",stock_data_dict)

    final_data = []
    
    for entry in stock_entry_data:
        batch_no = entry.get("batch_no")  # Get batch_no from stock_entry_data
        warehouse = entry.get("t_warehouse")  # Get target warehouse from stock_entry_data
        
        # Get stock_qty from stock_data only if batch_no and warehouse match, otherwise default to 0
        stock_qty = stock_data_dict.get((batch_no, warehouse), 0)
        
        # Append data with stock_qty added only when there's a match
        final_data.append({
            **entry,  # Keep all existing fields
            "stock_qty": stock_qty  # Add new column for stock_qty
        })

    # Custom JSON encoder to handle dates
    def custom_json_encoder(obj):
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')  # Convert date to string format
        raise TypeError(f"Type {type(obj)} not serializable")

    # Print stock_data and final_data using frappe.msgprint
    frappe.msgprint(f"Stock Data:\n{json.dumps(stock_data, indent=2, default=custom_json_encoder)}")
    frappe.msgprint(f"Final Data:\n{json.dumps(final_data, indent=2, default=custom_json_encoder)}")

    return final_data




# def combine_stock_and_batchwise_data(stock_entry_data, stock_data):
#     final_data = []
#     return final_data
    
    # for ste in stock_entry_data:
    #     final_data.append(ste)
    #     # Find matching batchwise data by item_code and batch_no
    #     # for batch in batchwise_data:
    #     #     if ste['item_code'] == batch['item_code'] and ste['batch_no'] == batch['batch_no']:
    #     #         # Add ste_qty and balance_qty together
    #     #         ste['balance_qty'] = batch['balance_qty']
    #     #         final_data.append(ste)
    
    # return final_data





