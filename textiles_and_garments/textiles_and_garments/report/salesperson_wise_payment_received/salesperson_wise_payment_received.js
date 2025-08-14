// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt


frappe.query_reports["SalesPerson Wise Payment Received"] = {
	"filters": [
		{
			fieldname: "payment_entry",
			label: __("Payment Entry"),
			fieldtype: "Link",
			options: "Payment Entry",
			width: "280",
		},
		{
			fieldname: "sales_person",
			label: __("Sales Person"),
			fieldtype: "Link",
			options: "Sales Person",
			width: "280",
		},
		{
			fieldname: "docstatus",
			label: __("Docstatus"),
			fieldtype: "Select",
			width: "280",
			options: [
				{ "label": "Draft", "value": "0" },
				{ "label": "Submitted", "value": "1" },
				{ "label": "Cancelled", "value": "2" }
			],
		},
		{
			fieldname: "from_date",
			label: __("From This Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.add_days(frappe.datetime.get_today(), -7),
		},
		{
			fieldname: "to_date",
			label: __("To This Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.get_today(),
		},
	]
};
		