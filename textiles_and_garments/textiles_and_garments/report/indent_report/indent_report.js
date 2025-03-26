// Copyright (c) 2024, Aravind and contributors
// For license information, please see license.txt

frappe.query_reports["Indent Report"] = {
	"filters": [
		{
			fieldname: "finished_item_code",
			label: __("Item"),
			fieldtype: "Link",
			width: "280",
			options: "Item",
		},
		{
			fieldname: "docstatus",
			label: __("Docstatus"),
			fieldtype: "Select",
			width: "280",
			options: ["0","1","2"],
		},
		// {
		// 	fieldname: "custom_item_status",
		// 	label: __("Item Status"),
		// 	fieldtype: "Select",
		// 	options: ["Not Started", "Completed", "Cancelled", "Partially Delivered and Need to Deliver"],
		// 	width: "80",
			
		// },
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





