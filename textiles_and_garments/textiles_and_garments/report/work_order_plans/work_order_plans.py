# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

# Copyright (c) 2025, Aravind and contributors
# For license information,please see license.txt

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
        #     "label": _("Date"),
        #     "fieldname": "posting_date",
        #     "fieldtype": "Date",
        #     "width": 150,
        # },
        {
            "label": _("Parent Plan no"),
            "fieldname": "parent_plansNo",
            "fieldtype": "Link",
            "options": "Plan Items",
            "width": 100,
        },
        {
            "label": _("Plan Items"),
            "fieldname": "custom_plan_items",
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
            "label": _("Work Order"),
            "fieldname": "work_order",
            "fieldtype": "Link",
            "options": "Work Order",
            "width": 200,
        },
        {
            "label": _("Sales Order"),
            "fieldname": "sales_order",
            "fieldtype": "Link",
            "options": "Sales Order",
            "width": 200,
        },
        # {
        #     "label": _("Process"),
        #     "fieldname": "process",
        #     "fieldtype": "Data",
        #     "width": 100,
        # },
        # {
        #     "label": _("Customer"),
        #     "fieldname": "requested_by",
        #     "fieldtype": "Data",
        #     "width": 150,
        # },
        # {
        #     "label": _("Customer Group"),
        #     "fieldname": "customer_group",
        #     "fieldtype": "Data",
        #     "width": 150,
        # },
        
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 200,
        },
        # {
        #     "label": _("Item Name"),
        #     "fieldname": "item_name",
        #     "fieldtype": "Data",
        #     "width": 250,
        # },
        {
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("MTM Qty"),
            "fieldname": "material_transferred_for_manufacturing",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("MF Qty"),
            "fieldname": "produced_qty",
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
            "width": 250,
        }
    ]

    return columns

def get_data(filters):
    data = []
    wo_data = get_work_order_data(filters)
    data.extend(wo_data)
    return data

