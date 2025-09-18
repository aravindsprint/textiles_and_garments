// Copyright (c) 2024, Aravind and contributors
// For license information, please see license.txt

// frappe.query_reports["Sales Order Qty Vs Delivered Qty"] = {
// 	"filters": [
// 		{
// 			fieldname: "item_code",
// 			label: __("Item"),
// 			fieldtype: "Link",
// 			width: "280",
// 			options: "Item",
// 		},
// 		{
// 			fieldname: "commercial_name",
// 			label: __("Commercial name"),
// 			fieldtype: "Data",
// 			width: "280",
// 		},
// 		{
// 			fieldname: "from_date",
// 			label: __("From This Date"),
// 			fieldtype: "Date",
// 			width: "80",
// 			reqd: 1,
// 			default: frappe.datetime.add_days(frappe.datetime.get_today(), -7),
// 		},
// 		{
// 			fieldname: "to_date",
// 			label: __("To This Date"),
// 			fieldtype: "Date",
// 			width: "80",
// 			reqd: 1,
// 			default: frappe.datetime.get_today(),
// 		},
// 		{
// 			fieldname: "custom_item_status",
// 			label: __("Item Status"),
// 			fieldtype: "Select",
// 			options: ["Not Started", "Completed", "Cancelled", "Partially Delivered and Need to Deliver"],
// 			width: "80",
			
// 		},
// 		{
// 			fieldname: "delivery_status",
// 			label: __("Delivery Status"),
// 			fieldtype: "Select",
// 			options: ["Not Delivered", "Fully Delivered", "Partly Delivered", "Not Applicable"],
// 			width: "80",
			
// 		},

// 	]
// };


// frappe.query_reports["Sales Order Qty Vs Delivered Qty"] = {
// 	"filters": [
// 		{
// 			fieldname: "item_code",
// 			label: __("Item"),
// 			fieldtype: "Link",
// 			width: "280",
// 			options: "Item",
// 		},
// 		{
// 			fieldname: "commercial_name",
// 			label: __("Commercial name"),
// 			fieldtype: "Data",
// 			width: "280",
// 		},
// 		{
// 			fieldname: "from_date",
// 			label: __("From This Date"),
// 			fieldtype: "Date",
// 			width: "80",
// 			reqd: 1,
// 			default: frappe.datetime.add_days(frappe.datetime.get_today(), -7),
// 		},
// 		{
// 			fieldname: "to_date",
// 			label: __("To This Date"),
// 			fieldtype: "Date",
// 			width: "80",
// 			reqd: 1,
// 			default: frappe.datetime.get_today(),
// 		},
// 		{
// 			fieldname: "custom_item_status",
// 			label: __("Item Status"),
// 			fieldtype: "MultiSelect",
// 			options: ["Not Started", "Completed", "Cancelled", "Partially Delivered and Need to Deliver"],
// 			width: "80",
			
// 		},
// 		{
// 			fieldname: "delivery_status",
// 			label: __("Delivery Status"),
// 			fieldtype: "Select",
// 			options: ["Not Delivered", "Fully Delivered", "Partly Delivered", "Not Applicable"],
// 			width: "80",
			
// 		},

// 	]
// };

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
			fieldtype: "MultiSelectList",
			width: "80",
			get_data: function() {
				// Return the static options
				// return [
				// 	{ value: "Not Started", description: __("Not Started") },
				// 	{ value: "Completed", description: __("Completed") },
				// 	{ value: "Cancelled", description: __("Cancelled") },
				// 	{ value: "Partially Delivered and Need to Deliver", description: __("Partially Delivered and Need to Deliver") }
				// ];
				return [
					{ value: "Not Started", description: __("") },
					{ value: "Completed", description: __("") },
					{ value: "Cancelled", description: __("") },
					{ value: "Partially Delivered and Need to Deliver", description: __("") }
				];
			}
		},
		{
			fieldname: "delivery_status",
			label: __("Delivery Status"),
			fieldtype: "Select",
			options: ["Not Delivered", "Fully Delivered", "Partly Delivered", "Not Applicable"],
			width: "80",
		}
	]
};