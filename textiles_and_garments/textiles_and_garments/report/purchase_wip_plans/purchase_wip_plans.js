

// Copyright (c) 2024, Aravind and contributors
// For license information,please see license.txt

// frappe.query_reports["Purchase WIP Plans"] = {
// 	"filters": [
// 		{
// 			fieldname: "plan_items",
// 			label: __("Plan Items"),
// 			fieldtype: "Link",
// 			options: "Plan Items",
// 			width: "380",
// 		},
// 		// {
// 		// 	fieldname: "plansNo",
// 		// 	label: __("Plans"),
// 		// 	fieldtype: "Link",
// 		// 	options: "Plans",
// 		// 	width: "380",
// 		// },
// 		{
// 			fieldname: "item_code",
// 			label: __("Item"),
// 			fieldtype: "Link",
// 			options: "Item",
// 			width: "280",
// 		},
// 		{
// 			fieldname: "docstatus",
// 			label: __("Docstatus"),
// 			fieldtype: "Select",
// 			width: "280",
// 			options: [
// 				{ "label": "Draft", "value": "0" },
// 				{ "label": "Submitted", "value": "1" },
// 				{ "label": "Cancelled", "value": "2" }
// 			],
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
// 			fieldname: "commercial_name",
// 			label: __("Commercial Name"),
// 			fieldtype: "Data",
// 			width: "200",
// 		},
// 		{
// 			fieldname: "color",
// 			label: __("Color"),
// 			fieldtype: "Data",
// 			width: "200",
// 		}
// 	]
// };
frappe.query_reports["Purchase WIP Plans"] = {
    "filters": [
        {
            "fieldname": "plan_items",
            "label": __("Plan Items"),
            "fieldtype": "Link",
            "options": "Plan Items",
            "width": "380"
        },
        {
            "fieldname": "item_code",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "width": "280"
        },
        // {
        //     "fieldname": "docstatus",
        //     "label": __("Document Status"),
        //     "fieldtype": "Select",
        //     "width": "280",
        //     "options": [
        //         { "label": __("Draft"), "value": "0" },
        //         { "label": __("Submitted"), "value": "1" },
        //         { "label": __("Cancelled"), "value": "2" }
        //     ],
        //     "default": "1"  // Default to Submitted documents
        // },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "width": "80",
            "reqd": 1,
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -7)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "width": "80",
            "reqd": 1,
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "commercial_name",
            "label": __("Commercial Name"),
            "fieldtype": "Data",
            "width": "200"
        },
        {
            "fieldname": "color",
            "label": __("Color"),
            "fieldtype": "Data",
            "width": "200"
        }
    ]
};







