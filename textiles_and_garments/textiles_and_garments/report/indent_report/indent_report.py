# Copyright (c) 2025, Aravind and contributors
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
            "label": _("Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "label": _("Process"),
            "fieldname": "process",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Main Indent"),
            "fieldname": "for_project",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Sub Indent"),
            "fieldname": "parent",
            "fieldtype": "Link",
            "options": "Material Request",
            "width": 150,
        },
        {
            "label": _("Commercial Name"),
            "fieldname": "commercial_name",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Color"),
            "fieldname": "color",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": _("Customer"),
            "fieldname": "requested_by",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "label": _("Customer Group"),
            "fieldname": "customer_group",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "label": _("UOM"),
            "fieldname": "stock_uom",
            "fieldtype": "Data",
            "width": 70,
        },
        {
            "label": _("Item Code"),
            "fieldname": "finished_item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 200,
        },
        {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 250,
        }
    ]

    return columns

def get_data(filters):
    data = []
    sales_data = get_sales_order_data(filters)
    data.extend(sales_data)
    return data

def get_sales_order_data(filters):
    # query = """
    #     SELECT
    #         soi.item_code AS item_code,
    #         soi.commercial_name AS commercial_name,
    #         soi.color AS color,
    #         soi.width AS width,
    #         soi.custom_item_status AS custom_item_status,
    #         soi.qty AS qty,
    #         soi.rate AS rate,
    #         soi.amount AS original_amount,
    #         COALESCE(soi.delivered_qty, 0) AS delivered_qty,
    #         (soi.qty - COALESCE(soi.delivered_qty, 0)) AS pending_qty,
    #         ((soi.qty - COALESCE(soi.delivered_qty, 0)) * soi.rate) AS amount,
    #         soi.stock_uom AS stock_uom,
    #         so.transaction_date AS posting_date,
    #         so.customer AS customer,
    #         st.sales_person,
    #         so.name AS name,
    #         so.delivery_date AS delivery_date,
    #         so.docstatus AS status
    #     FROM 
    #         `tabSales Order Item` AS soi
    #     LEFT JOIN 
    #         `tabSales Order` AS so
    #     ON 
    #         so.name = soi.parent
    #     LEFT JOIN `tabSales Team` st on st.parent = so.customer    
    #     WHERE 
    #         so.docstatus = 1 AND
    #         (so.name LIKE 'PTMTO%%' OR
    #         so.name LIKE 'SOJV%%' OR
    #         so.name LIKE 'SOHO%%')
    # """
    
    query = """
        SELECT 
		    mri.date,    
		    CASE 
		        WHEN finished_item_code LIKE 'G%' THEN 'Knitting'
		        WHEN finished_item_code LIKE 'D%' THEN 'Dyeing'
		        WHEN finished_item_code LIKE 'S%' THEN 'Stentering'
		        WHEN finished_item_code LIKE 'P%' THEN 'Peach finish'
		        WHEN finished_item_code LIKE 'H%' THEN 'Heat setting'
		        ELSE 'Unknown' 
		    END AS process,
			mri.for_project, 
		    mri.parent,  
			item.commercial_name, 
		    item.color, 
		    requested_by, 
		    CASE 
		        WHEN requested_by = 'For Stock' THEN 'STOCK'
		        ELSE 'MTO' 
		    END AS customer_group,
		    mri.qty, 
		    mri.uom, 
		    mri.finished_item_code,   
		    item.item_name
		FROM `material_request_item` AS mri
		INNER JOIN item ON material_request_item.finished_item_code = item.item_code
		ORDER BY process, customer_group
        """





    conditions = []
    
    if filters.get("finished_item_code"):
        conditions.append("mri.finished_item_code = %(finished_item_code)s")
    
    if filters.get("commercial_name"):
        conditions.append("mri.commercial_name = %(commercial_name)s")
    
    if filters.get("color"):
        conditions.append("mri.color = %(color)s")
    
    if filters.get("from_date"):
        conditions.append("so.date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("so.date <= %(to_date)s")
    
    if filters.get("status"):
        conditions.append("so.status = %(status)s")
    
    if conditions:
        query += " AND " + " AND ".join(conditions)

    filter_values = {
        "item_code": filters.get("item_code"),
        "commercial_name": filters.get("commercial_name"),
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "status": filters.get("status"),
    }
    
    return frappe.db.sql(query, filter_values, as_dict=1)

