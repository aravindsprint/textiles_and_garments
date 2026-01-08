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
			"fieldname": "purchase_order",
			"label": _("Purchase Order"),
			"fieldtype": "Link",
			"options": "Purchase Order",
			"width": 150
		},
		{
			"fieldname": "transaction_date",
			"label": _("PO Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "supplier",
			"label": _("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 150
		},
		{
			"fieldname": "supplier_name",
			"label": _("Supplier Name"),
			"fieldtype": "Data",
			"width": 180
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		},
		{
			"fieldname": "item_name",
			"label": _("Item Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "qty",
			"label": _("Ordered Qty"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "stock_uom",
			"label": _("UOM"),
			"fieldtype": "Link",
			"options": "UOM",
			"width": 80
		},
		{
			"fieldname": "received_qty",
			"label": _("Received Qty"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "pending_qty",
			"label": _("Pending Qty"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "per_received",
			"label": _("% Received"),
			"fieldtype": "Percent",
			"width": 100
		},
		{
			"fieldname": "schedule_date",
			"label": _("Schedule Date"),
			"fieldtype": "Date",
			"width": 110
		},
		{
			"fieldname": "shipping_address",
			"label": _("Shipping Address"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "material_request",
			"label": _("Material Request"),
			"fieldtype": "Link",
			"options": "Material Request",
			"width": 150
		},
		{
			"fieldname": "aging_days",
			"label": _("Aging (Days)"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "company",
			"label": _("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"width": 200
		}
	]

def get_data(filters):
	"""
	Fetch Purchase Order items with conditions:
	- Document Status = Submitted
	- Item Code LIKE '%yr%' (yarn items)
	- % Received NOT EQUALS 100
	- % Received LESS THAN 95
	- Shipping Address LIKE '%NAP%'
	"""
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(f"""
		SELECT 
			po.name as purchase_order,
			po.transaction_date,
			po.supplier,
			po.supplier_name,
			po.status,
			po.company,
			po.shipping_address as shipping_address,
			poi.item_code,
			poi.item_name,
			poi.qty,
			poi.stock_uom,
			poi.received_qty,
			(poi.qty - poi.received_qty) as pending_qty,
			ROUND((poi.received_qty / poi.qty * 100), 2) as per_received,
			poi.schedule_date,
			poi.material_request,
			DATEDIFF(CURDATE(), po.transaction_date) as aging_days
		FROM 
			`tabPurchase Order` po
		INNER JOIN 
			`tabPurchase Order Item` poi ON poi.parent = po.name
		WHERE 
			po.docstatus = 1
			AND poi.item_code LIKE '%%GKF%%'
			AND ROUND((poi.received_qty / poi.qty * 100), 2) != 100.00
			AND ROUND((poi.received_qty / poi.qty * 100), 2) < 95.00
			AND po.shipping_address LIKE '%%NAP%%'
			{conditions}
		ORDER BY 
			po.transaction_date DESC, po.name, poi.idx
	""", filters, as_dict=1)
	
	return data

def get_conditions(filters):
	"""Build additional filter conditions"""
	conditions = ""
	
	if filters.get("company"):
		conditions += " AND po.company = %(company)s"
	
	if filters.get("supplier"):
		conditions += " AND po.supplier = %(supplier)s"
	
	if filters.get("from_date"):
		conditions += " AND po.transaction_date >= %(from_date)s"
	
	if filters.get("to_date"):
		conditions += " AND po.transaction_date <= %(to_date)s"
	
	if filters.get("item_code"):
		conditions += " AND poi.item_code = %(item_code)s"
	
	if filters.get("material_request"):
		conditions += " AND poi.material_request = %(material_request)s"
	
	return conditions