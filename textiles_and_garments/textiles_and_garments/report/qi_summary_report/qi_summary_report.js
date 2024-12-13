// Copyright (c) 2024, Aravind and contributors
// For license information, please see license.txt

frappe.query_reports["QI Summary Report"] = {
	"filters": [
		{
			fieldname: "item_code",
			label: __("Item"),
			fieldtype: "Link",
			width: "280",
			options: "Item",
		},
		{
			fieldname: "posting_date",
			label: __("From This Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.add_days(frappe.datetime.get_today(), -7),
		},
		{
			fieldname: "posting_date",
			label: __("To This Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.get_today(),
		},

	]
};

