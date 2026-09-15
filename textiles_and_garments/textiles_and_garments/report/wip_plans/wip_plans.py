# Copyright (c) 2025, Aravind and contributors
# For license information,please see license.txt


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
            "label": _("Plan Items"),
            "fieldname": "plan_items",
            "fieldtype": "Link",
            "options": "Plan Items",
            "width": 100,
        },
        {
            "label": _("Plan no"),
            "fieldname": "plansNo",
            "fieldtype": "Link",
            "options": "Plans",
            "width": 100,
        },
        {
            "label": _("Process"),
            "fieldname": "operation",
            "fieldtype": "Link",
            "options": "Operation",
            "width": 100,
        },
        {
            "label": _("Item Code"),
            "fieldname": "plans_item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 250,
        },
        {
            "label": _("Commercial Name"),
            "fieldname": "commercial_name",
            "fieldtype": "data",
            "width": 250,
        },
        {
            "label": _("Color"),
            "fieldname": "color",
            "fieldtype": "data",
            "width": 250,
        },
        {
            "label": _("Sales Order"),
            "fieldname": "sales_order",
            "fieldtype": "Link",
            "options": "Sales Order",
            "width": 200,
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 240,
        },
        {
            "label": _("Plan Qty"),
            "fieldname": "plan_qty",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("Sent Qty"),
            "fieldname": "delivered_qty",
            "fieldtype": "Float",
            "width": 90,
        },
        
        {
            "label": _("Actual Sent Qty"),
            "fieldname": "actual_delivered_qty",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("Received Qty"),
            "fieldname": "recQty",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("Returned Qty"),
            "fieldname": "returned_qty",
            "fieldtype": "Float",
            "width": 90,
        },

        {
            "label": _("Balance Qty"),
            "fieldname": "balance_qty",
            "fieldtype": "Float",
            "width": 90,
        },
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



# def get_purchase_receipt_data(filters):
#     """Get received quantity from Purchase Receipt Items matching the plans_no"""
#     logger.info("Starting get_purchase_receipt_data with filters: %s", filters)
    
#     query = """
#         SELECT 
#             pri.item_code,
#             pri.batch_no,
#             pri.warehouse,
#             pri.custom_plans as plans_no,
#             SUM(pri.qty) as received_qty
#         FROM `tabPurchase Receipt Item` AS pri
#         JOIN `tabPurchase Receipt` AS pr ON pr.name = pri.parent
#         WHERE pr.docstatus = 1
#     """

#     conditions = []
#     if filters.get("from_date"):
#         conditions.append("pr.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions.append("pr.posting_date <= %(to_date)s")
#     if filters.get("item_code"):
#         conditions.append("pri.item_code = %(item_code)s")
#     if filters.get("warehouse"):
#         conditions.append("pri.warehouse = %(warehouse)s")
#     if filters.get("batch_no"):
#         conditions.append("pri.batch_no = %(batch_no)s")
#     if filters.get("plans_no"):
#         conditions.append("pri.custom_plans = %(plans_no)s")

#     if conditions:
#         query += " AND " + " AND ".join(conditions)

#     query += " GROUP BY pri.item_code, pri.warehouse, pri.batch_no, pri.custom_plans"

#     values = {
#         "from_date": filters.get("from_date"),
#         "to_date": filters.get("to_date"),
#         "item_code": filters.get("item_code"),
#         "warehouse": filters.get("warehouse"),
#         "batch_no": filters.get("batch_no"),
#         "plans_no": filters.get("plans_no"),
#     }

#     results = frappe.db.sql(query, values, as_dict=True)
#     logger.info("Purchase Receipt query returned %d results", len(results))
    
#     # Create a dictionary for easy lookup
#     pr_data = {}
#     for row in results:
#         key = (row.item_code, row.plans_no)
#         pr_data[key] = row.received_qty
        
#     return pr_data

# def get_subcontracting_receipt_data(filters):
#     """Get received quantity from Subcontracting Receipt Items matching the plans_no"""
#     logger.info("Starting get_subcontracting_receipt_data with filters: %s", filters)
    
