# Copyright (c) 2026, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	"""Define report columns"""
	return [
		{
			"fieldname": "name",
			"label": _("Awaiting GRN ID"),
			"fieldtype": "Link",
			"options": "Awaiting GRN",
			"width": 150
		},
		{
			"fieldname": "supplier",
			"label": _("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 180
		},
		{
			"fieldname": "supplier_invoicedc_no",
			"label": _("Supplier DC No"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "supplier_invoicedc_date",
			"label": _("DC Date"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "posting_date",
			"label": _("Posting Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "posting_time",
			"label": _("Posting Time"),
			"fieldtype": "Time",
			"width": 100
		},
		{
			"fieldname": "total_qty",
			"label": _("Total Qty"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "total_gross_weight",
			"label": _("Total Gross Weight"),
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "aging_days",
			"label": _("Aging (Days)"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "owner",
			"label": _("Created By"),
			"fieldtype": "Link",
			"options": "User",
			"width": 150
		}
	]

def get_data(filters):
	"""Fetch pending GRN data where purchase_receipt is empty"""
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(f"""
		SELECT 
			grn.name,
			grn.supplier,
			grn.supplier_invoicedc_no,
			grn.supplier_invoicedc_date,
			grn.posting_date,
			grn.posting_time,
			grn.owner,
			SUM(item.qty) as total_qty,
			SUM(item.gross_weight) as total_gross_weight,
			DATEDIFF(CURDATE(), grn.posting_date) as aging_days
		FROM 
			`tabAwaiting GRN` grn
		LEFT JOIN 
			`tabAwaitingGRNItem` item ON item.parent = grn.name
		WHERE 
			grn.docstatus = 1
			AND (grn.purchase_receipt IS NULL OR grn.purchase_receipt = '')
			{conditions}
		GROUP BY 
			grn.name
		ORDER BY 
			grn.posting_date ASC
	""", filters, as_dict=1)
	
	return data

def get_conditions(filters):
	"""Build filter conditions based on user input"""
	conditions = ""
	
	if filters.get("supplier"):
		conditions += " AND grn.supplier = %(supplier)s"
	
	if filters.get("from_date"):
		conditions += " AND grn.posting_date >= %(from_date)s"
	
	if filters.get("to_date"):
		conditions += " AND grn.posting_date <= %(to_date)s"
	
	if filters.get("supplier_invoicedc_no"):
		conditions += " AND grn.supplier_invoicedc_no = %(supplier_invoicedc_no)s"
	
	if filters.get("aging_days"):
		conditions += " AND DATEDIFF(CURDATE(), grn.posting_date) >= %(aging_days)s"
	
	return conditions