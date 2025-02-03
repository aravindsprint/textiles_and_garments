// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt


frappe.query_reports["Jobwork Ageing in Dyeing Unit"] = {
	"filters": [
		{
			fieldname: "stock_entry",
			label: __("Stock Entry"),
			fieldtype: "Link",
			width: "280",
			options: "Stock Entry",
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
		{
			fieldname: "wo_status",
			label: __("WO Status"),
			fieldtype: "Data",
			width: "280",
		},
		{
			fieldname: "si_status",
			label: __("SI Status"),
			fieldtype: "Data",
			width: "280",
		},

	]
};