#     query = """
#         SELECT 
#             sri.item_code,
#             sri.batch_no,
#             sri.warehouse,
#             sri.custom_plans as plans_no,
#             SUM(sri.received_qty) as subcontract_received_qty
#         FROM `tabSubcontracting Receipt Item` AS sri
#         JOIN `tabSubcontracting Receipt` AS sr ON sr.name = sri.parent
#         WHERE sr.docstatus = 1 and sri.custom_plans ='PPS/0218'
#     """

#     conditions = []
#     if filters.get("from_date"):
#         conditions.append("sr.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions.append("sr.posting_date <= %(to_date)s")
#     if filters.get("item_code"):
#         conditions.append("sri.item_code = %(item_code)s")
#     if filters.get("warehouse"):
#         conditions.append("sri.warehouse = %(warehouse)s")
#     if filters.get("batch_no"):
#         conditions.append("sri.batch_no = %(batch_no)s")
#     if filters.get("plans_no"):
#         conditions.append("sri.custom_plans = %(plans_no)s")

#     if conditions:
#         query += " AND " + " AND ".join(conditions)

#     query += " GROUP BY sri.item_code, sri.warehouse, sri.batch_no, sri.custom_plans"

#     values = {
#         "from_date": filters.get("from_date"),
#         "to_date": filters.get("to_date"),
#         "item_code": filters.get("item_code"),
#         "warehouse": filters.get("warehouse"),
#         "batch_no": filters.get("batch_no"),
#         "plans_no": filters.get("plans_no"),
#     }

#     results = frappe.db.sql(query, values, as_dict=True)
#     logger.info("Subcontracting Receipt query returned %d results", len(results))
    
#     # Create a dictionary for easy lookup
#     scr_data = {}
#     for row in results:
#         key = (row.item_code,  row.plans_no)
#         scr_data[key] = row.subcontract_received_qty
        
#     print("\n\nscr_data\n\n",scr_data)
#     logger.info("Subcontracting Receipt scr_data: %s ", (scr_data))
#     return scr_data


# def get_production_stock_reservation_data(filters, batchwise_stock):
#     # Log the start of the function
#     logger.info("Starting get_production_stock_reservation_data with filters: %s", filters)
    
#     # Get purchase receipt and subcontracting receipt data
#     pr_data = get_purchase_receipt_data(filters)
#     scr_data = get_subcontracting_receipt_data(filters)
    
#     query = """
#         SELECT 
#             plans.item_code as plans_item_code,
#             plans.plan_items as plan_items,
#             plans.posting_date as posting_date,
#             plans.sales_order as sales_order,
#             plans.customer as customer,
#             plans.plan_qty as plan_qty,
#             item.item_name,
#             item.commercial_name,
#             item.color,
#             item.custom_operation as operation,
#             psr.plans_no,
#             psr.voucher_qty as qty,
#             psr.stock_uom as uom,
#             psri.warehouse,
#             psri.batch_no,
#             psr.reserved_qty as reserved_qty,
#             psri.returned_qty as returned_qty,
#             psri.short_close_qty,
#             psri.delivered_qty,
#             psri.actual_delivered_qty,
#             psr.docstatus,
#             psr.creation
#         FROM `tabProduction Stock Reservation` AS psr
#         JOIN `tabPlans` AS plans ON plans.name = psr.plans_no
#         JOIN `tabSerial and Batch Entry Plans` AS psri ON psri.parent = psr.name
#         JOIN `tabItem` AS item ON item.item_code = plans.item_code
#         WHERE plans.docstatus != 2 and plans.plan_items = 'PLAN/0029'
#     """

    

#     conditions = []
#     if filters.get("from_date"):
#         conditions.append("psr.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions.append("psr.posting_date <= %(to_date)s")
#     if filters.get("item_code"):
#         conditions.append("plans.item_code = %(item_code)s")
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

