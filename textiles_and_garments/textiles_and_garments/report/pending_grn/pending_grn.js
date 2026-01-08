// Copyright (c) 2026, Aravind and contributors
// For license information, please see license.txt

frappe.query_reports["Pending GRN"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 0
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 0
		},
		{
			"fieldname": "supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"reqd": 0
		},
		{
			"fieldname": "supplier_invoicedc_no",
			"label": __("Supplier DC No"),
			"fieldtype": "Data",
			"reqd": 0
		},
		{
			"fieldname": "aging_days",
			"label": __("Minimum Aging Days"),
			"fieldtype": "Int",
			"reqd": 0
		}
	]
};