def get_work_order_data(filters):
    # query = """
    #     SELECT 
    #         mr.date as posting_date,    
    #         CASE 
    #             WHEN mri.finished_item_code LIKE 'G%%' THEN 'Knitting'
    #             WHEN mri.finished_item_code LIKE 'D%%' THEN 'Dyeing'
    #             WHEN mri.finished_item_code LIKE 'S%%' THEN 'Stenter'
    #             WHEN mri.finished_item_code LIKE 'PF%%' THEN 'Peach finish'
    #             WHEN mri.finished_item_code LIKE 'H%%' THEN 'Heat setting'
    #             WHEN mri.finished_item_code LIKE 'WH%%' THEN 'OW Heat setting'
    #             WHEN mri.finished_item_code LIKE 'PK%%' THEN 'Printing'
    #             ELSE 'Unknown' 
    #         END AS process,
    #         mri.for_project, 
    #         mri.parent,  
    #         item.commercial_name, 
    #         item.color, 
    #         mr.requested_by, 
    #         CASE 
    #             WHEN mr.requested_by = 'For Stock' THEN 'STOCK'
    #             ELSE 'MTO' 
    #         END AS customer_group,
    #         mri.qty, 
    #         mri.uom, 
    #         mri.finished_item_code,
    #         item.item_name,
    #         mr.docstatus
    #     FROM `tabMaterial Request` AS mr
    #     JOIN `tabMaterial Request Item` AS mri ON mri.parent = mr.name
    #     JOIN `tabItem` AS item ON item.name = mri.finished_item_code
    # """

    # query = """
    #     SELECT 
    #         mr.date as posting_date,
    #         CASE 
    #             WHEN mri.finished_item_code LIKE 'G%%' THEN 'Knitting'
    #             WHEN mri.finished_item_code LIKE 'D%%' THEN 'Dyeing'
    #             WHEN mri.finished_item_code LIKE 'S%%' THEN 'Stenter'
    #             WHEN mri.finished_item_code LIKE 'PF%%' THEN 'Peach finish'
    #             WHEN mri.finished_item_code LIKE 'H%%' THEN 'Heat setting'
    #             WHEN mri.finished_item_code LIKE 'WH%%' THEN 'OW Heat setting'
    #             WHEN mri.finished_item_code LIKE 'PK%%' THEN 'Printing'
    #             ELSE 'Unknown' 
    #         END AS process,
    #         mri.for_project,
    #         mri.parent,
    #         mri.custom_commercial_name as commercial_name, 
    #         mri.custom_color as color, 
    #         mr.requested_by, 
    #         CASE 
    #             WHEN mr.requested_by = 'For Stock' THEN 'STOCK'
    #             ELSE 'MTO' 
    #         END AS customer_group,
    #         mri.qty, 
    #         mri.uom as uom,
    #         mri.finished_item_code,
    #         item.item_name,
    #         mr.docstatus
    #     FROM `tabMaterial Request` AS mr
    #     JOIN `tabMaterial Request Item` AS mri ON mri.parent = mr.name
    #     JOIN `tabItem` AS item ON item.name = mri.item_code
    # """

    # query = """
    #     SELECT 
    #         wo.transaction_date as posting_date,
    #         wo.custom_plan_items,
    #         wo.custom_plans,
    #         wo.production_item as item_code,
    #         wo.custom_commercial_name as commercial_name, 
    #         wo.custom_color as color, 
    #         wo.qty, 
    #         wo.uom as uom,
    #         wo.material_transferred_for_manufacturing,
    #         wo.produced_qty,
    #         item.item_name,
    #         wo.docstatus
    #     FROM `tabWork Order` AS wo
    #     JOIN `tabItem` AS item ON item.item_code = wo.production_item
    # """

    query = """
	    SELECT 
		    CASE 
		        WHEN wo.custom_parent_plan_no IS NOT NULL AND wo.custom_parent_plan_no != '' 
		        THEN wo.custom_parent_plan_no 
		        WHEN wo.custom_parent_po_plan_no IS NOT NULL AND wo.custom_parent_po_plan_no != ''
		        THEN wo.custom_parent_po_plan_no
		        ELSE wo.custom_plans
		    END as parent_plansNo,
		    wo.custom_plan_items as custom_plan_items,
		    wo.custom_plans as plansNo,
		    wo.name as work_order,
		    wo.production_item as item_code,
		    wo.custom_commercial_name as commercial_name, 
		    wo.custom_color as color, 
		    wo.qty, 
		    wo.stock_uom as uom,
		    wo.material_transferred_for_manufacturing,
		    wo.produced_qty,
		    item.item_name,
		    wo.docstatus
		FROM `tabWork Order` AS wo
		JOIN `tabItem` AS item ON item.item_code = wo.production_item
		WHERE wo.docstatus = 1
	"""

    conditions = []

    # if filters.get("from_date"):
    #     conditions.append("wo.date >= %(from_date)s")
    # if filters.get("to_date"):
    #     conditions.append("wo.date <= %(to_date)s")
    if filters.get("item_code"):
        conditions.append("wo.production_item = %(item_code)s")
    if filters.get("commercial_name"):
        conditions.append("wo.custom_commercial_name = %(commercial_name)s")
    if filters.get("color"):
        conditions.append("wo.custom_color = %(color)s")
    if filters.get("docstatus") is not None:
        conditions.append("wo.docstatus = %(docstatus)s")


    # Only add WHERE clause if there are conditions
    if conditions:
        query += " WHERE " + " AND ".join(conditions)



    filter_values = {
        "item_code": filters.get("finished_item_code") or None,
        "commercial_name": filters.get("commercial_name") or None,
        "color": filters.get("color") or None,
        # "from_date": filters.get("from_date"),
        # "to_date": filters.get("to_date"),
        "docstatus": int(filters.get("docstatus")) if filters.get("docstatus") else None,
    }

    
    return frappe.db.sql(query, filter_values, as_dict=1)


