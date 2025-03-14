// Copyright (c) 2024, Aravind and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Order Qty Vs Delivered Qty"] = {
	"filters": [
		{
			fieldname: "item_code",
			label: __("Item"),
			fieldtype: "Link",
			width: "280",
			options: "Item",
		},
		{
			fieldname: "commercial_name",
			label: __("Commercial name"),
			fieldtype: "Data",
			width: "280",
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
		{
			fieldname: "custom_item_status",
			label: __("Item Status"),
			fieldtype: "Select",
			options: ["Completed", "Cancelled", "Partially Delivered and Need to Deliver"],
			width: "80",
			
		},
		{
			fieldname: "status",
			label: __("Document Status"),
			fieldtype: "Select",
			options: ["Completed", "Cancelled", "Partially Delivered and Need to Deliver"],
			width: "80",
			
		},

	]
};




