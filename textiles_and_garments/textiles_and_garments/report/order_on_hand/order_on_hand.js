// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt


frappe.query_reports["Order On Hand"] = {
	"filters": [
		{
			fieldname: "sales_person",
			label: __("Sales Person"),
			fieldtype: "Link",
			width: "280",
			options: "Sales Person",
			get_query: function() {
				return {
					filters: {
						"is_group": 0
					}
				};
			}
		},
		{
			fieldname: "parent_sales_person",
			label: __("Sales Team"),
			fieldtype: "Link",
			width: "280",
			options: "Sales Person",
			get_query: function() {
				return {
					filters: {
						"is_group": 1
					}
				};
			}
		},
		// {
		// 	fieldname: "series",
		// 	label: __("Series"),
		// 	fieldtype: "Data",
		// 	options: ["Not Delivered", "Fully Delivered", "Partly Delivered", "Not Applicable"],
		// 	width: "80",
			
		// },
		// {
		// 	fieldname: "series",
		// 	label: __("Series"),
		// 	fieldtype: "MultiSelectList",
		// 	width: "80",
		// 	get_data: function() {
		// 		return [
		// 			{ value: "SAL-ORD-.YYYY.-", description: __("") },
		// 			{ value: "SAL-ORDRET-.YYYY.-", description: __("") },
		// 		];
		// 	}
		// },
		{
			fieldname: "series",
			label: __("Series"),
			fieldtype: "MultiSelectList",
			width: "80",
			get_data: function() {
				return [
					{ value: "SURATSO/25/.#", description: __("") },
					{ value: "PILAYA/25/.#", description: __("") },
					{ value: "PDJO/25/.#", description: __("") },
					{ value: "PTSI/25/.#", description: __("") },
					{ value: "PTMTO/25/.#", description: __("") },
					{ value: "PSMTO/25/.#", description: __("") },
					{ value: "PHSO/25/.#", description: __("") },
					{ value: "SOHO/25/.#", description: __("") },
					{ value: "SOJV/25/.#", description: __("") },
					{ value: "PISE/25/.#", description: __("") },
					{ value: "PFSO/25/.#", description: __("") },
					{ value: "UNISO25/25/.#", description: __("") },
					{ value: "SP25/25/.#", description: __("") },
				];
			}
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			width: "80",
			options: "Customer",
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
		// {
		// 	fieldname: "delivery_status",
		// 	label: __("Delivery Status"),
		// 	fieldtype: "Select",
		// 	options: ["","Not Delivered", "Fully Delivered", "Partly Delivered", "Not Applicable"],
		// 	width: "80",
			
		// },
		{
			fieldname: "status",
			label: __("Docstatus"),
			fieldtype: "MultiSelectList",
			width: "80",
			get_data: function() {
				return [
					{ value: "Draft", description: __("") },
					{ value: "To Deliver and Bill", description: __("") },
					{ value: "To Bill", description: __("") },
					{ value: "To Deliver", description: __("") },
					{ value: "Completed", description: __("") },
					{ value: "Cancelled", description: __("") },
					{ value: "Closed", description: __("") }
				];
			}
		},

	]
};




