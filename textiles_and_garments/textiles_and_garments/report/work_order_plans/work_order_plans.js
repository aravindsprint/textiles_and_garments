// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt


frappe.query_reports["Work Order Plans"] = {
	"filters": [
		{
			fieldname: "item_code",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
			width: "280",
		},
		{
			fieldname: "work_order",
			label: __("Work Order"),
			fieldtype: "Link",
			options: "Work Order",
			width: "280",
		},
		{
			fieldname: "plansNo",
			label: __("Plans"),
			fieldtype: "Link",
			options: "Plans",
			width: "380",
		},
		{
			fieldname: "custom_plan_items",
			label: __("Plan Items"),
			fieldtype: "Link",
			options: "Plan Items",
			width: "380",
		},
		{
			fieldname: "parent_plansNo",
			label: __("Parent Plans"),
			fieldtype: "Link",
			options: "Plans",
			width: "380",
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
		{
			fieldname: "commercial_name",
			label: __("Commercial Name"),
			fieldtype: "Data",
			width: "200",
		},
		{
			fieldname: "color",
			label: __("Color"),
			fieldtype: "Data",
			width: "200",
		}
	]
};