#     results = frappe.db.sql(query, values, as_dict=True)
#     print("\n\n wip results\n\n",results)
#     logger.info("Query returned %d results", len(results))

#     previous_avail_map = {}

#     for row in results:
#         key = (row.item_code, row.warehouse, row.batch_no, row.plans_no)
#         print("\n\nkey\n\n",key)
#         logger.debug("Processing row with key: %s", key)

#         purchase_receipt_key =(row.item_code, row.plans_no)
#         subcontract_receipt_key =(row.item_code, row.plans_no)
#         print("\n\nsubcontract_receipt_key\n\n",subcontract_receipt_key)
#         print("\n\nsubcontract_receipt_key\n\n",scr_data.get(subcontract_receipt_key, 0.0))

#         # Add received_qty from purchase receipt and subcontracting receipt if available
#         row.received_qty = flt(pr_data.get(purchase_receipt_key, 0.0))
#         row.subcontract_received_qty = flt(scr_data.get(subcontract_receipt_key, 0.0))

#         row.recQty = max(flt(row.received_qty), flt(row.subcontract_received_qty))
#         # row.delivered_qty = row.actual_delivered_qty
#         row.balance_qty = row.delivered_qty - (row.recQty + row.returned_qty)
        
#     return results



# def get_production_stock_reservation_data(filters, batchwise_stock):
#     logger.info("Starting get_production_stock_reservation_data with filters: %s", filters)
    
#     # First get the PSR data
#     query = """
#         SELECT 
#             plans.item_code as plans_item_code,
#             plans.plan_items as plan_items,
#             plans.posting_date as posting_date,
#             plans.sales_order as sales_order,
#             plans.customer as customer,
#             plans.plan_qty as plan_qty,
#             item.item_name,
#             item.commercial_name,
#             item.color,
#             item.custom_operation as operation,
#             psr.plans_no,
#             psr.voucher_qty as qty,
#             psr.stock_uom as uom,
#             psri.warehouse,
#             psri.batch_no,
#             psr.reserved_qty as reserved_qty,
#             psri.returned_qty as returned_qty,
#             psri.short_close_qty,
#             psri.delivered_qty,
#             psri.actual_delivered_qty,
#             psr.docstatus,
#             psr.creation
#         FROM `tabProduction Stock Reservation` AS psr
#         JOIN `tabPlans` AS plans ON plans.name = psr.plans_no
#         JOIN `tabSerial and Batch Entry Plans` AS psri ON psri.parent = psr.name
#         JOIN `tabItem` AS item ON item.item_code = plans.item_code
#         WHERE plans.docstatus != 2
#     """

#     conditions = []
#     if filters.get("from_date"):
#         conditions.append("psr.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions.append("psr.posting_date <= %(to_date)s")
#     if filters.get("item_code"):
#         conditions.append("plans.item_code = %(item_code)s")
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

#     results = frappe.db.sql(query, values, as_dict=True)
#     logger.info("PSR query returned %d results", len(results))

#     if not results:
#         return results

#     # Collect unique item_code + plans_no combinations from PSR results
#     unique_combinations = set()
#     for row in results:
#         unique_combinations.add((row.plans_item_code, row.plans_no))

#     # Now fetch PR and SCR data only for these combinations
#     pr_filters = filters.copy()
#     pr_filters["item_codes"] = [x[0] for x in unique_combinations]
#     pr_filters["plans_nos"] = [x[1] for x in unique_combinations]
    
#     pr_data = get_purchase_receipt_data(pr_filters)
#     scr_data = get_subcontracting_receipt_data(pr_filters)

#     # Process the results
#     for row in results:
#         key = (row.plans_item_code, row.plans_no)
        
#         # Add received_qty from purchase receipt and subcontracting receipt if available
#         row.received_qty = flt(pr_data.get(key, 0.0))
#         row.subcontract_received_qty = flt(scr_data.get(key, 0.0))

