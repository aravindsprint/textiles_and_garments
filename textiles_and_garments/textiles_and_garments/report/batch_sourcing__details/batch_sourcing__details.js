// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

frappe.query_reports["Batch Sourcing  Details"] = {
    "filters": [
        {
            fieldname: "batch_no",
            label: __("Batch"),
            fieldtype: "Link",
            options: "Batch",
            reqd: 1,
            width: "280",
            get_query: function() {
                return {
                    filters: {
                        "disabled": 0
                    }
                }
            }
        },
        {
            fieldname: "supplier",
            label: __("Supplier"),
            fieldtype: "Link",
            options: "Supplier",
            reqd: 0,
            width: "280",
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            width: "80",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -3),
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            width: "80",
            default: frappe.datetime.get_today(),
        },
        {
            fieldname: "show_all_levels",
            label: __("Show All Levels"),
            fieldtype: "Check",
            default: 1,
            description: __("Show complete hierarchy of batches")
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (column.fieldname == "link" && data.link) {
            value = data.link;
        }
        
        if (column.fieldname == "batch" && data.s_no == 1) {
            value = `<b>${value}</b>`;
        }
        
        return value;
    },

    "tree": true,
    "name_field": "batch",
    "parent_field": "parent_batch",
    "initial_depth": 3,
    "get_parent_row": function(row) {
        // This helps in showing the hierarchy in tree view
        if (row.parent_batch) {
            return { batch: row.parent_batch };
        }
        return null;
    }
};


// frappe.query_reports["Batch Sourcing  Details"] = {
// 	"filters": [
// 		{
// 			fieldname: "plans_item_code",
// 			label: __("Item"),
// 			fieldtype: "Link",
// 			options: "Item",
// 			width: "380",
// 		},
// 		{
// 			fieldname: "warehouse",
// 			label: __("Warehouse"),
// 			fieldtype: "Link",
// 			options: "Warehouse",
// 			width: "250",
// 		},
// 		{
// 			fieldname: "batch_no",
// 			label: __("Batch"),
// 			fieldtype: "Link",
// 			options: "Batch",
// 			width: "380",
// 		},
// 		{
// 			fieldname: "plansNo",
// 			label: __("Plans"),
// 			fieldtype: "Link",
// 			options: "Plans",
// 			width: "380",
// 		},
// 		{
// 			fieldname: "plan_items",
// 			label: __("Plan Items"),
// 			fieldtype: "Link",
// 			options: "Plan Items",
// 			width: "380",
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
// 			// default: frappe.datetime.add_days(frappe.datetime.get_today(), -7),
// 		},
// 		{
// 			fieldname: "to_date",
// 			label: __("To This Date"),
// 			fieldtype: "Date",
// 			width: "80",
// 			reqd: 1,
// 			// default: frappe.datetime.get_today(),
// 		},
// 		// {
// 		// 	fieldname: "commercial_name",
// 		// 	label: __("Commercial Name"),
// 		// 	fieldtype: "Data",
// 		// 	width: "200",
// 		// },
// 		// {
// 		// 	fieldname: "color",
// 		// 	label: __("Color"),
// 		// 	fieldtype: "Data",
// 		// 	width: "200",
// 		// }

// 	]
// };