#         row.recQty = max(flt(row.received_qty), flt(row.subcontract_received_qty))
#         row.balance_qty = row.delivered_qty - (row.recQty + row.returned_qty)
        
#     return results

def get_production_stock_reservation_data(filters, batchwise_stock):
    logger.info("Starting get_production_stock_reservation_data with filters: %s", filters)
    
    # First get the base plan items data
    base_query = """
        SELECT 
            pi.name as plan_items,
            pid.name as plan_item_detail,
            pid.item_code as plans_item_code,
            pid.plan_qty as plan_qty,
            pid.docstatus,
            pid.parent as plan_items_parent,
            pid.plan as plansNo,
            pi.posting_date,
            pi.sales_order,
            pi.customer,
            item.item_name,
            item.commercial_name,
            item.color,
            item.custom_operation as operation,
            item.stock_uom as uom,
            pid.creation
        FROM `tabPlan Item Planned Wise` AS pid
        INNER JOIN `tabPlan Items` AS pi ON pi.name = pid.parent
        LEFT JOIN `tabItem` AS item ON item.item_code = pid.item_code
        WHERE pid.docstatus != 2 and pid.parent = 'PLAN/0031'
    """

    base_conditions = []
    if filters.get("from_date"):
        base_conditions.append("pi.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        base_conditions.append("pi.posting_date <= %(to_date)s")
    if filters.get("item_code"):
        base_conditions.append("pid.item_code = %(item_code)s")
    if filters.get("plans_no"):
        base_conditions.append("pi.name = %(plans_no)s")

    if base_conditions:
        base_query += " AND " + " AND ".join(base_conditions)

    base_query += " ORDER BY pid.creation"

    base_values = {
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "item_code": filters.get("item_code"),
        "plans_no": filters.get("plans_no"),
    }

    base_results = frappe.db.sql(base_query, base_values, as_dict=True)
    print("\n\nbase_results\n\n",base_results)
    logger.info("Base plan items query returned %d results", len(base_results))

    if not base_results:
        return []

    # Collect unique plan_items and item_codes for production data query
    plan_items = list(set([row.plan_items for row in base_results]))
    item_codes = list(set([row.plans_item_code for row in base_results]))

    # Now fetch production stock reservation data for these plan items and item codes
    production_query = """
        SELECT 
            psr.name,
            psr.plans_no,
            psr.plan_items,
            plans.item_code as item_code,
            batch.item,
            psri.warehouse,
            psri.batch_no,
            psr.reserved_qty,
            psri.returned_qty,
            psri.short_close_qty,
            psri.delivered_qty,
            psri.actual_delivered_qty,
            psr.voucher_qty as qty
        FROM `tabProduction Stock Reservation` AS psr
        JOIN `tabSerial and Batch Entry Plans` AS psri ON psri.parent = psr.name
        JOIN `tabBatch` AS batch ON batch.name = psri.batch_no
        JOIN `tabPlans` AS plans ON plans.name = psr.plans_no
        WHERE psr.docstatus = 1
        AND psr.plan_items IN %(plan_items)s
        and psr.plan_items = 'PLAN/0031'
        ORDER BY psr.name asc
    """

    production_values = {
        "plan_items": plan_items,
        "item_codes": item_codes
    }
    print("\n\nproduction_values FULL QUERY:\n", production_query % production_values)

    production_results = frappe.db.sql(production_query, production_values, as_dict=True)
    print("\n\nproduction_results\n\n",production_results)
    logger.info("Production stock reservation query returned %d results", len(production_results))

    # Create a dictionary to map plan_items+item_code to production data
    production_map = {}
    for prod_row in production_results:
        key = (prod_row.plan_items, prod_row.item)
        print("\n\nkey\n\n",key)
        if key not in production_map:
            production_map[key] = []
        production_map[key].append(prod_row)

    # Now combine base results with production data
    combined_results = []
    for base_row in base_results:
        key = (base_row.plan_items, base_row.plans_item_code)
        production_rows = production_map.get(key, [])
        print("\n\nproduction_rows\n\n",production_rows)

        if production_rows:
            for prod_row in production_rows:
                print("\n\nprod_row\n\n",prod_row)
                combined_row = base_row.copy()
                combined_row.update({
                    "plans_no": prod_row.plans_no,
                    "warehouse": prod_row.warehouse,
                    "batch_no": prod_row.batch_no,
                    "reserved_qty": prod_row.reserved_qty,
                    "returned_qty": prod_row.returned_qty,
                    "short_close_qty": prod_row.short_close_qty,
                    "delivered_qty": prod_row.delivered_qty,
                    "actual_delivered_qty": prod_row.actual_delivered_qty,
                    "qty": prod_row.qty
                })
                combined_results.append(combined_row)
        else:
            # Include base data even if no production data exists
            combined_results.append(base_row)

    # Now get PR and SCR data for the combined results
    print("\n\ncombined_results\n\n",combined_results)
    unique_combinations = set()
    for row in combined_results:
        if hasattr(row, 'plans_item_code') and hasattr(row, 'plansNo'):
            unique_combinations.add((row.plans_item_code, row.plansNo))

    if unique_combinations:
        pr_filters = filters.copy()
        pr_filters["item_codes"] = [x[0] for x in unique_combinations]
        pr_filters["plans_nos"] = [x[1] for x in unique_combinations]
        
        
        pr_data = get_purchase_receipt_data(pr_filters)
        print("\n\npr_data\n\n",pr_data)
        scr_data = get_subcontracting_receipt_data(pr_filters)

        # Add PR and SCR data to combined results
        print("\n\n after pr and scr combined_results\n\n",combined_results)
        for row in combined_results:
            if hasattr(row, 'plans_item_code') and hasattr(row, 'plans_no'):
                key = (row.plans_item_code, row.plansNo)
                row.received_qty = flt(pr_data.get(key, 0.0))
                row.subcontract_received_qty = flt(scr_data.get(key, 0.0))
                row.recQty = max(flt(row.received_qty), flt(row.subcontract_received_qty))
                if hasattr(row, 'delivered_qty') and hasattr(row, 'returned_qty'):
                    row.balance_qty = flt(row.delivered_qty) - (flt(row.recQty) + flt(row.returned_qty))

    return combined_results

def get_purchase_receipt_data(filters):
    """Get received quantity from Purchase Receipt Items matching the plans_no"""
    logger.info("Starting get_purchase_receipt_data with filters: %s", filters)
    
    query = """
        SELECT 
            pri.item_code,
            pri.batch_no,
            pri.warehouse,
            pri.custom_plans as plans_no,
            SUM(pri.qty) as received_qty
        FROM `tabPurchase Receipt Item` AS pri
        JOIN `tabPurchase Receipt` AS pr ON pr.name = pri.parent
        WHERE pr.docstatus = 1
    """

    conditions = []
    if filters.get("from_date"):
        conditions.append("pr.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("pr.posting_date <= %(to_date)s")
    if filters.get("item_code"):
        conditions.append("pri.item_code = %(item_code)s")
    elif filters.get("item_codes"):
        conditions.append("pri.item_code IN %(item_codes)s")
    if filters.get("warehouse"):
        conditions.append("pri.warehouse = %(warehouse)s")
    if filters.get("batch_no"):
        conditions.append("pri.batch_no = %(batch_no)s")
    if filters.get("plans_no"):
        conditions.append("pri.custom_plans = %(plans_no)s")
    # elif filters.get("plans_nos"):
    #     conditions.append("pri.custom_plans IN %(plans_nos)s")

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " GROUP BY  pri.custom_plans, pri.item_code, pri.warehouse, pri.batch_no"

    values = {
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "item_code": filters.get("item_code"),
        "item_codes": filters.get("item_codes"),
        "warehouse": filters.get("warehouse"),
        "batch_no": filters.get("batch_no"),
        "plans_no": filters.get("plans_no"),
        # "plans_nos": filters.get("plans_nos"),
    }
    print("\n\nFULL QUERY:\n", query % values)

    print("\n\nvalues\n\n",values)

    results = frappe.db.sql(query, values, as_dict=True)
    print("\n\nresults\n\n",results)
    logger.info("Purchase Receipt query returned %d results", len(results))
    
    # Create a dictionary for easy lookup
    pr_data = {}
    for row in results:
        key = (row.item_code, row.plans_no)
        pr_data[key] = row.received_qty
        
    print("\n\npr_data\n\n",pr_data)
    return pr_data

def get_subcontracting_receipt_data(filters):
    """Get received quantity from Subcontracting Receipt Items matching the plans_no"""
    logger.info("Starting get_subcontracting_receipt_data with filters: %s", filters)
    
    query = """
        SELECT 
            sri.item_code,
            sri.batch_no,
            sri.warehouse,
            sri.custom_plans as plans_no,
            SUM(sri.received_qty) as subcontract_received_qty
        FROM `tabSubcontracting Receipt Item` AS sri
        JOIN `tabSubcontracting Receipt` AS sr ON sr.name = sri.parent
        WHERE sr.docstatus = 1
    """

    conditions = []
    if filters.get("from_date"):
        conditions.append("sr.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("sr.posting_date <= %(to_date)s")
    if filters.get("item_code"):
        conditions.append("sri.item_code = %(item_code)s")
    elif filters.get("item_codes"):
        conditions.append("sri.item_code IN %(item_codes)s")
    if filters.get("warehouse"):
        conditions.append("sri.warehouse = %(warehouse)s")
    if filters.get("batch_no"):
        conditions.append("sri.batch_no = %(batch_no)s")
    if filters.get("plans_no"):
        conditions.append("sri.custom_plans = %(plans_no)s")
    # elif filters.get("plans_nos"):
    #     conditions.append("sri.custom_plans IN %(plans_nos)s")

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " GROUP BY sri.item_code, sri.warehouse, sri.batch_no, sri.custom_plans"

    values = {
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "item_code": filters.get("item_code"),
        "item_codes": filters.get("item_codes"),
        "warehouse": filters.get("warehouse"),
        "batch_no": filters.get("batch_no"),
        "plans_no": filters.get("plans_no"),
        # "plans_nos": filters.get("plans_nos"),
    }

    results = frappe.db.sql(query, values, as_dict=True)
    print("\n\nscr results\n\n",results)
    logger.info("Subcontracting Receipt query returned %d results", len(results))
    
    # Create a dictionary for easy lookup
    scr_data = {}
    for row in results:
        key = (row.item_code, row.plans_no)
        scr_data[key] = row.subcontract_received_qty
        
    print("\n\nscr_data\n\n",scr_data)
    return scr_data



# def get_production_stock_reservation_data(filters, batchwise_stock):
#     logger.info("Starting get_production_stock_reservation_data with filters: %s", filters)
    
#     # Build base query for Plan Items Detail
#     base_query = """
#         SELECT 
#             pi.name as plan_items,
#             pid.name as plan_item_detail,
#             pid.item_code as plans_item_code,
#             pid.qty as plan_qty,
#             pid.docstatus,
#             pid.parent as plan_items_parent,
#             pi.posting_date,
#             pi.sales_order,
#             pi.customer,
#             item.item_name,
#             item.commercial_name,
#             item.color,
#             item.custom_operation as operation,
#             item.stock_uom as uom,
#             pid.creation
#         FROM `tabPlan Items Detail` AS pid
#         INNER JOIN `tabPlan Items` AS pi ON pi.name = pid.parent
#         LEFT JOIN `tabItem` AS item ON item.item_code = pid.item_code
#         WHERE pid.parent = 'PLAN/0029'
#     """

#     # Build production data query (removed non-existent plan_item_detail column)
#     production_query = """
#         SELECT 
#             psr.name,
#             psr.plans_no,
#             psr.plan_items,
#             batch.item_code
#             psri.warehouse,
#             psri.batch_no,
#             psr.reserved_qty,
#             psri.returned_qty,
#             psri.short_close_qty,
#             psri.delivered_qty,
#             psri.actual_delivered_qty,
#             psr.voucher_qty as qty
#         FROM `tabProduction Stock Reservation` AS psr
#         JOIN `tabSerial and Batch Entry Plans` AS psri ON psri.parent = psr.name
#         JOIN `tabBatch` AS batch ON batch.item_code = psri.batch_no
#         WHERE psr.docstatus = 1 ORDER BY psr.name asc
#     """

#     # Build conditions for both queries
#     base_conditions = []
#     prod_conditions = []
#     values = {}

#     # Common filters
#     if filters.get("plans_no"):
#         base_conditions.append("pid.parent = %(plans_no)s")
#         prod_conditions.append("psr.plans_no = %(plans_no)s")
#         values["plans_no"] = filters["plans_no"]

#     if filters.get("from_date"):
#         base_conditions.append("pi.posting_date >= %(from_date)s")
#         values["from_date"] = filters["from_date"]

#     if filters.get("to_date"):
#         base_conditions.append("pi.posting_date <= %(to_date)s")
#         values["to_date"] = filters["to_date"]

#     if filters.get("item_code"):
#         base_conditions.append("pid.item_code = %(item_code)s")
#         values["item_code"] = filters["item_code"]

#     if filters.get("warehouse"):
#         prod_conditions.append("psri.warehouse = %(warehouse)s")
#         values["warehouse"] = filters["warehouse"]

#     if filters.get("batch_no"):
#         prod_conditions.append("psri.batch_no = %(batch_no)s")
#         values["batch_no"] = filters["batch_no"]

#     # Apply conditions to queries
#     if base_conditions:
#         base_query += " AND " + " AND ".join(base_conditions)

#     if prod_conditions:
#         production_query += " AND " + " AND ".join(prod_conditions)

#     # Execute queries
#     try:
#         plan_results = frappe.db.sql(base_query, values, as_dict=True)
#         production_results = frappe.db.sql(production_query, values, as_dict=True)
        
#         logger.info("Found %d plan items and %d production records", 
#                    len(plan_results), len(production_results))
#     except Exception as e:
#         frappe.log_error(f"Query failed: {str(e)}\nBase Query: {base_query}\nProduction Query: {production_query}\nValues: {values}")
#         raise

#     # Create a dictionary to map item_code to production data
#     production_data_map = {}
#     for prod in production_results:
#         key = prod.get("item_code")
#         production_data_map[key] = prod

#     # Merge results using item_code as key
#     for plan_row in plan_results:
#         key = plan_row.get("plans_item_code")
#         production_data = production_data_map.get(key, {})
        
#         plan_row.update({
#             "plans_no": production_data.get("plans_no"),
#             "warehouse": production_data.get("warehouse"),
#             "batch_no": production_data.get("batch_no"),
#             "reserved_qty": production_data.get("reserved_qty", 0),
#             "returned_qty": production_data.get("returned_qty", 0),
#             "short_close_qty": production_data.get("short_close_qty", 0),
#             "delivered_qty": production_data.get("delivered_qty", 0),
#             "actual_delivered_qty": production_data.get("actual_delivered_qty", 0),
#             "qty": production_data.get("qty", 0)
#         })

#     # Get purchase and subcontracting data
#     item_plan_combinations = {
#         (row["plans_item_code"], row["plans_no"]) 
#         for row in plan_results 
#         if row.get("plans_item_code") and row.get("plans_no")
#     }
    
#     pr_data = get_purchase_receipt_data(filters, item_plan_combinations)
#     scr_data = get_subcontracting_receipt_data(filters, item_plan_combinations)

#     # Calculate final quantities per item
#     for row in plan_results:
#         p_key = (row["plans_item_code"], row["plans_no"]) if row.get("plans_item_code") and row.get("plans_no") else None
#         s_key = p_key  # Same key for both
        
#         row["received_qty"] = flt(pr_data.get(p_key, 0)) if p_key else 0
#         row["subcontract_received_qty"] = flt(scr_data.get(s_key, 0)) if s_key else 0
#         row["recQty"] = max(row["received_qty"], row["subcontract_received_qty"])
#         row["balance_qty"] = flt(row.get("delivered_qty", 0)) - (row["recQty"] + flt(row.get("returned_qty", 0)))
        
#     return plan_results





# def get_purchase_receipt_data(filters, item_plan_combinations):
#     """Get received quantity from Purchase Receipt Items matching the plans_no"""
#     logger.info("Starting get_purchase_receipt_data with filters: %s", filters)
    
#     if not item_plan_combinations:
#         return {}
    
#     # Create a list of conditions for item_code and plans_no combinations
#     item_conditions = []
#     plan_conditions = []
#     for item_code, plans_no in item_plan_combinations:
#         item_conditions.append(f"pri.item_code = '{item_code}'")
#         plan_conditions.append(f"pri.custom_plans = '{plans_no}'")
    
#     query = f"""
#         SELECT 
#             pri.item_code,
#             pri.custom_plans as plans_no,
#             SUM(pri.qty) as received_qty
#         FROM `tabPurchase Receipt Item` AS pri
#         JOIN `tabPurchase Receipt` AS pr ON pr.name = pri.parent
#         WHERE pr.docstatus = 1
#           AND ({' OR '.join(item_conditions)})
#           AND ({' OR '.join(plan_conditions)})
#     """

#     if filters.get("from_date"):
#         query += f" AND pr.posting_date >= '{filters.get('from_date')}'"
#     if filters.get("to_date"):
#         query += f" AND pr.posting_date <= '{filters.get('to_date')}'"

#     query += " GROUP BY pri.item_code, pri.custom_plans"

#     results = frappe.db.sql(query, as_dict=True)
#     logger.info("Purchase Receipt query returned %d results", len(results))
    
#     # Create a dictionary for easy lookup
#     pr_data = {}
#     for row in results:
#         key = (row.item_code, row.plans_no)
#         pr_data[key] = row.received_qty
        
#     return pr_data

# def get_subcontracting_receipt_data(filters, item_plan_combinations):
#     """Get received quantity from Subcontracting Receipt Items matching the plans_no"""
#     logger.info("Starting get_subcontracting_receipt_data with filters: %s", filters)
    
#     if not item_plan_combinations:
#         return {}
    
#     # Create a list of conditions for item_code and plans_no combinations
#     item_conditions = []
#     plan_conditions = []
#     for item_code, plans_no in item_plan_combinations:
#         item_conditions.append(f"sri.item_code = '{item_code}'")
#         plan_conditions.append(f"sri.custom_plans = '{plans_no}'")
    
#     query = f"""
#         SELECT 
#             sri.item_code,
#             sri.custom_plans as plans_no,
#             SUM(sri.received_qty) as subcontract_received_qty
#         FROM `tabSubcontracting Receipt Item` AS sri
#         JOIN `tabSubcontracting Receipt` AS sr ON sr.name = sri.parent
#         WHERE sr.docstatus = 1
#           AND ({' OR '.join(item_conditions)})
#           AND ({' OR '.join(plan_conditions)})
#     """

#     if filters.get("from_date"):
#         query += f" AND sr.posting_date >= '{filters.get('from_date')}'"
#     if filters.get("to_date"):
#         query += f" AND sr.posting_date <= '{filters.get('to_date')}'"

#     query += " GROUP BY sri.item_code, sri.custom_plans"

#     results = frappe.db.sql(query, as_dict=True)
#     logger.info("Subcontracting Receipt query returned %d results", len(results))
    
#     # Create a dictionary for easy lookup
#     scr_data = {}
#     for row in results:
#         key = (row.item_code, row.plans_no)
#         scr_data[key] = row.subcontract_received_qty
        
#     logger.info("Subcontracting Receipt scr_data: %s", scr_data)
#     return scr_data



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
